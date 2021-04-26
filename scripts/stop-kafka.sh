#!/bin/sh
# Author: Jacqueline Garrahan
#
# Stops Kafka server 
#
# Copyright @2021 SLAC National Accelerator Laboratory

if [[ -d $KAFKA_TOP ]]; then 
    $KAFKA_TOP/bin/kafka-server-stop.sh
    $KAFKA_TOP/bin/zookeeper-server-stop.sh
else
    echo "Kafka path not found. Has environment been set? KAFKA_TOP: ${KAFKA_TOP}"
fi