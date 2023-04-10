#!/bin/env python3

import time
import requests

# Set the endpoint URL for the Polygon RPC API
endpoint_url = "http://localhost:8545"

# Set the number of seconds to run the script
duration = 10

# Set the start time for the script
start_time = time.time()

# Define the JSON-RPC payload
payload = {
    "jsonrpc": "2.0",
    "method": "eth_blockNumber",
    "params": [],
    "id": 1
}

# Initialize the counter for the number of blocks
block_count = 0

# Loop for the specified duration
while (time.time() - start_time) < duration:
    # Send the POST request to the endpoint and get the response
    response = requests.post(endpoint_url, json=payload)

    # Parse the response JSON and extract the block number
    response_json = response.json()
    block_number_hex = response_json["result"]
    block_number = int(block_number_hex, 16)

    # If the block number has changed, increment the block count
    if block_number > block_count:
        block_count = block_number

# Calculate the block processing rate
block_rate = block_count / duration

print(f"Block processing rate: {block_rate:.2f} blocks per second")  # Output the result to the console

