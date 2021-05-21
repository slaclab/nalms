#!/bin/sh
# Author: Jacqueline Garrahan
#
# This script creates service files using active NALMS configuration.
# Requires sudo
#
# To run only one of the services, you can use tag --elasticsearch, --kafka, --zookeeper
# To build the services without deploying use --dry
#
# Copyright @2021 SLAC National Accelerator Laboratory

if [ "$1" == "-h" ]; then
  echo "Usage: start-local-kafka.sh server.properties"
  exit 0
fi


if [[ "$*" == "--dry" ]]
then
    DRYRUN=true
else
    DRYRUN=false
fi


if [[ "$*" == "--elasticsearch" ]]
then
    ELASTICSEARCH_ONLY=true
else
    ELASTICSEARCH_ONLY=false
fi


if [[ "$*" == "--kafka" ]]
then
    KAFKA_ONLY=true
else
    KAFKA_ONLY=false
fi

if [[ "$*" == "--zookeeper" ]]
then
    ZOOKEEPER_ONLY=true
else
    ZOOKEEPER_ONLY=false
fi





if [[ ! -d "$KAFKA_TOP" ]]; then
  echo "KAFKA_TOP is not set correctly."
  echo "\$KAFKA_TOP = ${KAFKA_TOP}"
  exit 0
fi


if [[ ! -d "$NALMS_TOP" ]]; then
  echo "NALMS_TOP is not set correctly."
  echo "\$NALMS_TOP = ${NALMS_TOP}"
  exit 0
fi

if [[ -z "$NALMS_ENV" ]]; then
  echo "\$NALMS_ENV is not set."
  exit 0
fi

if [[ -z "$JAVA_HOME" ]]; then
  echo "\$JAVA_HOME is not set."
  exit 0
fi

if [[ -z "$ELASTICSEARCH_LOG_DIR" ]]; then
  echo "\$ELASTICSEARCH_LOG_DIR is not set."
  exit 0
fi


# create logging dir
if [[ ! -d "/var/log/nalms" && ! $DRYRUN ]]; then
    mkdir /var/log/nalms
fi

# check ELASTICSEARCH_TOP is set
if [[ ! -d "$ELASTICSEARCH_TOP" ]]; then
  echo "ELASTICSEARCH_TOP is incorrectly configured."
  echo "\$ELASTICSEARCH_TOP = ${ELASTICSEARCH_TOP}"
  exit 0
fi

# remove old artifacts
if ! $DRYRUN; then
  if [[ -f "$NALMS_TOP/services/nalms-kafka.service" && ! $ZOOKEEPER_ONLY && ! $ELASTICSEARCH_ONLY ]]; then
      rm $NALMS_TOP/services/nalms-kafka.service
  fi

  if [[ -f "$NALMS_TOP/services/nalms-zookeeper.service" && ! $KAFKA_ONLY && ! $ELASTICSEARCH_ONLY ]]; then
      rm $NALMS_TOP/services/nalms-zookeeper.service
  fi

  if [[ -f "$NALMS_TOP/services/nalms-elasticsearch.service" && ! $ZOOKEEPER_ONLY && ! $KAFKA_ONLY ]]; then
      rm $NALMS_TOP/services/nalms-elasticsearch.service
  fi
fi


# if not a dry run, remove relevant systemd files
if ! $DRYRUN ; then
  if [[ -f "/etc/systemd/system/nalms-kafka.service" && (! $ZOOKEEPER_ONLY || ! $ELASTICSEARCH_ONLY) ]]; then
      rm /etc/systemd/system/nalms-kafka.service
  fi

  if [[ -f "/etc/systemd/system/nalms-zookeeper.service"  && (! $KAFKA_ONLY || ! $ELASTICSEARCH_ONLY) ]]; then
      rm /etc/systemd/system/nalms-zookeeper.service
  fi

  if [[ -f "/etc/systemd/system/nalms-elasticsearch.service" && (! $ZOOKEEPER_ONLY || ! $KAFKA_ONLY) ]]; then
      rm /etc/systemd/system/nalms-elasticsearch.service
  fi
fi 

if ! $ZOOKEEPER_ONLY || ! $ELASTICSEARCH_ONLY; then

  KAFKA_FILE=$NALMS_TOP/services/nalms-kafka.service

  touch $KAFKA_FILE

  echo "# File /etc/systemd/system/nalms-kafka.service">> $KAFKA_FILE
  echo "# Generated from $NALMS_TOP/scripts/build-services.sh " >> $KAFKA_FILE
  echo "" >> $KAFKA_FILE
  echo "" >> $KAFKA_FILE

  echo "[Unit]" >> $KAFKA_FILE
  echo "Description=Apache Kafka server (broker)" >> $KAFKA_FILE
  echo "Documentation=http://kafka.apache.org/documentation.html" >> $KAFKA_FILE
  echo "Requires=network.target remote-fs.target" >> $KAFKA_FILE
  echo "After=network.target remote-fs.target nalms-zookeeper.service" >> $KAFKA_FILE

  echo "" >> $KAFKA_FILE

  echo "[Service]"  >> $KAFKA_FILE
  echo "Type=simple" >> $KAFKA_FILE
  echo "Environment=JAVA_HOME=${JAVA_HOME}" >> $KAFKA_FILE
  echo "Environment=LOG_DIR=${KAFKA_LOG_DIR}" >> $KAFKA_FILE
  echo "ExecStart=${KAFKA_TOP}/bin/kafka-server-start.sh ${NALMS_TOP}/config/${NALMS_ENV}_server.properties" >> $KAFKA_FILE
  echo "ExecStop=${KAFKA_TOP}/bin/kafka-server-stop.sh" >> $KAFKA_FILE

  echo "" >> $KAFKA_FILE

  echo "[Install]" >> $KAFKA_FILE
  echo "WantedBy=multi-user.target" >> $KAFKA_FILE

  if ! $DRYRUN ; then
    cp $NALMS_TOP/services/nalms-kafka.service /etc/systemd/system/nalms-kafka.service
  fi

