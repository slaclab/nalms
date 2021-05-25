#!/bin/sh
# Author: Jacqueline Garrahan
#
# This script install the nalms package
#
# To install a subset of services, you can use tag --elasticsearch, --kafka, --zookeeper
# Requires sudo
#
# Copyright @2021 SLAC National Accelerator Laboratory

if [ "$1" == "-h" ]; then
  echo "Usage: install.sh [--zookeeper] [--elasticsearch] [--kafka]"
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


# execute build and check completion
if ! sh ./build.sh; then
    echo "Unable to install."
    exit 1
fi


# create logging dir
if [[ ! -d "/var/log/nalms" ]]; then
    mkdir /var/log/nalms
fi


# install zookeeper
if [[ $BUILD_ZOOKEEPER -eq 1 ]]; then

    # remove existing nalms-zookeeper service file
    if [[ -f "/etc/systemd/system/nalms-zookeeper.service" ]]; then
        rm /etc/systemd/system/nalms-zookeeper.service
    fi

    # stop in the case that zookeeper running
    systemctl stop nalms-zookeeper.service

    cp /tmp/nalms/nalms-zookeeper.service /etc/systemd/system/nalms-zookeeper.service

    # reload daemon
    systemctl daemon-reload

    # enable service
    systemctl enable nalms-zookeeper.service

    # start service
    systemctl start nalms-zookeeper.service


fi


# install kafka
if [[ $BUILD_KAFKA -eq 1 ]]; then

    # remove kafka logs
    if [[ ! -d $KAFKA_LOG_DIR ]]; then
        mkdir $KAFKA_LOG_DIR
    else
        rm -r $KAFKA_LOG_DIR
        mkdir $KAFKA_LOG_DIR
    fi


    # remove existing nalms-kafka service file
    if [[ -f "/etc/systemd/system/nalms-kafka.service" ]]; then
        rm /etc/systemd/system/nalms-kafka.service
    fi

    # stop in the case that kafka running
    systemctl stop nalms-kafka.service

    cp /tmp/nalms/nalms-kafka.service /etc/systemd/system/nalms-kafka.service

    # reload daemon
    systemctl daemon-reload

    # enable service
    systemctl enable nalms-kafka.service

    # start service
    systemctl start nalms-kafka.service

fi


# install elasticsearch
if [[ $BUILD_ELASTICSEARCH -eq 1 ]]; then

    # remove existing nalms-elasticsearch service file
    if [[ -f "/etc/systemd/system/nalms-elasticsearch.service" ]]; then
        rm /etc/systemd/system/nalms-elasticsearch.service
    fi

    # create a designated elasticearch user
    if ! id "elasticsearch" &>/dev/null ;  then
        useradd elasticsearch
    fi

    # change ownership of log and data dir
    if [[ ! -d $ELASTICSEARCH_LOG_DIR ]]; then
        mkdir $ELASTICSEARCH_LOG_DIR
        mkdir $ELASTICSEARCH_LOG_DIR/logs
    else
        rm -r $ELASTICSEARCH_LOG_DIR
        mkdir $ELASTICSEARCH_LOG_DIR
        mkdir $ELASTICSEARCH_LOG_DIR/logs
    fi

    if [[ ! -d $ELASTICSEARCH_DATA_DIR ]]; then
        mkdir $ELASTICSEARCH_DATA_DIR
    else 
        rm -r $ELASTICSEARCH_DATA_DIR
        mkdir $ELASTICSEARCH_DATA_DIR
    fi


    chown -R elasticsearch:elasticsearch $ELASTICSEARCH_LOG_DIR $ELASTICSEARCH_DATA_DIR

    # stop in the case that elasticsearch running
    systemctl stop nalms-elasticsearch.service

    cp /tmp/nalms/nalms-elasticsearch.service /etc/systemd/system/nalms-elasticsearch.service

    # reload daemon
    systemctl daemon-reload

    # enable service
    systemctl enable nalms-elasticsearch.service

    # start service
    systemctl start nalms-elasticsearch.service

    # create alarm template
    #sh create_alarm_template.sh

fi



# create kafka log dir?
# create tmux user
