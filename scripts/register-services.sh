#!/bin/sh
# Author: Jacqueline Garrahan
#
# Register systemd services 
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
f

# check KAFKA_TOP is set
if [[ ! -d "$KAFKA_TOP" ]]; then
  echo "KAFKA_TOP is incorrectly configured."
  echo "\$KAFKA_TOP = ${KAFKA_TOP}"
  exit 0
fi

sudo systemctl start ${ELASTICSEARCH_PATH}/bin/elasticsearch.service
sudo systemctl start ${NALMS_TOP}/current/services/zookeeper.service
sudo systemctl start ${NALMS_TOP}/current/services/kafka.service