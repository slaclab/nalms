#!/bin/sh
# Author: Jacqueline Garrahan
#
# Starts kafka server 
#
# Copyright @2021 SLAC National Accelerator Laboratory

if [ "$1" == "-h" ]; then
  echo "Usage: start-local-zookeeper.sh zookeeper.properties"
  exit 0
fi


if [[ -z "$1"  && ! -f "$ZOOKEEPER_PROPERTY_FILE" || ! -f "$1"]]; then
  echo "Kafka server property files not provided. Pass property file or set \$KAFKA_PROPERTY_FILE"
  echo "Usage: start-local-zookeeper.sh zookeeper_property_file"
  exit 0
fi

# check KAFKA_TOP is set
if [[ ! -d "$KAFKA_TOP" ]]; then
  echo "KAFKA_TOP is incorrectly configured."
  echo "\$KAFKA_TOP = ${KAFKA_TOP}"
  exit 0
fi

# check NALMS_TOP is set
if [[ ! -d "$NALMS_TOP" ]]; then
  echo "NALMS_TOP is incorrectly configured."
  echo "\$NALMS_TOP = ${NALMS_TOP}"
  exit 0
fi

# check NALMS_ENV is set
if [[ -z "$NALMS_ENV" ]]; then
  echo "No environment. Must set \$NALMS_ENV=prod,dev"
  echo "\$NALMS_ENV = ${NALMS_ENV}"
  exit 0
fi

# check NALMS_TOP is set
if [[ -z "$ZOOKEEPER_HOST" ]]; then
  echo "ZOOKEEPER_HOST is not set."
  exit 0
fi

ZOOKEEPER_PROPERTY_FILE=$1
SERVER_PROPERTY_FILE=$2

ZOOKEEPER_HOST_BASE="$(cut -d':' -f1 <<< $ZOOKEEPER_HOST)"
ZOOKEEPER_PORT="$(cut -d':' -f2 <<< $ZOOKEEPER_HOST)"

# Check property file provided
if [[ -z "$1" ]]; then
  if [[-z "$ZOOKEEPER_PROPERTY_FILE"]]; then
    echo "Property files not provided. Must pass property files or define \$ZOOKEEPER_PROPERTY_FILE and \$SERVER_PROPERTY_FILE"
    echo "Usage: start_kafka.sh zookeeper_property_file server_property_file"
    exit 0
  fi
fi


if [[ -f "$ZOOKEEPER_PROPERTY_FILE" ]]; then
    $KAFKA_TOP/bin/zookeeper-server-start.sh  -daemon $ZOOKEEPER_PROPERTY_FILE
else
    $KAFKA_TOP/bin/zookeeper-server-start.sh  -daemon $NALMS_TOP/config/${NALMS_ENV}_zookeeper.properties
fi
echo "Starting Zookeeper..."

# allow time to set up
sleep 30

# check zookeeper has started
if [[ ! -z $( echo srvr | nc $ZOOKEEPER_HOST_BASE $ZOOKEEPER_PORT ) ]] ; then
    echo "Zookeeper service started."
fi