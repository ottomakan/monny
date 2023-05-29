#!/bin/bash

## Initialization script to set up environment to run monny
## activate python
source /home/poktadmin/monenv/bin/activate

export PATH=/home/poktadmin/.local/bin:$PATH

## Check server disk and other resources
/home/poktadmin/monny/serv_mon.py

## Check sync status of Polygon node
/home/poktadmin/monny/eth_mon.py

## Deactivate Python venv (activated by monny_pre.sh)
deactivate
echo "Finished monny.sh"
