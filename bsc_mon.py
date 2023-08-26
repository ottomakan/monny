#!/bin/env python

import requests
import time
import config_mon as cm

BSC_RPC_URL = cm.my_bsc_url  # Replace with the actual BSC RPC URL
BSCSCAN_API_KEY = cm.bsc_api_key  # Replace with your BSCScan API Key

def get_bsc_info():
    response = requests.post(BSC_RPC_URL, json={"jsonrpc": "2.0", "method": "eth_syncing", "id": 1})
    if response.status_code == 200:
        data = response.json()
        if "result" in data and data["result"]:
            return f"BSC node is syncing - Current block: {data['result']['currentBlock']}"

        response = requests.post(BSC_RPC_URL, json={"jsonrpc": "2.0", "method": "eth_blockNumber", "id": 1})
        if response.status_code == 200:
            data = response.json()
            if "result" in data:
                return f"BSC node is up to date - Current block: {int(data['result'], 16)}"  # Hex to int conversion
    cm.send_tg_msg(f"{cm.myhostname}: Our BSC node is DOWN!! \U0001F62D")
    return "Failed to retrieve BSC node status"

def is_bsc_synced():
    response = requests.post(BSC_RPC_URL, json={"jsonrpc": "2.0", "method": "eth_syncing", "id": 1})
    if response.status_code == 200:
        data = response.json()
        if "result" in data and data["result"] is False:
            return True
    return False

def get_bscscan_block_number():
    url = f"https://api.bscscan.com/api?module=proxy&action=eth_blockNumber&apikey={BSCSCAN_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if "result" in data:
            return int(data["result"], 16)

    return -1

def compare_block_number():
    local_block_number = -1
    bscscan_block_number = get_bscscan_block_number()

    response = requests.post(BSC_RPC_URL, json={"jsonrpc": "2.0", "method": "eth_blockNumber", "id": 1})
    if response.status_code == 200:
        data = response.json()
        if "result" in data:
            local_block_number = int(data["result"], 16)

    if local_block_number == -1:
        cm.send_tg_msg(f"{cm.myhostname}: Failed to retrieve our BSC blok number. Check if BSC node is DOWN!! \U0001F62D")
        return "Failed to retrieve local node block number."

    if bscscan_block_number == -1:
        return "Failed to retrieve BSCScan block number."

    if local_block_number > bscscan_block_number:
        print(f"{cm.myhostname}: Our node is ahead of the network! \U0001F60E\n Network block height: {bscscan_block_number}\n Our block height: {local_block_number}")
        return "Local node is AHEAD of the network."
    elif abs(local_block_number - bscscan_block_number) < cm.alert_theshold_blocks:
        print(f"{cm.myhostname}: BSC node is in sync \U0001F600\n Network block height: {bscscan_block_number}\n Our block height: {local_block_number}")
        return "Local node is in sync with the network."
    else:
        cm.send_tg_msg(f"{cm.myhostname}: Our node is BEHIND the network! \U0001F622\n Network block height: {bscscan_block_number}\n Our block height: {local_block_number}")
        return f"Local node is out of sync. Local block number: {local_block_number}, BSCScan block number: {bscscan_block_number}"

if __name__ == "__main__":
    bsc_status = get_bsc_info()
    print("BSC: ", bsc_status)

    sync_status = compare_block_number()
    print("Sync status: ", sync_status)
