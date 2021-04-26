#!/bin/sh
# Author: Jacqueline Garrahan
#
# Start systemd services for single machine installation
#
# Copyright @2021 SLAC National Accelerator Laboratory

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

# check KAFKA_TOP is set
if [[ ! -d "$KAFKA_TOP" ]]; then
  echo "KAFKA_TOP is incorrectly configured."
  echo "\$KAFKA_TOP = ${KAFKA_TOP}"
  exit 0
fi

# check ELASTICSEARCH_TOP is set
if [[ ! -d "$ELASTICSEARCH_TOP" ]]; then
  echo "ELASTICSEARCH_TOP is incorrectly configured."
  echo "\$ELASTICSEARCH_TOP = ${ELASTICSEARCH_TOP}"
  exit 0
fi


sudo systemctl start ${ELASTICSEARCH_TOP}/bin/elasticsearch.service
sudo systemctl start ${NALMS_TOP}/services/zookeeper.service
sudo systemctl start ${NALMS_TOP}/services/kafka.service