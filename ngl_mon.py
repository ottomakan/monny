#!/bin/env python

import requests, statistics
import time
import config_mon as cm

def ngl_progress_check(nodes):
    block_heights = []
    for node in nodes:
        url = f"http://{node}.{cm.domain}:{cm.port}"
        try:
            response = requests.post(url, json={"jsonrpc": "2.0", "method": "eth_blockNumber", "params": [], "id": 1})
            if response.status_code == 200:
                result_hex = response.json().get("result")
                # Convert hexadecimal to decimal
                block_height = int(result_hex, 16)
                block_heights.append(block_height)
            else:
                print(f"Failed to connect to node {node}. Status code: {response.status_code}")
                cm.send_tg_msg(f"Alert from {cm.myhostname}: NGL on {node} returned Status code: {response.status_code}. Maybe DOWN? \U0001F62D")
        except Exception as e:
            print(f"Error connecting to node {node}: {e}")
            cm.send_tg_msg(f"Alert from {cm.myhostname}: NGL on {node} is DOWN!! \U0001F62D")
    if block_heights:
        # max_height = max(block_heights)
        # avg_height = sum(block_heights) / len(block_heights)
        if statistics.stdev(block_heights) > 1:
            print(f"Difference between max and avg block heights is greater than 1")
            print(f'{nodes} block heights: {block_heights}')
            cm.send_tg_msg(f"{cm.myhostname}: One or more NGL node is BEHIND!! \U0001F62D \n{nodes} \nblock heights: {block_heights}")

        else:
            print("Difference between max and avg block heights is not greater than 1")
            print(f'{nodes} block heights: {block_heights}')
            # cm.send_tg_msg(f"{cm.myhostname}: One or more NGL node is BEHIND!! \U0001F62D \n{nodes} \nblock heights: {block_heights}")

    return block_heights

block_heights = ngl_progress_check(cm.nodes)
# print("Block heights:", block_heights)
# print("Standard deviation of block heights:", statistics.stdev(block_heights))