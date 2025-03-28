import hashlib
from pickle import FALSE
import sys
import socket
import heapq
import time
import uuid
import json
import random
import traceback

#return a block request by any peers in the network
def get_block(data,addr):
    #print(f"\nGET BLOCK: {data['height']}")
    try:
        block_type = data["type"]
        height = data["height"]
    except KeyError as e:
        print(f"Invalid PROTOCOL structure: Missing key {e} \n{data}")
        return
        
    block_msg = {
        "type": "GET_BLOCK_REPLY",
        "height": None,
        "minedBy": None,
        "nonce": None,
        "messages": None,
        "hash": None,
        "timestamp": None
   }

    #if block exists in current chain 
    if data["height"] < len(block_list):
        curr_idx =  height
         # Ensure the block at curr_idx is not None
        if block_list[curr_idx] is not None:
            # The block exists, so fill in the details
            block_msg["height"] = block_list[curr_idx]["height"]
            block_msg["minedBy"] = block_list[curr_idx]["minedBy"]
            block_msg["nonce"] = block_list[curr_idx]["nonce"]
            block_msg["messages"] = block_list[curr_idx]["messages"]
            block_msg["hash"] = block_list[curr_idx]["hash"]
            block_msg["timestamp"] = block_list[curr_idx]["timestamp"]
        else:
            print(f"Block at index {curr_idx} is None. Requesting it from peers.")
            # Handle the case where the block is missing (e.g., request from peers)
            # You can request the block from peers here if necessary.
            return

    mySocket.sendto(json.dumps(block_msg).encode(),addr)

def build_chain(block):
    # Ensure the block's height is valid
    if block["height"] < 0:
        print(f"Invalid block height: {block['height']}")
        return False

    #Expand the block_list if the height is beyond the current length
    while len(block_list) <= block["height"]:
        block_list.append(None)  # Placeholder for uninitialized blocks

    # Check if the block at the given height is already filled
    if block_list[block["height"]] is not None:
        return False

    block_hash = block["hash"]

    # Only add the block if it has sufficient difficulty.
    if block_hash[-1 * DIFFICULTY:] == '0' * DIFFICULTY:
        # Add the block to its specific height
        new_block = {
            "height": block["height"],
            "minedBy": block["minedBy"],
            "nonce": block["nonce"],
            "messages": block["messages"],
            "hash": block["hash"],
            "timestamp": block["timestamp"],
        }
        block_list[block["height"]] = new_block
        #print(f"\nBLOCK WITH Height {block['height']}, HASH: {block['hash']} ADDED")
        #print(f"\nBlock added:{new_block['height']}")
        return True
    else:
        print(f"Invalid block HASH: {block['hash']}")
        return False


def add_block(block):
    print(f"\n######################################\nANNOUNCE -> ADD_BLOCK:\n{block}\n")
    # Validatig the block
    try:
        block_type = block["type"]
        height = block["height"]
        minedBy = block["minedBy"]
        nonce = block["nonce"]
        messages = block["messages"]
        block_hash = block["hash"]
        timestamp = block["timestamp"]
    except KeyError as e:
        print(f"Invalid PROTOCOL structure: Missing key {e} \n{data}")
        return
    
    new_block = {
        "height": None,
        "minedBy": None,
        "nonce": None,
        "messages": [],
        "hash": None,
        "timestamp": None,
    }

    # Ensure the block height matches the expected next block in the chain
    if block["height"] == len(block_list):
        new_block["height"] = block["height"]
        new_block["minedBy"] = block["minedBy"]
        new_block["timestamp"] = block["timestamp"]

        # Validate nonce
        if len(block["nonce"]) <= 40:
            new_block["nonce"] = block["nonce"]
            print(f"Length of Nonce is VALID: {new_block['nonce']}")
            # Validate messages
            if len(block["messages"]) <= 10:
                for m in block["messages"]:
                    if len(m) <= 20:
                        new_block["messages"].append(m)
                        print(f"Messages are VALID")

                # Validate hash
                hashBase = hashlib.sha256()

                # Get the most recent hash or use an empty string for the genesis block
                if len(block_list) > 0:
                    lastHash = block_list[-1]["hash"]
                    hashBase.update(lastHash.encode())
                else:
                    lastHash = None  # Genesis block

                # Add miner's name
                hashBase.update(block["minedBy"].encode())

                # Add messages in order
                for m in block["messages"]:
                    hashBase.update(m.encode())

                # Add the time (convert to bytes)
                hashBase.update(int(block["timestamp"]).to_bytes(8, 'big'))

                # Add the nonce
                hashBase.update(block["nonce"].encode())

                # Calculate the hash
                calculated_hash = hashBase.hexdigest()
                print(f"Calculated HASH: {calculated_hash}\nProvided HASH: {block['hash']}")

                # Ensure difficulty is met and hash matches
                if calculated_hash[-1 * DIFFICULTY:] == '0' * DIFFICULTY and calculated_hash == block["hash"]:
                    new_block["hash"] = block["hash"]
                    block_list.append(new_block)
                    print(f"BLOCK ADDED after ANNOUNCE: {new_block['height']} \n######################################\n")
                else:
                    print("HASH DIFFICULTY NOT MET! \n######################################\n")
            else:
                print("MESSAGES ARE NOT VALID \n######################################\n")
        else:
            print("NONCE NOT VALID \n######################################\n")
    else:
        print("Not the top block \n######################################\n")

