# def consensus():
#     print("\n\n\nIN CONSENSUS\n\n\n")
#     stat_req = { "type": "STATS" }
#     stat_req = json.dumps(stat_req).encode()
#     print("\nCONSENSUS->STAT_REQUESTED")

#     stats_replies = []
#     mySocket.settimeout(2)  # Timeout for response

#     # Request stats from peers
#     for curr_peer in peers:
#         replied = False
#         retry_count = 0
#         max_retries = 3
#         while not replied and retry_count < max_retries:
#             retry_count += 1
#             mySocket.sendto(stat_req, curr_peer)
#             try:
#                 data, addr = mySocket.recvfrom(1024)
#                 data_json = json.loads(data.decode())

#                 if data_json["type"] == "STATS_REPLY":
#                     stats_replies.append([data_json["height"], curr_peer])
#                     replied = True
                
#                 if data_json["type"] == "GOSSIP_REPLY":
#                     peer_gossip(data_json)

#                 if data_json["type"] == "GOSSIP":
#                     print(f"CONSENSUS->STAT_REQUESTED->ForLoop->WhileLoop->GOSSIP")
#                     send_gossip_reply(data_json)

#             except socket.timeout:
#                 print("Timeout while waiting for peer response.")
#             except Exception as e:
#                 print(f"Error during stats request: {e}")

#     # No valid responses from peers
#     if not stats_replies:
#         print("No peers responded with valid stats.")
#         return

#     # Manually count the occurrences of each height
#     height_dict = {}
#     for height, _ in stats_replies:
#         if height in height_dict:
#             height_dict[height] += 1
#         else:
#             height_dict[height] = 1

#     # Find the most common height (max height with highest occurrences)
#     most_common_height = max(height_dict, key=height_dict.get)
#     print(f"MOST COMMON HEIGHT: {most_common_height}")

#     # Find peers who have the most common height
#     common_height_peers = [peer for height, peer in stats_replies if height == most_common_height]
#     print(f"COMMON HEIGHT_PEERS: {common_height_peers}")


#     # Request blocks concurrently from peers with the most common height
#     while len(block_list) < most_common_height:
#         block_req = {
#             "type": "GET_BLOCK",
#             "height": len(block_list)
#         }

#         # Randomly shuffle peers to load balance the block request
#         random.shuffle(common_height_peers)

#         # Send requests to peers and collect ready sockets
#         ready_peers = []
#         for curr_peer in common_height_peers:
#             mySocket.sendto(json.dumps(block_req).encode(), curr_peer)
#             ready_peers.append(curr_peer)

#         # Use select to wait for responses
#         while ready_peers:
#             readable, _, _ = select.select([mySocket], [], [], 0)  # 2-second timeout for select

#             for s in readable:
#                 try:
#                     data, addr = s.recvfrom(1024)
#                     data_json = json.loads(data.decode())

#                     if data_json["type"] == "GET_BLOCK_REPLY":
#                         add_block(data_json)
#                         ready_peers.remove(addr)  # Successfully received block

#                     if data_json["type"] == "GOSSIP_REPLY":
#                         peer_gossip(data_json)

#                     if data_json["type"] == "GOSSIP":
#                         send_gossip_reply(data_json)

#                 except socket.timeout:
#                     print("Timeout while waiting for block response.")
#                 except Exception as e:
#                     print(f"Error during block request: {e}")

#     # Validate the full chain
#     if not validate_chain():
#         print("Chain validation failed. Attempting next longest chain.")
#         # Retry with a different peer or take other measures
#     else:
#         print("Chain synchronized and validated.")

#     # Save the last time consensus was performed
#     last_consensus_time = time()


# def validate_chain():
#     for i in range(1, len(block_list)):
#         curr_block = block_list[i]
#         prev_block = block_list[i - 1]

#         # Recalculate hash for current block
#         hashBase = hashlib.sha256()

#         # Include the previous block's hash
#         hashBase.update(prev_block["hash"].encode())

#         # Include miner's name
#         hashBase.update(curr_block["minedBy"].encode())

#         # Include messages in order
#         for m in curr_block["messages"]:
#             hashBase.update(m.encode())

#         # Include the timestamp (convert to bytes)
#         hashBase.update(int(curr_block["timestamp"]).to_bytes(8, 'big'))

#         # Include the nonce
#         hashBase.update(curr_block["nonce"].encode())

#         # Calculate the hash
#         calculated_hash = hashBase.hexdigest()

