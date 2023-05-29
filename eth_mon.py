#!/bin/env python

import requests
import time
import config_mon as cm

ERIGON_RPC_URL = cm.my_node_url
ETHERSCAN_API_KEY = cm.etherscan_api_key

## Check to see if the node is syncing or has already completed sync
## Returns an error when node is not reachable
def get_erigon_info():
    response = requests.post(ERIGON_RPC_URL, json={"jsonrpc": "2.0", "method": "eth_syncing", "id": 1})
    if response.status_code == 200:
        data = response.json()
        if "result" in data and data["result"]:
            return f"Erigon is syncing - Current block: {data['result']['currentBlock']}"

        response = requests.post(ERIGON_RPC_URL, json={"jsonrpc": "2.0", "method": "eth_blockNumber", "id": 1})
        if response.status_code == 200:
            data = response.json()
            if "result" in data:
                return f"Erigon is up to date - Current block: {int(data['result'], 16)}" ## Hex to int conversion
    cm.send_tg_msg(f"{cm.myhostname}: Our Erigon node is DOWN!! \U0001F62D")
    return "Failed to retrieve Erigon node status"

def is_erigon_synced():
    response = requests.post(ERIGON_RPC_URL, json={"jsonrpc": "2.0", "method": "eth_syncing", "id": 1})
    if response.status_code == 200:
        data = response.json()
        if "result" in data and data["result"] is False:
            return True
    return False

def get_etherscan_block_number():
    url = f"{cm.etherscan_url}&apikey={ETHERSCAN_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if "result" in data:
            return int(data["result"], 16)

    return -1

def compare_block_number():
    local_block_number = -1
    etherscan_block_number = get_etherscan_block_number()

    ## Get local block number
    response = requests.post(ERIGON_RPC_URL, json={"jsonrpc": "2.0", "method": "eth_blockNumber", "id": 1})
    if response.status_code == 200:
        data = response.json()
        if "result" in data:
            local_block_number = int(data["result"], 16)

    if local_block_number == -1:
        cm.send_tg_msg(f"{cm.myhostname}: Failed to retrieve our Erigon blok number. Check if Erigon node is DOWN!! \U0001F62D")
        return "Failed to retrieve local node block number."

    if etherscan_block_number == -1:
        return "Failed to retrieve Etherscan block number."
    
    if local_block_number > etherscan_block_number:
        # cm.send_tg_msg(f"{cm.myhostname}: Our node is ahead of the network! \U0001F60E\n Network block height: {etherscan_block_number}\n Our block height: {local_block_number}")
        print(f"{cm.myhostname}: Our node is ahead of the network! \U0001F60E\n Network block height: {etherscan_block_number}\n Our block height: {local_block_number}")
        return "Local node is AHEAD of the network."
    elif abs(local_block_number - etherscan_block_number) < cm.alert_theshold_blocks:
        # cm.send_tg_msg(f"{cm.myhostname}: Erigon node is in sync \U0001F600\n Network block height: {etherscan_block_number}\n Our block height: {local_block_number}")
        print(f"{cm.myhostname}: Erigon node is in sync \U0001F600\n Network block height: {etherscan_block_number}\n Our block height: {local_block_number}")
        return "Local node is in sync with the network."
    else:
        cm.send_tg_msg(f"{cm.myhostname}: Our node is BEHIND the network! \U0001F622\n Network block height: {etherscan_block_number}\n Our block height: {local_block_number}")
        print(f"{cm.myhostname}: Our node is BEHIND the network! \U0001F622\n Network block height: {etherscan_block_number}\n Our block height: {local_block_number}")
        return f"Local node is out of sync. Local block number: {local_block_number}, Etherscan block number: {etherscan_block_number}"

if __name__ == "__main__":
    erigon_status = get_erigon_info()
    print("Erigon: ", erigon_status)

    # if is_erigon_synced():
    #     print("Erigon is synced with the network!")
    # else:
    #     print("Erigon is not synced with the network.")

    sync_status = compare_block_number()
    print("Sync status: ", sync_status)

    print("-----------")