# When a GOSSIP reply is received from peers, add them to the peers list.
def peer_gossip(data):
    global last_consensus_time
    global consensus_flag
    try:
        msg_type = data["type"]
        msg_host = data["host"]
        msg_port = data["port"]
        msg_port = data["port"]
        if msg_port not in range(0,65535):
            print("PORT OVERFLOW: Port should be btw 0-65535")
            return
        msg_name = data["name"]
    except KeyError as e:
        print(f"Invalid GOSSIP_REPLY structure: Missing key {e}\n{data}")
        return
        # Validatig the data
    #print_peers()
    #print(f"\nGOSSIP(from)-> NAME:{data['name']}")
    curr_peer = (msg_host, msg_port)

    # If the peer is not already in the list, add it.
    if curr_peer not in peers:
        peers.append(curr_peer)
        last_GOSSIP_time_peers.append(-1)  # Initialize last GOSSIP time for this peer.
        #print(f"GOSSIP -> Added new peer: {curr_peer}")

    # First time running consensus: If exactly 3 peers are present and no consensus has been run yet.
    #print(f"\n\n\n LAST CONSENSUS TIME: {last_consensus_time}\n\n\n")
    if len(peers) >= 7 and last_consensus_time == 0 and not consensus_flag:
        last_consensus_time = time.time()
        print(f"\n\nLast_Consensus_time: {last_consensus_time}\n\n")
        print(f"######################################\nTriggering consensus with the first {len(peers)} peers.\n######################################")
        consensus_flag = True
        consensus()
    elif len(peers) < 7 and last_consensus_time == 0 and not consensus_flag:
        print("Peer count dropped below 7. Consensus stability might be affected.")
        print(f"\n\nLast_Consensus_time: {last_consensus_time}\n\n")
        consensus_flag = True
        print(f"######################################\nTriggering consensus with the first {len(peers)} peers.\n######################################")
        consensus()

# When receiving a GOSSIP message, send a GOSSIP-REPLY back to the sender.
def send_gossip_reply(data):
    # Validatig the data
    try:
        msg_type = data["type"]
        msg_host = data["host"]
        msg_port = data["port"]
        if msg_port not in range(0,65535):
            print("PORT OVERFLOW: Port should be btw 0-65535")
            return
        # msg_id = data["id"]
        msg_name = data["name"]
    except KeyError as e:
        print(f"Invalid GOSSIP structure: Missing key {e} \n{data}")
        return
    gossip_reply = {
        "type": "GOSSIP_REPLY",
        "host": myhost,
        "port": myPort,
        "name": name
    }
    curr_peer = (data["host"], data["port"])

    # If the peer is not already in the list, add it.
    if curr_peer not in peers:
        peers.append(curr_peer)
        last_GOSSIP_time_peers.append(-1)  # Initialize last GOSSIP time for this peer.
        #print(f"GOSSIP_REPLY-> Added new peer: {curr_peer}")

    # Send the GOSSIP-REPLY message to the peer.
    mySocket.sendto(json.dumps(gossip_reply).encode(), curr_peer)

    # Update the last GOSSIP time for the peer.
    for i in range(len(peers)):
        if peers[i] == curr_peer:
            last_GOSSIP_time_peers[i] = time.time()
            #print(f"Updated last GOSSIP time for peer {curr_peer}")
            break


