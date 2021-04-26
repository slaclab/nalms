# NALMS

# Environment variables
NALMS_TOP  
KAFKA_TOP  
ALARM_SERVER_PATH  
KAFKA_LOG_PATH  
ZOOKEEPER_LOG_PATH  
ELASTICSEARCH_PATH  
ALARM_LOGGER_PATH  
ALARM_CONFIG_LOGGER_PATH  
EPICS_CA_AUTO_ADDR_LIST  
EPICS_CA_ADDR_LIST  
EPICS_CA_REPEATER_PORT  
EPICS_CA_SERVER_PORT  
NALMS_TOP   
ZOOKEEPER_HOST  
LOG_PATH   
JAVA_HOME  
NALMS_ENV  
KAFKA_BOOTSTRAP  

# Services
Kafka, Zookeeper, and Elasticsearch will all be installed as systemd services. These may be started/stopped using:

Kafka
sudo systemctl start kafka.service
sudo systemctl stop kafka.service

Zookeeper
sudo systemctl start zookeeper.service
sudo systemctl stop zookeeper.service

Elasticsearch
sudo systemctl start elasticsearch.service
sudo systemctl stop elasticsearch.service