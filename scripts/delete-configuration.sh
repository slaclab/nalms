#!/bin/sh
# Author: Jacqueline Garrahan
#
# Mark all topics related to a configuration for deletion. 
# It is important to note that deletion will not be immediate.
#
# Copyright @2021 SLAC National Accelerator Laboratory

if [ "$1" == "-h" ]; then
  echo "Usage: delete-configurations.sh configuration_name"
  echo "Requires \$KAFKA_TOP and \$ZOOKEEPER_HOST to be set."
  exit 0
fi

if [[ ! -d "$KAFKA_TOP" ]]; then
  echo "KAFKA_TOP is not set."
  exit 0
fi

if [[ -z "$ZOOKEEPER_HOST" ]]; then
  echo "ZOOKEEPER_HOST is not set."
  exit 0
fi

if [[ -z "$1" ]]; then
  echo "Configuration not provided."
  echo "Usage: delete-configurations.sh configuration_name"
  exit 0
fi

CONFIGURATION=$1

$KAFKA_TOP/current/bin/kafka-topics.sh --zookeeper $ZOOKEEPER_HOST --delete --topic "${CONFIGURATION}"
$KAFKA_TOP/current/bin/kafka-topics.sh --zookeeper $ZOOKEEPER_HOST --delete --topic "${CONFIGURATION}Talk"
$KAFKA_TOP/current/bin/kafka-topics.sh --zookeeper $ZOOKEEPER_HOST --delete --topic "${CONFIGURATION}Command"
