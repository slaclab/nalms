#!/bin/sh
# Author: Jacqueline Garrahan
#
# This script creates service files using active NALMS configuration.
# Requires sudo
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
  echo "NALMS_ENV is not set."
  exit 0
fi

if [[ -z "$JAVA_HOME" ]]; then
  echo "JAVA_HOME is not set."
  exit 0
fi

# create logging dir
if [[ ! -d "/var/log/nalms" && $DRYRUN != true ]]; then
    mkdir /var/log/nalms
fi

# check ELASTICSEARCH_TOP is set
if [[ ! -d "$ELASTICSEARCH_TOP" ]]; then
  echo "ELASTICSEARCH_TOP is incorrectly configured."
  echo "\$ELASTICSEARCH_TOP = ${ELASTICSEARCH_TOP}"
  exit 0
fi

# remove old artifacts
if [ -f "$NALMS_TOP/services/nalms-kafka.service" ]; then
    rm $NALMS_TOP/services/nalms-kafka.service
fi

if [ -f "$NALMS_TOP/services/nalms-zookeeper.service" ]; then
    rm $NALMS_TOP/services/nalms-zookeeper.service
fi

if [ -f "$NALMS_TOP/services/nalms-elasticsearch.service" ]; then
    rm $NALMS_TOP/services/nalms-elasticsearch.service
fi


# if not a dry run, remove relevant systemd files
if [ $DRYRUN != true ]; then
  if [ -f "/etc/systemd/system/nalms-kafka.service" ]; then
      rm /etc/systemd/system/nalms-kafka.service
  fi

  if [ -f "/etc/systemd/system/nalms-zookeeper.service" ]; then
      rm /etc/systemd/system/nalms-zookeeper.service
  fi

  if [ -f "/etc/systemd/system/nalms-elasticsearch.service" ]; then
      rm /etc/systemd/system/nalms-elasticsearch.service
  fi
fi 


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
#User=DESIRED_USER
#Group=DESIRED_GROUP
echo "Environment=JAVA_HOME=${JAVA_HOME}" >> $KAFKA_FILE
echo "Environment=LOG_DIR=${KAFKA_LOG_DIR}" >> $KAFKA_FILE
echo "ExecStart=${KAFKA_TOP}/bin/kafka-server-start.sh ${NALMS_TOP}/config/${NALMS_ENV}_server.properties" >> $KAFKA_FILE
echo "ExecStop=${KAFKA_TOP}/bin/kafka-server-stop.sh" >> $KAFKA_FILE

echo "" >> $KAFKA_FILE

echo "[Install]" >> $KAFKA_FILE
echo "WantedBy=multi-user.target" >> $KAFKA_FILE

if [ $DRYRUN != true ]; then
  cp $NALMS_TOP/services/nalms-kafka.service /etc/systemd/system/nalms-kafka.service
fi

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
if [ $DRYRUN != true ]; then
  cp $NALMS_TOP/services/nalms-zookeeper.service /etc/systemd/system/nalms-zookeeper.service
fi

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
echo "Environment=JAVA_HOME=${JAVA_HOME}" >> $ELASTICSEARCH_FILE

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

# copy elasticsearch file
if [ $DRYRUN != true ]; then
 cp $NALMS_TOP/services/nalms-elasticsearch.service /etc/systemd/system/nalms-elasticsearch.service
fi