#         # Validate hash and difficulty
#         if calculated_hash != curr_block["hash"] or calculated_hash[-1 * DIFFICULTY:] != '0' * DIFFICULTY:
#             print(f"Block {i} validation failed.")
#             print(f"Expected Hash: {curr_block['hash']}, Calculated Hash: {calculated_hash}")
#             return False

#     print("All blocks validated successfully.")
#     return True




# #validates and adds the block in the chain 
# def add_block(block):
#     print(f"\nADD_BLOCK: \n{block}")
#     new_block ={
#         "height" : None,
#         "minedBy" : None,
#         "nonce" : None,
#         "messages" : [],
#         "prevHash" : None,
#         "hash" : None,
#     }

#     if block["height"] == len(block_list):
#         print("ADD_BLOCK->HEIGHT = 0")
#         new_block["height"] = block["height"]
#         new_block["minedBy"] = block["minedBy"]

#         #validating nonce
#         if len(block["nonce"]) < 40:
#             new_block["nonce"] = block["nonce"]
#             print("ADD_BLOCK->HEIGHT = 0 -> NONCE Validated")

            
#             #validate messages
#             if len(block["messages"]) <=10:
#                 for m in block["messages"]:
#                     if len(m) <= 20:
#                         new_block["messages"].append(m)
#                         print("ADD_BLOCK->HEIGHT = 0 -> NONCE Validated->Messages ADDED")

                
#                 #hash validation
#                 hashBase = hashlib.sha256()
#                 # get the most recent hash

#                 # if len(block_list) > 0:
#                 #     lastHash = block_list[-1]["hash"]
#                 #     new_block["prevHash"] = lastHash
#                 #     # add it to this hash
#                 #     hashBase.update(lastHash.encode())            

#                 # add the miner
#                 hashBase.update(block['minedBy'].encode())

#                 # add the messages in order
#                 for m in block['messages']:                
#                     hashBase.update(m.encode())

#                 # add the nonce
#                 hashBase.update(block['nonce'].encode())   

#                 # get the pretty hexadecimal
#                 hash = hashBase.hexdigest()                   
#                 print(f"ADD_BLOCK->HEIGHT = 0 -> NONCE Validated->Messages ADDED ->\n\nHASH: {hash}")
#                 # is it difficult enough? then add to end of the chain 
#                 if hash[-1 * DIFFICULTY:] == '0' * DIFFICULTY:
#                     if hash == block["hash"]:
#                         new_block["hash"] = block["hash"]
#                         block_list.append(new_block)
#                         print(f"ADD_BLOCK->BLOCK ADDED->{new_block}")


#29 November
# def consensus():
#     print("\n\n\nIN CONSENSUS\n\n\n")
#     stat_req = { "type": "STATS" }
#     stat_req = json.dumps(stat_req).encode()
#     print("\nCONSENSUS->STAT_REQUESTED")

#     stats_replies = []
#     mySocket.settimeout(2)  # Timeout for response

#     # Request stats from peers
#     for curr_peer in peers:
#         replied = False
#         retry_count = 0
#         max_retries = 3
#         while not replied and retry_count < max_retries:
#             retry_count += 1
#             mySocket.sendto(stat_req, curr_peer)
#             try:
#                 data, addr = mySocket.recvfrom(1024)
#                 data_json = json.loads(data.decode())

#                 if data_json["type"] == "STATS_REPLY":
#                     stats_replies.append([data_json["height"], curr_peer])
#                     replied = True
                
#                 if data_json["type"] == "GOSSIP_REPLY":
#                     peer_gossip(data_json)

#                 if data_json["type"] == "GOSSIP":
#                     print(f"CONSENSUS->STAT_REQUESTED->ForLoop->WhileLoop->GOSSIP")
#                     send_gossip_reply(data_json)

#             except socket.timeout:
#                 print("Timeout while waiting for peer response.")
#             except Exception as e:
#                 print(f"Error during stats request: {e}")

#     # No valid responses from peers
#     if not stats_replies:
#         print("No peers responded with valid stats.")
#         return

#     # Identify the longest chain
#     max_chain = max(stats_replies, key=lambda x: x[0])[0]
#     max_chain_peers = [peer for height, peer in stats_replies if height == max_chain]
#     print(f"\n\nCONSENSUS->MAX_CHAIN_PEERS: {max_chain_peers}")

#     # Request blocks from peers to sync chain
#     while len(block_list) < max_chain:
#         block_req = {
#             "type": "GET_BLOCK",
#             "height": len(block_list)
#         }
#         for curr_peer in max_chain_peers:
#             replied = False
#             retry_count = 0
#             max_retries = 3
#             while not replied and retry_count < max_retries:
#                 retry_count += 1
#                 mySocket.sendto(json.dumps(block_req).encode(), curr_peer)
#                 mySocket.settimeout(2)  # Timeout for response

