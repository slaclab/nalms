#!/bin/sh
# Author: Jacqueline Garrahan
#
# List active configurations tracked with a zookeeper host.
#
# Copyright @2021 SLAC National Accelerator Laboratory

if [ "$1" == "-h" ]; then
  echo "Usage: list-configurations.sh"
  echo "Requires \$KAFKA_HOME and \$ZOOKEEPER_HOST to be set."
  exit 0
fi

if [[ ! -d "$KAFKA_HOME" ]]; then
  echo "KAFKA_HOME is not set."
  exit 0
fi

if [[ -z "$ZOOKEEPER_HOST" ]]; then
  echo "ZOOKEEPER_HOST is not set."
  exit 0
fi

list_var=$($KAFKA_HOME/bin/kafka-topics.sh --list --zookeeper $ZOOKEEPER_HOST)

IFS=$'\n'

read -rd '' -a strarr <<< "$list_var"

for val in "${strarr[@]}";
do
#    if  [ grep -q "Command" <<< "$val" ] && [ grep -q "Talk"  <<< "$val" ] ; then
    if [[ ! "$val" == *"Command"* && ! "$val" == *"Talk"* && ! "$val" == *"Metrics" && ! "$val" == *"consumer_offsets" ]]; then
    # && "Talk" != *"$val"*
      echo "$val";
    fi
done
