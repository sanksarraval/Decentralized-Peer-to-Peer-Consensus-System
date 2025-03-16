# Peer Synchronization & Consensus  

This repository contains the implementation of a **peer-to-peer network simulation** for achieving synchronization and consensus. The project is developed as part of **COMP 3010** at the University of Manitoba and focuses on **peer gossiping, consensus mechanisms, and blockchain validation**.  

## 📌 Features  
- **Peer Communication:** Peers exchange GOSSIP messages to stay connected and share information.  
- **Consensus Algorithm:** Determines the longest valid chain based on peer agreement.  
- **Block Synchronization:** Fetches missing blocks in a round-robin manner from trusted peers.  
- **Peer Cleanup:** Removes inactive peers if they fail to send GOSSIP messages for over 60 seconds.  
- **Resilient Execution:** Implements retry logic for message exchanges and consensus validation.  

## 🔧 How to Run  
Start a peer using the following command:  

```bash
python peer.py <MyName> <MyPort> <NetworkServer> <NetworkPort>
```
## 🔍 Expected Behavior
- Peers periodically send and receive GOSSIP and STATS messages.
- The network performs consensus every 2 minutes to validate and synchronize the blockchain.
- If consensus fails or no valid peers are found, re-running the program may help.

##📌 Notes
- Ensure at least 4 active peers in the network for efficient message propagation.
- Chain validation retries up to 10 times before marking consensus as failed.

##📫 Contact
- For any questions or clarifications, feel free to reach out!
