#!/bin/env python3

import requests

# Replace <YOUR_NODE_URL> with the URL of your Polygon node.
NODE_URL = 'http://localhost:8545'

try:
    # Retrieve the latest block number from the Polygon API.
    response = requests.get(
        'https://api.polygonscan.com/api?module=proxy&action=eth_blockNumber')
    latest_block_number = int(response.json()['result'], 16)

    # Retrieve the block number of your node.
    response = requests.post(NODE_URL, json={
                            "jsonrpc": "2.0", "method": "eth_blockNumber", "params": [], "id": 1})
    node_block_number = int(response.json()['result'], 16)

    # Compare the two block numbers and print the result.
    if abs(latest_block_number - node_block_number) < 5:
        print('Your node is in sync with the Polygon network.')
        print(f"Latest block number:{latest_block_number}\nNode block number: {node_block_number}")
    else:
        print('Your node is not in sync with the Polygon network. Latest block number is',
            latest_block_number, 'and your node block number is', node_block_number)
except ValueError as e:
    if "invalid literal for int() with base 16" in str(e):
        print(f"Value error: {e}. Invalid hex string: {latest_block_number}")
    else:
        print(f"Value error: {e}")
except requests.exceptions.RequestException as e:
    if isinstance(e, requests.exceptions.ConnectionError):
        print('Error connecting to the Polygon node:', str(e))
    elif isinstance(e, requests.exceptions.HTTPError):
        if e.response.status_code == 429 and 'max rate limit reached' in e.response.text.lower():
            print('Error connecting to PolyScan: max rate limit reached. Please wait a few minutes and try again.')
        else:
            print('Error connecting to PolyScan:', str(e))
    else:
        print('Unexpected error:', str(e))
except Exception as e:
    print('Unexpected error:', str(e))