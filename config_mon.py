'''
Configuration data for monny
'''
import socket
import subprocess

def send_tg_msg(msg):
    try:
        subprocess.run(['telegram-send', '--config', tg_config_file, msg])
    except subprocess.CalledProcessError as e:
    # Handle the error
        print(f"Error running subprocess command: {e}")

## Filesystems to monitor
fs_list = ['/data','/home','/']
fs_free_threshold_pct = 90

## POLYGON Configs
polyscan_api_key = 'Y73EWHN3MMXRWV9896VPIN6VV9RGKSJ2XY'
my_node_url = 'http://localhost:8545'
polyscan_url = 'https://api.polygonscan.com/api?module=proxy&action=eth_blockNumber'
alert_theshold_blocks = 5

## Other configs
local_path = "/home/poktadmin/.local/bin"
tg_config_file = "/home/poktadmin/monny/telegram-send.conf"
myhostname = host = socket.gethostname()