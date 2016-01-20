#!/bin/bash

#change this to whatever location you checked out to
export ROOT=/home/rentrocket/rentrocket
#utilizes mindstream for launching:
#https://github.com/charlesbrandt/mindstream
launch.py -c $ROOT blank

echo "Other common options:
launch.py -c $ROOT columbia

launch.py -c $ROOT scripts

launch.py -c $ROOT settings
launch.py -c $ROOT code
launch.py -c $ROOT layout
launch.py -c $ROOT design

launch.py -c $ROOT auth
launch.py -c $ROOT resources

new window
cd /c/clients/rentrocket/code/
/c/downloads/python/google_appengine/dev_appserver.py rentrocket

"
