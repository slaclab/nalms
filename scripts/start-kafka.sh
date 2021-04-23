#!/bin/sh
# Author: Jacqueline Garrahan
#
# Starts kafka server 
#
# Copyright @2021 SLAC National Accelerator Laboratory
if [ "$1" == "-h" ]; then
  echo "Usage: start-local-kafka.sh server.properties"
  exit 0
fi


if [[ -z "$1"  && ! -f "$KAFKA_PROPERTY_FILE" || ! -f "$1"]]; then
  echo "Kafka server property files not provided. Pass property file or set \$KAFKA_PROPERTY_FILE"
  echo "Usage: start-local-kafka.sh server_property_file"
  exit 0
fi

# check KAFKA_TOP is set
if [[ ! -d "$KAFKA_TOP" ]]; then
  echo "KAFKA_TOP is incorrectly configured."
  echo "\$KAFKA_TOP = ${KAFKA_TOP}"
  exit 0
fi

# check NALMS_ENV is set
if [[ -z "$NALMS_ENV" ]]; then
  echo "No environment. Must set \$NALMS_ENV=prod,dev"
  echo "\$NALMS_ENV = ${NALMS_ENV}"
  exit 0
fi

# check NALMS_TOP is set
if [[ ! -d "$NALMS_TOP" ]]; then
  echo "NALMS_TOP is incorrectly configured."
  echo "\$NALMS_TOP = ${NALMS_TOP}"
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


# check for zookeeper and 
if [[ ! -z $( echo srvr | nc $ZOOKEEPER_HOST_BASE $ZOOKEEPER_PORT ) ]]; then

  echo "Starting Kafka cluster..."
  if [[ -f "$KAFKA_PROPERTY_FILE" ]]; then
    ${KAFKA_TOP}/current/bin/kafka-server-start.sh  -daemon $KAFKA_PROPERTY_FILE
  else
    ${KAFKA_TOP}/current/bin/kafka-server-start.sh  -daemon ${NALMS_TOP}/current/config/${NALMS_ENV}_server.properties
  fi

else
  echo "Running zookeeper not detected of ${ZOOKEEPER_HOST}."
fi