# sends the stats 
def getStats(addr):
    msgReply = {
        "type": "STATS_REPLY",
        "height": -1,
        "hash" : None
    }

    if len(block_list) > 0:
        msgReply["height"] = len(block_list)
        msgReply["hash"] = block_list[-1]["hash"]

    #print(f"STAT-REPLY: {msgReply} to {addr}")
    mySocket.sendto(json.dumps(msgReply).encode(),addr)


def consensus():
    print("\n##########################################\nIN CONSENSUS\n")
    global retry_count_validation
    global block_list
    global most_agreed_peers
    print(f"Sending STATS to all known {len(peers)} peers!")
    stat_req = {"type": "STATS"}
    stat_req = json.dumps(stat_req).encode()

    # Broadcast stats request to all peers
    for curr_peer in peers:
        replied = False
        for attempt in range(5):  # Retry up to 3 times
            try:
                mySocket.sendto(stat_req, curr_peer)
                mySocket.settimeout(100)  # Timeout for response
                data, addr = mySocket.recvfrom(1024)
                if not data:
                    print(f"Received empty data from {addr}. Skipping processing.")
                    continue
                data_json = json.loads(data.decode())

                if data_json["type"] == "STATS_REPLY":
                    height = data_json.get("height")
                    block_hash = data_json.get("hash")
                    if height is not None and height > 0 and block_hash.endswith("0" * DIFFICULTY) and block_hash is not None:
                        #stats_replies.append([height, block_hash, curr_peer])
                        stats_replies.add((height, block_hash, curr_peer))
                        
                        replied = True
                        break
                elif data_json["type"] == "GOSSIP_REPLY":
                    peer_gossip(data_json)
                elif data_json["type"] == "GOSSIP":
                    send_gossip_reply(data_json)
            except socket.timeout:
                print(f"Timeout while waiting for peer {curr_peer} response. Attempt {attempt + 1}/3")
            except Exception as e:
                print(f"Error during stats request from {curr_peer}: {e}")

    if not stats_replies:
        print("No peers responded with valid stats.")
        return
    
    # Determine the most agreed-upon chain height and maintain peers for each height
    height_peers = {}
    for height, _, peer in stats_replies:
        if height not in height_peers:
            height_peers[height] = []
        height_peers[height].append(peer)

    #print(f"\nHeight to peers mapping: \n{height_peers}\n")
        # Create a max heap based on chain height and peer count
    # heap = [(-height, len(peers), height, peers) for height, peers in height_peers.items()]
    # heapq.heapify(heap)
    # print(f"\n\nHEAP:\n{heap}\n\n")
        # Print the height and how many peers are backing it
    # print("\nPeers backing each height:")
    # for height, x in height_peers.items():
    #     print(f"Height {height}: {len(x)} peers")

    # Filter out invalid heights (None or <= 0)
    # valid_heights = {height: x for height, x in height_peers.items() if height is not None and height > 0}
    # print(f"\nValid heights and their peers: \n{valid_heights}\n")

    # Check if there are valid heights to consider
    if not height_peers:
        print("No valid chain heights found (all heights <= 0). Consensus cannot proceed.")
        most_agreed_height = 0  # Default value in case of no valid heights
    else:
        # Find the most agreed-upon height manually
        highest_count = -1
        most_agreed_height = None
        most_agreed_peers = []
        for height, x in height_peers.items():
            peer_count = len(x)
            # Prefer the height with the highest peer count; break ties with the greater height value
            if peer_count > highest_count or (peer_count == highest_count and (most_agreed_height is None or height > most_agreed_height)):
                most_agreed_height = height
                highest_count = peer_count
                most_agreed_peers = x

    print(f"\n\nMost agreed height: {most_agreed_height}\n\n")
    print(f"\n\nMost Agreed Peers: {most_agreed_peers}")

    batch_size = 50  # Number of blocks to request at a time
    current_peer_index = 0

    good_peers = [
        peer for peer in most_agreed_peers 
        if peer != (myhost, myPort) and peer not in bad_actors
        ]
    
    while len(block_list) < most_agreed_height:
        start_height = len(block_list)
        end_height = min(start_height + batch_size, most_agreed_height)
        
        # Ensure good_peers is not empty
        if good_peers:
            # Select peer in a round-robin manner from filtered peers
            current_peer_index = (current_peer_index + 1) % len(good_peers)
            curr_peer = good_peers[current_peer_index]

            # # Update `current_peer_index` in a round-robin manner
            # current_peer_index = (current_peer_index + 1) % len(good_peers)
        else:
            print("No good peers available for consensus.")
            break

        print(f"Requesting blocks {start_height}-{end_height - 1} from peer {curr_peer}")

        for height in range(start_height, end_height):
            block_req = {
                "type": "GET_BLOCK",
                "height": height
            }
            retry_count = 0
            max_retries = 10
            replied = False

            while retry_count < max_retries and not replied:
                retry_count += 1
                mySocket.sendto(json.dumps(block_req).encode(), curr_peer)
                mySocket.settimeout(10)  # Timeout for response
                try:
                    data, addr = mySocket.recvfrom(1024)
                    if not data:
                        print(f"Received empty data from {addr}. Skipping processing.")
                        continue
                    # Process the response only if it matches the expected format
                    data_json = json.loads(data.decode())
                    # Validate block hash difficulty
                    if data_json["type"] == "GET_BLOCK_REPLY":
                        block_reply_height = data_json["height"]
                        block_reply_hash = data_json["hash"]
                        
                        # Validate block hash difficulty
                        if block_reply_hash and block_reply_hash[-1 * DIFFICULTY:] == '0' * DIFFICULTY:
                            build_chain(data_json)
                            replied = True

                        else:
                            break

                    elif data_json["type"] == "GOSSIP_REPLY":
                        peer_gossip(data_json)

                    elif data_json["type"] == "GOSSIP":
                        send_gossip_reply(data_json)

                except socket.timeout:
                    print(f"Timeout for block {height} from peer {curr_peer}. Retrying...")
                except Exception as e:
                    print(f"Error requesting block {height} from peer {curr_peer} in CONSENSUS: {e}")
            if not replied:
                #print(f"Peer {curr_peer} failed to provide block {height}.")
                break  # Exit the inner loop to pick the next good peer                    
    
    # Validate the full chain
    while retry_count_validation < 10:
        if validate_chain(most_agreed_height):
            print("Chain synchronized and validated.\n##########################################\n")
            break
        else:
            retry_count_validation += 1
            print(f"Chain validation failed. Retrying consensus... Attempt {retry_count_validation}/10")
            block_list = []  # Reset the block list to start fresh
            stats_replies.clear() # Clears the set so it's empty for the next retry
            consensus()

    if retry_count_validation == 10:
        print("Consensus failed after 10 attempts.")
        print(f"LENGTH OF PEERS: {len(peers)}")
        #print(f"LENGTH OF GOOD PEERS: {len(good_peers)}")
        print(f"Length of My Block Chain: {len(block_list)}")
        # print(e)
        sys.exit(0)
    else:
        last_consensus_time = time.time()
        print(f"Consensus successful. Last_Consensus_time: {last_consensus_time}")