#                 try:
#                     data, addr = mySocket.recvfrom(1024)
#                     data_json = json.loads(data.decode())

#                     if data_json["type"] == "GET_BLOCK_REPLY":
#                         add_block(data_json)
#                         replied = True
                    
#                     if data_json["type"] == "GOSSIP_REPLY":
#                         peer_gossip(data_json)

#                     if data_json["type"] == "GOSSIP":
#                         send_gossip_reply(data_json)
#                 except socket.timeout:
#                     print("Timeout while waiting for block response.")
#                 except Exception as e:
#                     print(f"Error during block request: {e}")

#     # Validate the full chain
#     if not validate_chain():
#         print("Chain validation failed. Attempting next longest chain.")
#         # Retry with a different peer or take other measures
#     else:
#         print("Chain synchronized and validated.")

#     # Save the last time consensus was performed
#     last_consensus_time = time()


# # Method to print peers with last GOSSIP time
# def print_peers():
#     print("\n--- Peers in the Network ---")
#     if len(peers) == 0:
#         print("No peers currently connected.")
#     else:
#         for idx, peer in enumerate(peers):
#             # Calculate time elapsed since last GOSSIP message
#             time_elapsed = time() - last_GOSSIP_time_peers[idx] if last_GOSSIP_time_peers[idx] != -1 else None
#             time_display = f"{time_elapsed:.2f} seconds" if time_elapsed is not None else "N/A"
#             print(f"{idx + 1}. Peer Address: {peer[0]}, Peer Port: {peer[1]}, Last GOSSIP: {time_display}")
#     print("----------------------------")


#NEW VALIDATE
# def consensus():
#     print("\n\nIN CONSENSUS\n\n")
#     # Request stats from all peers
#     stat_req = {"type": "STATS"}
#     stat_req = json.dumps(stat_req).encode()
#     stats_replies = []

#     # Broadcast stats request to all peers
#     for curr_peer in peers:
#         replied = False
#         retry_count = 0
#         max_retries = 3
#         while not replied and retry_count < max_retries:
#             retry_count += 1
#             mySocket.sendto(stat_req, curr_peer)
#             try:
#                 data, addr = mySocket.recvfrom(1024)
#                 mySocket.settimeout(10)  # Timeout for response
#                 data_json = json.loads(data.decode())

#                 if data_json["type"] == "STATS_REPLY":
#                     stats_replies.append([data_json["height"], curr_peer])
#                     replied = True

#                 elif data_json["type"] == "GOSSIP_REPLY":
#                     peer_gossip(data_json)

#                 elif data_json["type"] == "GOSSIP":
#                     send_gossip_reply(data_json)

#             except socket.timeout:
#                 print(f"Timeout while waiting for peer {curr_peer} response.")
#             except Exception as e:
#                 print(f"Error during stats request from {curr_peer}: {e}")
#     print(f"STAT_REPLIES: {stats_replies}")
#     # Check if no valid stats were received
#     if not stats_replies:
#         print("No peers responded with valid stats.")
#         return

#     # Find the most agreed-upon chain height
#     height_counts = {}
#     for height, _ in stats_replies:
#         if height not in height_counts:
#             height_counts[height] = 0
#         height_counts[height] += 1

#     most_agreed_height = max(height_counts, key=lambda h: (height_counts[h], h))

#     # Create a list of peers that agree on the most agreed-upon height
#     max_chain_peers = []
#     bad_actors = []  # To track bad actors (peers with height > most agreed-upon height)

#     for height, peer in stats_replies:
#         # Check if the peer is yourself or a bad actor
#         if peer == (myhost, myPort) or peer in bad_actors:
#             continue  # Skip adding this peer
#         if height == most_agreed_height:
#             max_chain_peers.append(peer)
#         elif height > most_agreed_height:
#             bad_actors.append(peer)  # Track bad actors

#     # Debugging output
#     print(f"CONSENSUS->MOST_AGREED_HEIGHT: {most_agreed_height}")
#     print(f"CONSENSUS->MAX_CHAIN_PEERS: {max_chain_peers}")
#     print(f"CONSENSUS->BAD_ACTORS: {bad_actors}")

#     # Create a new list of valid peers (excluding bad actors and yourself)
#     good_peers = [peer for peer in peers if peer != (myhost, myPort) and peer not in bad_actors]
#     print(f"GOOD PEERS: {good_peers}")

