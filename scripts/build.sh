#!/bin/sh
# Author: Jacqueline Garrahan
#
# This script creates build artifacts for nalms
#
# To build a subset of services, you can use tag --elasticsearch, --kafka, --zookeeper
# Generated files will be stored in /tmp/nalms/
#
# Copyright @2021 SLAC National Accelerator Laboratory

if [ "$1" == "-h" ]; then
  echo "Usage: build.sh [--zookeeper] [--elasticsearch] [--kafka]"
  exit 0
fi

BUILD_ELASTICSEARCH=0
BUILD_KAFKA=0
BUILD_ZOOKEEPER=0
EXIT=0

# Java home
if [[ ! -d "${JAVA_HOME}" ]] ; then
    echo "JAVA_HOME incorrectly set."
    echo "\$JAVA_HOME = ${JAVA_HOME}"
    EXIT=1
fi


# if no args provided, build all
if [ $# -eq 0 ]; then
    BUILD_ELASTICSEARCH=1
    BUILD_KAFKA=1
    BUILD_ZOOKEEPER=1

    # check environment
    if [[ -z "${KAFKA_LOG_DIR}" ]] ; then
        echo "KAFKA_LOG_DIR incorrectly set."
        echo "\$KAFKA_LOG_DIR = ${KAFKA_LOG_DIR}"
        EXIT=1
    fi

    if [[ ! -d "${KAFKA_TOP}" ]] ; then
        echo "KAFKA_TOP incorrectly set."
        echo "\$KAFKA_TOP = ${KAFKA_TOP}"
        EXIT=1
    fi

    if [[ ! -f "${KAFKA_PROPERTIES}" ]] ; then
        echo "KAFKA_PROPERTIES incorrectly set."
        echo "\$KAFKA_PROPERTIES = ${KAFKA_PROPERTIES}"
        EXIT=1
    fi

    if [[ ! -f "${ZOOKEEPER_PROPERTIES}" ]] ; then
        echo "ZOOKEEPER_PROPERTIES incorrectly set."
        echo "\$ZOOKEEPER_PROPERTIES = ${ZOOKEEPER_PROPERTIES}"
        EXIT=1
    fi

    if [[ -z "${ELASTICSEARCH_LOG_DIR}" ]] ; then
        echo "ELASTICSEARCH_LOG_DIR incorrectly set."
        echo "\$ELASTICSEARCH_LOG_DIR = ${ELASTICSEARCH_LOG_DIR}"
        EXIT=1
    fi

    if [[ -z "${ELASTICSEARCH_DATA_DIR}" ]] ; then
        echo "ELASTICSEARCH_DATA_DIR incorrectly set."
        echo "\$ELASTICSEARCH_DATA_DIR = ${ELASTICSEARCH_DATA_DIR}"
        EXIT=1
    fi

    if [[ ! -d "${NALMS_TOP}" ]]; then
        echo "NALMS_TOP incorrectly set correctly."
        echo "\$NALMS_TOP = ${NALMS_TOP}"
        EXIT=1
    fi

    if [[ ! -d "${ELASTICSEARCH_TOP}" ]] ; then
        echo "ELASTICSEARCH_TOP incorrectly set."
        echo "\$ELASTICSEARCH_TOP = ${ELASTICSEARCH_TOP}"
        EXIT=1
    fi

fi


# parse optional builds
while test $# -gt 0
do
    case "$1" in
        --elasticsearch) 
            BUILD_ELASTICSEARCH=1
            if [[ -z "${ELASTICSEARCH_LOG_DIR}" ]] ; then
                echo "ELASTICSEARCH_LOG_DIR incorrectly set."
                echo "\$ELASTICSEARCH_LOG_DIR = ${ELASTICSEARCH_LOG_DIR}"
                EXIT=1
            fi

            if [[ -z "${ELASTICSEARCH_DATA_DIR}" ]] ; then
                echo "ELASTICSEARCH_DATA_DIR incorrectly set."
                echo "\$ELASTICSEARCH_DATA_DIR = ${ELASTICSEARCH_DATA_DIR}"
                EXIT=1
            fi

            if [[ ! -d "${NALMS_TOP}" ]]; then
                echo "NALMS_TOP incorrectly set correctly."
                echo "\$NALMS_TOP = ${NALMS_TOP}"
                EXIT=1
            fi

            if [[ ! -d "${ELASTICSEARCH_TOP}" ]] ; then
                echo "ELASTICSEARCH_TOP incorrectly set."
                echo "\$ELASTICSEARCH_TOP = ${ELASTICSEARCH_TOP}"
                EXIT=1
            fi
            ;;
        --zookeeper) 
            BUILD_ZOOKEEPER=1
            if [[ -z "${KAKFA_LOG_DIR}" ]] ; then
                echo "KAFKA_LOG_DIR incorrectly set."
                echo "\$KAFKA_LOG_DIR = ${KAFKA_LOG_DIR}"
                EXIT=1
            fi

            if [[ ! -d "${KAKFA_TOP}" ]] ; then
                echo "KAFKA_TOP incorrectly set."
                echo "\$KAFKA_TOP = ${KAFKA_TOP}"
                EXIT=1
            fi

            if [[ ! -f "${ZOOKEEPER_PROPERTIES}" ]] ; then
                echo "ZOOKEEPER_PROPERTIES incorrectly set."
                echo "\$ZOOKEEPER_PROPERTIES = ${ZOOKEEPER_PROPERTIES}"
                EXIT=1
            fi
            ;;
        --kafka) 
            BUILD_KAFKA=1
            if [[ -z "${KAKFA_LOG_DIR}" ]] ; then
                echo "KAFKA_LOG_DIR incorrectly set."
                echo "\$KAFKA_LOG_DIR = ${KAFKA_LOG_DIR}"
                EXIT=1
            fi

            if [[ ! -d "${KAKFA_TOP}" ]] ; then
                echo "KAFKA_TOP incorrectly set."
                echo "\$KAFKA_TOP = ${KAFKA_TOP}"
                EXIT=1
            fi

            if [[ ! -f "${KAFKA_PROPERTIES}" ]] ; then
                echo "KAFKA_PROPERTIES incorrectly set."
                echo "\$KAFKA_PROPERTIES = ${KAFKA_PROPERTIES}"
                EXIT=1
            fi
            ;;
        "") echo "here"
    esac
    shift