def validate_chain(height):
    global most_agreed_peers
    if len(block_list) != height:
        print("Whole chain not formed")
        return False

    # Start validation from the second block (index 1)
    for i in range(1, len(block_list)):
        curr_block = block_list[i]
        prev_block = block_list[i - 1]

        if curr_block is None or prev_block is None:
            print(f"Block {i} is missing. Requesting from good peers...")
            block_received = False

            if not most_agreed_peers:
                print("Most agreed peers list is empty. Cannot proceed with validation.")
                return False

            for peer in most_agreed_peers:
                try:
                    # Send a request to the peer for the missing block
                    block_req = {"type": "GET_BLOCK", "height": i}
                    mySocket.sendto(json.dumps(block_req).encode(), peer)

                    # Wait for the peer's response
                    mySocket.settimeout(10)  # 10-second timeout
                    data, addr = mySocket.recvfrom(1024)
                    if not data:
                        print(f"Received empty data from {addr}. Skipping processing.")
                        continue
                    data_json = json.loads(data.decode())

                    # Validate the received block and ensure it's the correct height
                    if data_json["type"] == "GET_BLOCK_REPLY" and data_json.get("height") == i:
                        print(f"Received block {i} from peer {peer}.")
                        
                        # Insert or replace the block at the correct index
                        if i < len(block_list):
                            block_list[i] = data_json
                        else:
                            block_list.append(data_json)

                        curr_block = data_json
                        prev_block = block_list[i - 1]  # Update the previous block reference
                        block_received = True
                        break
                except socket.timeout:
                    print(f"Timeout requesting block {i} from peer {peer}. Trying next peer...")
                except Exception as e:
                    print(f"Error requesting block {i} from peer {peer} while validating: {e}")

            if not block_received:
                print(f"Validation failed: Could not retrieve block {i}.")
                return False

        # Calculate the hash for the current block
        calculated_hash = calculate_block_hash(curr_block, prev_block)

        # Validate the hash
        if calculated_hash != curr_block["hash"]:
            print(f"Block {i} hash mismatch. Expected Hash: {curr_block['hash']}, Calculated Hash: {calculated_hash}")
            block_received = False

            # Attempt to retrieve the correct block from peers
            for peer in most_agreed_peers:
                try:
                    block_req = {"type": "GET_BLOCK", "height": i}
                    mySocket.sendto(json.dumps(block_req).encode(), peer)

                    # Wait for the peer's response
                    mySocket.settimeout(10)  # 10-second timeout
                    data, addr = mySocket.recvfrom(1024)
                    if not data:
                        print(f"Received empty data from {addr}. Skipping processing.")
                        continue
                    data_json = json.loads(data.decode())

                    # Validate the received block and ensure it's the correct height
                    if data_json["type"] == "GET_BLOCK_REPLY" and data_json.get("height") == i:
                        recalculated_hash = calculate_block_hash(data_json, prev_block)

                        # If the recalculated hash is valid, add the block to the list
                        if recalculated_hash == data_json["hash"]:
                            print(f"Correct block {i} received from peer {peer}. Replacing the block.")
                            if i < len(block_list):
                                block_list[i] = data_json
                            else:
                                block_list.append(data_json)

                            curr_block = data_json
                            prev_block = block_list[i - 1]  # Update the previous block reference
                            block_received = True
                            break
                        else:
                            print(f"Block {i} received from peer {peer} is invalid. Hash mismatch.")    
                except socket.timeout:
                    print(f"Timeout requesting block {i} from peer {peer}. Trying next peer...")
                except Exception as e:
                    print(f"Error requesting block {i} from peer {peer} while validating: {e}")

            if not block_received:
                print(f"Validation failed: Could not retrieve a valid block {i}.")
                return False

        # Difficulty check: last DIFFICULTY characters should be '0'
        if calculated_hash[-DIFFICULTY:] != '0' * DIFFICULTY:
            print(f"Block {i} validation failed. Difficulty condition not met.")
            return False

    print("\n##########################################\nAll blocks validated successfully.")
    return True

