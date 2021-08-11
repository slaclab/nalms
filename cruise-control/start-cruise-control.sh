#!/bin/bash
#
# Author: Jacqueline Garrahan
# Start up phoebus client
usage() {
  cli_name=${0##*/}
  echo "Usage: start-cruise-control.sh"
  echo "Requires definition of \$ZOOKEEPER_CONNECT, \$BOOTSTRAP_SERVERS"
  exit 0
}

if [[ "$1" == "-h" ]]; then
  usage
fi

if [[ -z "$ZOOKEEPER_CONNECT" ]]; then
  echo "Zookeeper connect host not provided."
  usage
fi

if [[ -z "$BOOTSTRAP_SERVERS" ]]; then
  echo "Bootstrap servers not provided."
  usage
fi


sed -i 's/$ZOOKEEPER_CONNECT/'"$ZOOKEEPER_CONNECT/" $CRUISE_CONTROL_PROPERTIES
sed -i 's/$BOOTSTRAP_SERVERS/'"$BOOTSTRAP_SERVERS/" $CRUISE_CONTROL_PROPERTIES

./kafka-cruise-control-start.sh $CRUISE_CONTROL_PROPERTIES