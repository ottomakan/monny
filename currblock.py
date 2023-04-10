#!/bin/env python3

import requests

# Set the endpoint URL for the Polygon RPC API
endpoint_url = "http://localhost:8545"

# Define the JSON-RPC payload
payload = {
    "jsonrpc": "2.0",
    "method": "eth_blockNumber",
    "params": [],
    "id": 1
}

# Send the POST request to the endpoint and get the response
response = requests.post(endpoint_url, json=payload)

# Parse the response JSON and extract the block number
response_json = response.json()
block_number_hex = response_json["result"]
block_number = int(block_number_hex, 16)

print(block_number)  # Output: current block number as an integer