# Calculate the hash of a block using its components.
def calculate_block_hash(block, prev_block):
    try:
        hashBase = hashlib.sha256()
        # Include the previous block's hash
        hashBase.update(prev_block["hash"].encode())
        # Include the miner's name
        hashBase.update(block["minedBy"].encode())
        # Include messages in order
        for m in block["messages"]:
            hashBase.update(m.encode())
        # Include the timestamp
        hashBase.update(int(block["timestamp"]).to_bytes(8, 'big'))
        # Include the nonce
        hashBase.update(block["nonce"].encode())
        # Return the calculated hash
        return hashBase.hexdigest()
    except KeyError as e:
        print(f"Missing key during hash calculation: {e}")
        return None



#socket
name = f"SnakeJazz" 
myPort = 8699
robServer = "eagle.cs.umanitoba.ca"
robPort = 8999

try:
    mySocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    mySocket.bind(("", myPort))
    hostName = socket.gethostname()
    myhost = socket.gethostbyname(hostName)
    print("\n\n\n######################### Welcome to Sanskar's Blockchain Assignment #############################\n")
    print(f"\t\t IPADDR: {myhost}\n")
except Exception as e:
    print(f"Failed to bind to port {myPort}: {e}")
    sys.exit(1)

# default messages
# Gossip msg
gossip_msg = {
        "type" : "GOSSIP",
        "host" : myhost,
        "port" : myPort,
        "id"   : str(uuid.uuid1()),
        "name" : name
}

