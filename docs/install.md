# Installation

The NALMS system has been written for deployment as a set of Docker images, allowing for the distribution of services across network hosts configurable via environment variables and mounted volumes. In the case that containers aren't favorable, the Dockerfiles inside this repository should serve as a guide for these deployments and component source materials should be consulted for installation details.

The current NALMS iteration consists of the following Dockerhub hosted containers:


### jgarrahan/nalms-zookeeper
* Zookeeper 3.5.9

### jgarrahan/nalms-kafka
* Kafka 2.7.0 configured with cruise-control metrics reporter 
* SSL configurable (see [networking](networking.md))

### jgarrahan/nalms-phoebus-alarm-server
* Phoebus alarm server (built from HEAD of main branch)
* Python script for monitoring Kafka topics updating [alarm IOC](epics_integration.md) with bypasses and acknowledgments

### jgarrahan/nalms-phoebus-alarm-logger
* Phoebus alarm logger (built from HEAD of main branch)

### jgarrahan/nalms-elasticsearch
* Elasticsearch service (6.8.16)
* Script for templating of Alarm indices

### jgarrahan/nalms-grafana
* Grafana service (7.3.0-beta1)
* Template Grafana dashboard for any configuration
* Can be launched with multiple configurations as a comma separated list
* Automatic generation of elasticsearch datasources based on network configs and configuration names

### jgarrahan/nalms-cruise-control
* LinkendIn's Cruise Control monitor for Kafka clusters (built from HEAD of branch migrate_to_kafka_2_5, which is compatible with Kafka 2.7.0) 
* Cruise Control web UI

### jgarrahan/nalms-phoebus-client
* CS-Studio's Phoebus client tool built for use with only alarm services

## Download Images
Images may be downloaded from Dockerhub on a machine with Docker installed using the command (nalms-kafka here for example):
```
$ docker pull jgarrahan/nalms-kafka:latest
```
## Deploy
After pulling the latest image, it is recommended to use the [CLI](cli.md) for launching of each image as checks for necessary environment variables are built in to the interface. A full description of each image configuration is described [here](configuration.md).