done


# exit with failure
if [[ $EXIT -eq 1 ]]; then
    exit 1
fi

# create nalms tmp dir
if [[ ! -d "/tmp/nalms" ]]; then
  mkdir "/tmp/nalms"
fi

# remove old artifacts
if [[ -f "/tmp/nalms/nalms-kafka.service" && $BUILD_KAFKA -eq 1 ]]; then
    rm /tmp/nalms/nalms-kafka.service
fi

if [[ -f "/tmp/nalms/nalms-zookeeper.service" && $BUILD_ZOOKEEPER -eq 1 ]]; then
    rm /tmp/nalms/nalms-zookeeper.service
fi

if [[ -f "/tmp/nalms/nalms-elasticsearch.service" && $BUILD_ELASTICSEARCH -eq 1 ]]; then
    rm /tmp/nalms/nalms-elasticsearch.service
fi


# Build kafka service file
if [[ $BUILD_KAFKA -eq 1 ]]; then

    # create kafka file
    KAFKA_FILE=/tmp/nalms/nalms-kafka.service

    touch $KAFKA_FILE

    echo "# File /etc/systemd/system/nalms-kafka.service">> $KAFKA_FILE
    echo "# Generated from $NALMS_TOP/scripts/build.sh " >> $KAFKA_FILE
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
    echo "ExecStart=${KAFKA_TOP}/bin/kafka-server-start.sh ${KAFKA_PROPERTIES}" >> $KAFKA_FILE
    echo "ExecStop=${KAFKA_TOP}/bin/kafka-server-stop.sh" >> $KAFKA_FILE

    echo "" >> $KAFKA_FILE

    echo "[Install]" >> $KAFKA_FILE
    echo "WantedBy=multi-user.target" >> $KAFKA_FILE

fi

# build zookeeper service file
if [[ $BUILD_ZOOKEEPER -eq 1 ]]; then

    # create zookeeper file
    ZOOKEEPER_FILE=/tmp/nalms/nalms-zookeeper.service

    touch $ZOOKEEPER_FILE

    echo "# File /etc/systemd/system/nalms-zookeeper.service">> $ZOOKEEPER_FILE
    echo "# Generated from $NALMS_TOP/scripts/build.sh " >> $ZOOKEEPER_FILE
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
    echo "ExecStart=${KAFKA_TOP}/bin/zookeeper-server-start.sh ${ZOOKEEPER_PROPERTIES}" >> $ZOOKEEPER_FILE
    echo "ExecStop=${KAFKA_TOP}/bin/zookeeper-server-stop.sh" >> $ZOOKEEPER_FILE
    echo "SuccessExitStatus=143"  >> $ZOOKEEPER_FILE

    echo "" >> $ZOOKEEPER_FILE

    echo "[Install]" >> $ZOOKEEPER_FILE
    echo "WantedBy=multi-user.target" >> $ZOOKEEPER_FILE

fi

# build elasticsearch service file
if [[ $BUILD_ELASTICSEARCH -eq 1 ]]; then

    # create elasticsearch file
    ELASTICSEARCH_FILE=/tmp/nalms/nalms-elasticsearch.service

    echo "[Unit]" >> $ELASTICSEARCH_FILE
    echo "Description=Elasticsearch" >> $ELASTICSEARCH_FILE
    echo "Documentation=http://www.elastic.co" >> $ELASTICSEARCH_FILE
    echo "Wants=network-online.target" >> $ELASTICSEARCH_FILE
    echo "After=network-online.target" >> $ELASTICSEARCH_FILE

    echo "" >> $ELASTICSEARCH_FILE

    echo "[Service]" >> $ELASTICSEARCH_FILE
    echo "Environment=ES_HOME=${ELASTICSEARCH_TOP}" >> $ELASTICSEARCH_FILE
    echo "Environment=ES_PATH_CONF=${NALMS_TOP}/config/elasticsearch" >> $ELASTICSEARCH_FILE
    echo "Environment=ELASTICSEARCH_DATA_DIR=${ELASTICSEARCH_DATA_DIR}" >> $ELASTICSEARCH_FILE
    echo "Environment=ELASTICSEARCH_LOG_DIR=${ELASTICSEARCH_LOG_DIR}" >> $ELASTICSEARCH_FILE
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

fi