# Initialize lists and constants
last_GOSSIP_time = time.time()
last_consensus_time = 0
good_peers = []
most_agreed_peers = []
bad_actors = set()
retry_count_validation = 0
consensus_flag = False
peers = []
last_GOSSIP_time_peers = [] # saves the last time each peer sent GOSSIP 
block_list = []
stats_replies = set()
good_peers = []
DIFFICULTY = 8


#join network
mySocket.sendto(json.dumps(gossip_msg).encode(),(robServer,robPort))
mySocket.settimeout(10) # timeout for response 
while True:
    # Peer cleanup
    to_remove = []
    current_time = time.time()
    for curr in range(len(peers)):
        last_ping = last_GOSSIP_time_peers[curr]
        if current_time - last_ping > 60 and last_ping != -1:
            print(f"\n\t##########################################\nDIDN'T SEND GOSSIP FOR A MINUTE--BYEEEEEEE, {peers[curr]}\n\t##########################################\n")
            to_remove.append(curr)

    # Remove peers and their corresponding last ping times in reverse order
    for x in reversed(to_remove):
        peers.pop(x)
        last_GOSSIP_time_peers.pop(x)

    # run consensus after a 2 mins
    if current_time - last_consensus_time >= 120 and last_consensus_time != 0:
        print(f"\n##########################################\nCONSENSUS -> After Time Out!")
        stats_replies.clear() # Clears the set so it's empty for the next retry
        consensus()
        last_consensus_time = current_time  # Update the timestamp after consensus

    #GOSSIP every 30s
    if current_time - last_GOSSIP_time >= 30 :
        last_GOSSIP_time = current_time
        # Select 3 random peers
        if peers:
            selected_peers = random.sample(peers, min(3, len(peers)))
            for curr_peer in selected_peers:
                mySocket.sendto(json.dumps(gossip_msg).encode(), curr_peer)
        else:
            print("No peers available for gossip.")

    try:
        data,addr = mySocket.recvfrom(1024)
        if not data:
            print(f"Received empty data from {addr}. Skipping processing.")
            continue
        # Try to decode and process the data
        try:
            data_json = json.loads(data.decode())
             # Validate that the required key 'type' exists in the data
            if "type" not in data_json:
                print(f"Invalid data received from {addr}: Missing 'type' key. Data: {data}")
                continue  # Skip further processing for this message
            # Ensure the 'type' key exists in the data
            msg_type = data_json["type"]
            # Handle different message types
            if msg_type == "GOSSIP_REPLY":
                peer_gossip(data_json)
            elif msg_type == "GOSSIP":
                send_gossip_reply(data_json)
            elif msg_type == "GET_BLOCK":
                get_block(data_json, addr)
            elif msg_type == "STATS":
                getStats(addr)
            elif msg_type == "ANNOUNCE":
                add_block(data_json)
            elif msg_type == "CONSENSUS":
                print("\n\n\n\t######################### FORCED CONSENSUS ############################\t\n\n\n")
                stats_replies.clear() # Clears the set so it's empty for the next retry
                consensus()
            #else:
                #print(f"Unknown message type: {msg_type}")
        
        except json.JSONDecodeError:
            # Log error for malformed JSON
            print(f"Received malformed JSON data: {data}")

    except socket.timeout as t:
        print("timeout")
  
    except Exception as e:
        print(e)
        
        print("error at the end of main loop")
        traceback.print_exc()  # Prints the full traceback of the exception
        sys.exit(0)

    except KeyboardInterrupt as e:
        print("Shutting down gracefully...")
        mySocket.close()
        print(f"LENGTH OF PEERS: {len(peers)}")
        print(f"Length of BlockList: {len(block_list)}")
        sys.exit(0)