fi

if (! $KAFKA_ONLY || ! $ELASTICSEARCH_ONLY); then

  # create zookeeper file
  ZOOKEEPER_FILE=$NALMS_TOP/services/nalms-zookeeper.service

  touch $ZOOKEEPER_FILE

  echo "# File /etc/systemd/system/nalms-zookeeper.service">> $ZOOKEEPER_FILE
  echo "# Generated from $NALMS_TOP/scripts/build-services.sh " >> $ZOOKEEPER_FILE
  echo "" >> $ZOOKEEPER_FILE
  echo "" >> $ZOOKEEPER_FILE


  echo "[Unit]" >> $ZOOKEEPER_FILE
  echo "Description=Apache Zookeeper server (Kafka)" >> $ZOOKEEPER_FILE
  echo "Documentation=http://zookeeper.apache.org" >> $ZOOKEEPER_FILE
  echo "Requires=network.target remote-fs.target" >> $ZOOKEEPER_FILE
  echo "After=network.target remote-fs.target" >> $ZOOKEEPER_FILE
  echo "SuccessExitStatus=143"  >>  $ZOOKEEPER_FILE


  echo "" >> $ZOOKEEPER_FILE

  echo "[Service]" >> $ZOOKEEPER_FILE
  echo "Type=simple" >> $ZOOKEEPER_FILE
  echo "Environment=JAVA_HOME=${JAVA_HOME}" >> $ZOOKEEPER_FILE
  echo "Environment=LOG_DIR=${KAFKA_LOG_DIR}"  >> $ZOOKEEPER_FILE
  echo "ExecStart=${KAFKA_TOP}/bin/zookeeper-server-start.sh ${NALMS_TOP}/config/${NALMS_ENV}_zookeeper.properties" >> $ZOOKEEPER_FILE
  echo "ExecStop=${KAFKA_TOP}/bin/zookeeper-server-stop.sh" >> $ZOOKEEPER_FILE
  echo "SuccessExitStatus=143"  >> $ZOOKEEPER_FILE

  echo "" >> $ZOOKEEPER_FILE

  echo "[Install]" >> $ZOOKEEPER_FILE
  echo "WantedBy=multi-user.target" >> $ZOOKEEPER_FILE

  # copy zookeeper file
  if ! $DRYRUN; then
    cp $NALMS_TOP/services/nalms-zookeeper.service /etc/systemd/system/nalms-zookeeper.service
  fi
fi


if (! $ZOOKEEPER_ONLY || ! $KAFKA_ONLY); then
  # create elasticsearch file
  ELASTICSEARCH_FILE=$NALMS_TOP/services/nalms-elasticsearch.service

  echo "[Unit]" >> $ELASTICSEARCH_FILE
  echo "Description=Elasticsearch" >> $ELASTICSEARCH_FILE
  echo "Documentation=http://www.elastic.co" >> $ELASTICSEARCH_FILE
  echo "Wants=network-online.target" >> $ELASTICSEARCH_FILE
  echo "After=network-online.target" >> $ELASTICSEARCH_FILE

  echo "" >> $ELASTICSEARCH_FILE

  echo "[Service]" >> $ELASTICSEARCH_FILE
  echo "Environment=ES_HOME=${ELASTICSEARCH_TOP}" >> $ELASTICSEARCH_FILE
  echo "Environment=ES_PATH_CONF=${NALMS_TOP}/config/elasticsearch">> $ELASTICSEARCH_FILE
  echo "Environment=JAVA_HOME=${JAVA_HOME}" >> $ELASTICSEARCH_FILE
  echo "User=elasticsearch" >> $ELASTICSEARCH_FILE
  echo "Group=elasticsearch" >> $ELASTICSEARCH_FILE

  echo "" >> $ELASTICSEARCH_FILE


  echo "ExecStart=${ELASTICSEARCH_TOP}/bin/elasticsearch" >> $ELASTICSEARCH_FILE

  echo "" >> $ELASTICSEARCH_FILE

  echo "StandardOutput=journal" >> $ELASTICSEARCH_FILE
  echo "StandardError=inherit" >> $ELASTICSEARCH_FILE
  echo "LimitNOFILE=65536" >> $ELASTICSEARCH_FILE
  echo "LimitMEMLOCK=infinity" >> $ELASTICSEARCH_FILE
  echo "TimeoutStopSec=0" >> $ELASTICSEARCH_FILE
  echo "KillSignal=SIGTERM" >> $ELASTICSEARCH_FILE
  echo "SendSIGKILL=no" >> $ELASTICSEARCH_FILE
  echo "SuccessExitStatus=143" >> $ELASTICSEARCH_FILE

  echo "" >> $ELASTICSEARCH_FILE

  echo "[Install]" >> $ELASTICSEARCH_FILE
  echo "WantedBy=multi-user.target" >> $ELASTICSEARCH_FILE


  # elasticsearch requires a designated user
  # check that it exists and update permissions
  if ! id "elasticsearch" &>/dev/null && ! $DRYRUN; then
    useradd elasticsearch
    chown -R elasticsearch:elasticsearch $ELASTICSEARCH_LOG_DIR $ELASTICSEARCH_DATA_DIR
  fi


  # copy elasticsearch file
  if ! $DRYRUN; then
  cp $NALMS_TOP/services/nalms-elasticsearch.service /etc/systemd/system/nalms-elasticsearch.service
  fi
fi