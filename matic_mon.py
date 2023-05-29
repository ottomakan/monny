#!/bin/env python
import requests
import json
import time
import config_mon as cm

# Set the endpoint URL for the Bor node.
NODE_URL = cm.my_node_url

# Replace <YOUR_POLYSCAN_API_KEY> with your PolyScan API key.
POLYSCAN_API_KEY = cm.polyscan_api_key

# Define the function to retrieve the latest block number from PolyScan.
def get_latest_block_number():
    try:
        # Send an HTTP GET request to retrieve the latest block number.
        response = requests.get(
            f'{cm.polyscan_url}&apikey={POLYSCAN_API_KEY}')
        response.raise_for_status()
        latest_block_number_hex = response.json()['result']
        latest_block_number = int(latest_block_number_hex, 16)
        return latest_block_number
    except requests.exceptions.RequestException as e:
        print(f'Error: Unable to connect to PolyScan API: {e}')
        return None
    except json.JSONDecodeError as e:
        print(f'Error: Unable to decode JSON response from PolyScan API: {e}')
        return None
    except KeyError:
        print(f'Error: Unexpected response format from PolyScan API')
        return None
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 429:
            print(
                f'Error: Max rate limit reached for PolyScan API. Retrying in 60 seconds...')
            # time.sleep(60)
            return None
        else:
            print(f'Error: Unexpected HTTP error from PolyScan API: {e}')
            return None

# Define the main function to retrieve the latest block from the Bor node.
def get_my_latest_block():
    try:
        # Send a JSON-RPC request to the Bor node to retrieve the latest block.
        payload = {
            'jsonrpc': '2.0',
            'id': 1,
            'method': 'eth_blockNumber',
            'params': []
        }
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.post(NODE_URL, json=payload, headers=headers)
        response.raise_for_status()
        latest_block_number_hex = response.json()['result']
        latest_block_number = int(latest_block_number_hex, 16)
        return latest_block_number
    except requests.exceptions.RequestException as e:
        print(f'Error: Unable to connect to Bor node: {e}')
        print("Our Bor node is DOWN!! \U0001F62D")
        cm.send_tg_msg(f"{cm.myhostname}: Our Bor node is DOWN!! \U0001F62D")
        return None
    except json.JSONDecodeError as e:
        print(f'Error: Unable to decode JSON response from Bor node: {e}')
        return None
    except KeyError:
        print(f'Error: Unexpected response format from Bor node')
        return None
    except Exception as e:
        print("Our Bor node is DOWN!! \U0001F62D")
        cm.send_tg_msg(f"{cm.myhostname}: Our Bor node is DOWN!! \U0001F62D")
        return None

# Call the functions to retrieve the latest block numbers.
poly_latest_block_number = get_latest_block_number()
bor_latest_block_number = get_my_latest_block()

if poly_latest_block_number is not None and bor_latest_block_number is not None:
    print(f'PolyScan latest block number: {poly_latest_block_number}')
    print(f'My latest block number: {bor_latest_block_number}')
    if bor_latest_block_number > poly_latest_block_number:
        print("Our Bor node is AHEAD of PolyScan network \U0001F60E")
    elif abs(poly_latest_block_number - bor_latest_block_number) < cm.alert_theshold_blocks:
        print("Our Bor node is in sync with the PolyScan network \U0001F600")
        ## send message on Telegram!
        #cm.send_tg_msg(f"{cm.myhostname}: Polygon node is in sync \U0001F600\n Network block height: {poly_latest_block_number}\n Our block height: {bor_latest_block_number}")
    else:
        print("Our Bor node is not in sync with the PolyScan network \U0001F622")
        ## send message on Telegram!
        cm.send_tg_msg(f"{cm.myhostname}: Polygon node is not in sync \U0001F622\n Network block height: {poly_latest_block_number}\n Our block height: {bor_latest_block_number}")
        