#     # Check if we have any peers to work with
#     if not max_chain_peers:
#         print("No peers have the most agreed-upon height. Exiting consensus.")
#         return
    
#     if not good_peers:
#         print("No good peers available for block requests.")
#         return

    # # Request blocks from peers who agree on the most agreed-upon height
    # batch_size = 50  # Number of blocks to request at a time
    # current_peer_index = 0

    # while len(block_list) < most_agreed_height:
    #     start_height = len(block_list)
    #     end_height = min(start_height + batch_size, most_agreed_height)

    #     # Select peer in a round-robin manner from filtered peers
    #     curr_peer = good_peers[current_peer_index]
    #     current_peer_index = (current_peer_index + 1) % len(good_peers)

    #     print(f"Requesting blocks {start_height}-{end_height - 1} from peer {curr_peer}")

    #     for height in range(start_height, end_height):
    #         block_req = {
    #             "type": "GET_BLOCK",
    #             "height": height
    #         }
    #         retry_count = 0
    #         max_retries = 3
    #         replied = False

    #         while retry_count < max_retries and not replied:
    #             retry_count += 1
    #             mySocket.sendto(json.dumps(block_req).encode(), curr_peer)
    #             mySocket.settimeout(10)  # Timeout for response

    #             try:
    #                 data, addr = mySocket.recvfrom(1024)

    #                 # Process the response only if it matches the expected format
    #                 data_json = json.loads(data.decode())
    #                 if data_json["type"] == "GET_BLOCK_REPLY":
    #                     build_chain(data_json)  # Add block without validation
    #                     replied = True

    #                 elif data_json["type"] == "GOSSIP_REPLY":
    #                     peer_gossip(data_json)

    #                 elif data_json["type"] == "GOSSIP":
    #                     send_gossip_reply(data_json)

    #                 else:
    #                     print(f"Unexpected response type from {curr_peer}: {data_json['type']}")

    #             except socket.timeout:
    #                 print(f"Timeout for block {height} from peer {curr_peer}. Retrying...")
    #             except Exception as e:
    #                 print(f"Error requesting block {height} from peer {curr_peer}: {e}")

    # # Validate the full chain
    # if not validate_chain():
    #     print("Chain validation failed. Consensus could not synchronize.")
    #     print("\n\n Attempting consensus again\n\n")
    #     print(f"\n\nLast_Consensus_time: {last_consensus_time}\n\n")

    #     last_consensus_time = time()

    #     consensus()  # Uncommented to retry consensus
    # else:
    #     print("Chain synchronized and validated.")

    # # Save the last time consensus was performed
    # last_consensus_time = time()
    # print(f"\n\nLast_Consensus_time: {last_consensus_time}\n\n")


    # # Validate the full chain
    # if not validate_chain():
    #     print("Chain validation failed. Consensus could not synchronize.")
    #     print("\n\n Attempting consensus again\n\n")

    #     last_consensus_time = time()
    #     print(f"\n\nLast_Consensus_time: {last_consensus_time}\n\n")
    #     consensus()  # Uncommented to retry consensus
    # else:
    #     print("Chain synchronized and validated.")

    # # Save the last time consensus was performed
    # last_consensus_time = time()
    # print(f"\n\nLast_Consensus_time: {last_consensus_time}\n\n")
    
    
        # # Determine the most agreed-upon chain height
    # height_counts = {}
    # for height, _, _ in stats_replies:
    #     height_counts[height] = height_counts.get(height, 0) + 1
    
    # print(f"\nHEIGHT COUNT: {height_counts}\n")

    # # Filter out heights that are less than or equal to 0
    # valid_heights = {height: count for height, count in height_counts.items() if height is not None and height > 0}
    # print(f"\nValid HEIGHT: {valid_heights}\n")

    # # Ensure there are valid heights to consider
    # if not valid_heights:
    #     print("No valid chain heights found (all heights <= 0). Consensus cannot proceed.")
    #     most_agreed_height = 0  # Default or handle this case separately
    # else:
    #     # Find the most agreed-upon height manually
    #     highest_count = -1
    #     most_agreed_height = None
    #     for height, count in valid_heights.items():
    #         if count > highest_count or (count == highest_count and (most_agreed_height is None or height > most_agreed_height)):
    #             most_agreed_height = height
    #             highest_count = count

    # print(f"Most agreed height: {most_agreed_height}")
    # bad_actors.add(("130.179.28.116", 8999))
    # bad_actors.add(("130.179.28.116", 8997))