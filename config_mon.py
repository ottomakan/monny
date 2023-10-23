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

my_node_url = 'http://localhost:8545'

local_urls = {
    "scroll" : "http://localhost:8545",
    "geth" : "http://localhost:7545"
}
scan_urls = {
    "scroll" : ["https://api.scrollscan.com/api?module=proxy&action=eth_blockNumber", "Q1JV7SDPWWDDC9BPKAHG2ANUWQFXRJQNNZ"],
    "geth" : ["https://api.etherscan.io/api?module=proxy&action=eth_blockNumber", "R3J4QRQBXSPPWCGQC32UG4MQ7IEH46CDDR"]
}
## POLYGON Configs
polyscan_api_key = 'Y73EWHN3MMXRWV9896VPIN6VV9RGKSJ2XY'
polyscan_url = 'https://api.polygonscan.com/api?module=proxy&action=eth_blockNumber'
alert_theshold_blocks = 10

## Erigon/Ethereum Configs
etherscan_api_key = 'R3J4QRQBXSPPWCGQC32UG4MQ7IEH46CDDR'
etherscan_url = 'https://api.etherscan.io/api?module=proxy&action=eth_blockNumber'

## Scroll Configs
scroll_api_key = 'Q1JV7SDPWWDDC9BPKAHG2ANUWQFXRJQNNZ'
scrollscan_url = 'https://api.scrollscan.com/api?module=proxy&action=eth_blockNumber'

## BSC Configs
bsc_api_key = 'FNC1ZMT2W2Q6P11JM3H21BF5G9KZUVHHIN'
bscscan_url = 'https://api.bscscan.com/api?module=proxy&action=eth_blockNumber'
my_bsc_url = 'http://localhost:9595'

## Other configs
local_path = "/home/poktadmin/.local/bin"
tg_config_file = "/home/poktadmin/monny/telegram-send.conf"
myhostname = host = socket.gethostname()
