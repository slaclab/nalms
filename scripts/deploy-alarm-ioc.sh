#!/usr/bin/env bash
#
# Author: Jacqueline Garrahan
# Run phoebus-alarm-server image for given configuration
#
if [ "$1" == "-h" ]; then
  echo "Usage: deploy-ioc.sh [Configuration Name] [Configuration file]"
  exit 0
fi

#PREFIX!!!

docker run -v $2:/tmp/nalms/$1.xml -e CONFIG_NAME=$1 -e CONFIG_FILE=/tmp/nalms/$1.xml -p "5065:5065/tcp" -p "5064:5064/tcp" -p "5065:5065/udp" -p "5064:5064/udp" -it alarm-ioc 