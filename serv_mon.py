#!/usr/bin/env python3
import config_mon as cm
import psutil
import os
import subprocess

# Retrieve the current value of PATH
path = os.environ.get('PATH', '')

# Append the new directory to PATH
# new_path = cm.local_path + path

# Set the updated PATH value back to the os.environ dictionary
# os.environ['PATH'] = new_path

host = cm.myhostname
# tg_config_file = cm.tg_config_file
# Set the threshold for disk usage (in percentage)
THRESHOLD = cm.fs_free_threshold_pct

# Check the disk usage
#usage = psutil.disk_usage('/data')
for mount in cm.fs_list:
    #if usage.percent > THRESHOLD:
    usage = psutil.disk_usage(mount)
    if usage.percent > THRESHOLD:
        msg = f"{host}: Disk usage on {mount} is {usage.percent}%"
        # Send a Telegram message
        cm.send_tg_msg(msg)
        
