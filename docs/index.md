# Next ALarM Sytem

NALMS is an alarm system application designed for availability, integrability, and extensibility. The NALMS development was driven by SLAC's efforts to replace the Alarm Handler, due for deprecation as a Motif-based application, and to introduce process improvements addressing hierarchy implementation overhead, limited operator engagement, and operator display integration.

# Docker

This repository is packaged with tools for Docker based deployment. There are several reasons containerization is an advantageous:  

* The Kafka brokers may be straighforwardly deployed and the cluster scaled. Configurations are therefore transferable and port exposures may be configured directly on the Docker deployment.
* Contained applications may run in parallel, facilitating blue/green deployment workflows. 

This docker application consists of the following containers:

* Zookeeper
* Kafka
* Phoebus Alarm Server
* Phoebus Alarm Logger
* Elasticsearch
* Grafana
* An Example IOC
* Cruise Control

Docker-compose may be used to run a packaged example with all components.
```
$ docker-compose up
```

Once running, the cruise control dashboard is available at http://localhost:9090, and the grafana alarm log dashboard is available at http://localhost:3000. To access the alarm log dashboard, log in using the grafana default accounts, username: admin, password: admin. The alarm logger may need to be restarted if using docker compose, due to a slight delay in the alarm server startup. 

Operations on the IOC can be performed by running caputs/cagets after attaching to the running container. 


# Configuration

This sections includes an attempt to address configuration items, giving some insight to the service configuration within the Dockerized components and their Docker arguments.

An attempt has been made to sufficiently abstract scripts for deployments based on environment variables and a full descriptions of a complete environment for deployment is giving in the [CLI](cli.md) documentation.

Below, each component is outline with respect to Docker configuration variables and configuration file structure. For a full resource of available configurations, the source documentation will be linked. 

## Elasticsearch

### Configuration

The Elasticsearch configuration consists of three main files:

* elasticsearch.yml for configuring Elasticsearch
* jvm.options for configuring Elasticsearch JVM settings
* log4j2.properties for configuring Elasticsearch logging

A reference for elasticsearch configuration files can be found [here](https://www.elastic.co/guide/en/elasticsearch/reference/6.8/settings.html).

In order for the Elasticsearch fields to be properly formatted, a template matching the topic scheme must be posted to the server. These may be versioned and are automatically applied to newly created indices. The initial script for templating NALMS topics is hosted in `elasticsearch/scripts/create_alarm_template.sh`. This template has been taken from the Phoebus source [examples](https://github.com/ControlSystemStudio/phoebus/blob/master/app/alarm/examples/create_alarm_topics.sh).

### Docker 
The elasticsearch node may be configured using an exposed port, node specific variables, and Kafka networking variables. Because this is a single node deployment,  `single-node` deployment is used. Java options may be specifified using the `ES_JAVA_OPTS` variable. 

The following Docker run command will lauch an Elasticsearch node reachable on host machine port 9200.

```
docker run \
    -e node.name=node01 \
    -e cluster.name=es-cluster-7 \
    -e discovery.type=single-node \
    -e ES_JAVA_OPTS="-Xms128m -Xmx128m" \
    -e ES_HOST=localhost \
    -e ES_PORT=9200 \
    -p "9200:9200" \
    --name nalms_elasticsearch \
    -d jgarrahan/nalms-elasticsearch:latest
```
## Zookeeper

### Configuration
At present, Zookeeper is launched using the default settings. For more sophisticated deployments, a configuration with mounted configuration files would be preferable.

### Docker
The following command will run Zookeeper accessible on the host machine at port 2181:

```
docker run -p "2181:2181" --name nalms_zookeeper -d jgarrahan/nalms-zookeeper
```

## Kafka

### Configuration
This file is used to configure general properties of a Kafka broker including replication settings and communications protocols. Listeners are defined with respect to configured protocols and binding ports. Advertised listeners are configured with respect to configured protocol and exposed ports. 

The `replication.factor` must be appropriately modified based off of the number of nodes in the deployment. A single broker deployment would require `replication.factor` set to 1. A cluster deployment can accomodate a larger replication factor across the cluster and this file must be modified for the purpose. 

Networking configurations for SSL/TLS configuration settings are described [here](networking.md).

Also defined in this file is the reference to the zookeeper docker image resource:
```
zookeeper.connect=zookeeper:2181
```

Certain configurations options may be defined on the topic level. In `phoebus-alarm-server/cli/commands/create-kafka-indices`, state topics are created with partitions and replications dependent on the cluster settings. After initial creation, the Talk and Command topics are modified to use the deletion cleanup policy with set retention time. At present, the Talk command unused. The create-kafka-indices command is automatically executed during alarm server docker image startup.

There are many other settings pertaining to the optimization of the cluster and must be determined by traffic demands. A full catalog of available configurations may be found in the documentation, [here](https://kafka.apache.org/documentation/).

### Docker

The Kafka broker images require the definition of Kafka networking variables, `KAFKA_ADVERTISED_LISTENERS`, `KAFKA_LISTENER_SECURITY_PROTOCOL_MAP`, `KAFKA_LISTENERS`, `ZOOKEEPER_CONNECT` and must be provided a numeric broker ID. The image must be provisioned with an 8g memory allocation. Additional optimizations may be performed using the Docker image [configurations](https://docs.docker.com/config/containers/resource_constraints/). A configuration file must be mounted to `/opt/kafka/server.properties` for the image, with properly formatted networking and replication numbers. An example server configuration is given in `examples/demo/config/server.properties`.

An example run command for the Kafka docker image is given below:

```
docker run -m 8g  \
  -e KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://${HOST_IP}:9092,CONNECTIONS_FROM_HOST://${HOST_IP}:19092 \
  -e KAFKA_LISTENER_SECURITY_PROTOCOL_MAP=PLAINTEXT:PLAINTEXT,CONNECTIONS_FROM_HOST:PLAINTEXT \
  -e KAFKA_LISTENERS=PLAINTEXT://${HOST_IP}:9092,CONNECTIONS_FROM_HOST://0.0.0.0:19092 \
  -e ZOOKEEPER_CONNECT=${HOST_IP}:2182 \
  -e BROKER_ID=0 \
  -v "/full/path/to/examples/demo/config/server.properties:/opt/kafka/server.properties" \
  -p "19092:19092" \
  --name nalms_kafka_0 \
  -d jgarrahan/nalms-kafka:latest
```

Instructions on configuring the Docker image with SSL are given in [networking](networking.md).


## Phoebus Alarm Server

### Configuration

The Phoebus alarm server configuration properties file defines the EPICS configuration and Elasticsearch host configuration. A full preference list can be found in the CS-Studio [documentation](https://control-system-studio.readthedocs.io/en/latest/preference_properties.html).

Of particular importance are the EPICS, Kakfa, and Elasticsearch properties. The Alarm Server requires:

```ini
# Channel access settings
org.phoebus.pv.ca/addr_list=localhost:5064
org.phoebus.pv.ca/server_port=5064
org.phoebus.pv.ca/repeater_port=5065
org.phoebus.pv.ca/auto_addr_list=no

# pvAccess settings

# Kafka
org.phoebus.applications.alarm/server=kafka:19092
```

### Docker

The Phoebus alarm server requires mounting of the configuration file with the Docker volume option and the definition of environment variables indicating Kafka networking address, whether the alarm IOC is to be used, and the EPICS configuration settings to access the alarm and variable iocs. The Docker run command for the packaged example is given below:

```
$ docker run -v /full/path/to/examples/demo/demo.xml:/tmp/nalms/Demo.xml \
  --name nalms_server_Demo \
  -e ALARM_IOC=true \
  -e KAFKA_BOOTSTRAP=${HOST_IP}:19092 \
  -e EPICS_CA_ADDR_LIST=$HOST_IP \
  -e EPICS_CA_SERVER_PORT=5054 \
  -e EPICS_CA_REPEATER_PORT=5055 \
  -d -t jgarrahan/nalms-phoebus-alarm-server:latest start-server Demo /tmp/nalms/demo.xml
```

The configuration file must be mounted to `/tmp/nalms/${CONFIG_NAME}, for internal identification.

## Phoebus Alarm Logger

### Configuration

The alarm logger properties file requires the definition of Elasticsearch and Kafka networking environment variables. The templated file used by the image is hosted at `phoebus-alarm-logger/logger.properties`.  

```ini
# location of elastic node/s
es_host=localhost
es_port=9200

# Kafka server location
bootstrap.servers=localhost:9092
```
Additionally, logging for the logger is configurable and defined in `phoebus-alarm-server/logger.properties`.  

### Docker

The Phoebus alarm logger requires the mounting of the configuration file with the Docker volume option and the definition of Elasticsearch networking variables. The Docker run command for the packaged example is given below:

```
docker run -v /full/path/to/examples/demo/demo.xml:/tmp/nalms/Demo.xml \
  -e ES_HOST=${HOST_IP} \
  -e ES_PORT=9200 \ 
  -e BOOTSTRAP_SERVERS=${HOST_IP}:19092 \
  --name nalms_logger_Demo \
  -d jgarrahan/nalms-phoebus-alarm-logger:latest start-logger Demo /tmp/nalms/Demo.xml
```
The configuration file must be mounted to `/tmp/nalms/${CONFIG_NAME}, for internal identification.

## Phoebus Client

### Configuration

Like the alarm server and logger, the client also accepts a properties file that defines networking. 

### Docker

The Phoebus Client must be configured with a DISPLAY variable for X forwarding and mounted X11 volumes. Additionally, the client requires the definition of both EPICS, Elasticsearch, and Kafka networking variables.  The Docker run command for the packaged example is given below:

```
$ docker run -e DISPLAY=host.docker.internal:0 -v /tmp/.X11-unix:/tmp/.X11-unix -m 2g \
  -e EPICS_CA_ADDR_LIST=${HOST_IP} \
  -e EPICS_CA_SERVER_PORT=5064 \
  -e EPICS_CA_REPEATER_PORT=5065 \
  -e ES_HOST=${HOST_IP} \
  -e ES_PORT=9200 \
  -e CONFIG_NAME=Demo \
  -e KAFKA_HOST=${HOST_IP} \
  -e KAFKA_PORT=19092 \
  --name nalms-phoebus-client \
  -d jgarrahan/nalms-phoebus-client:latest
```

## Grafana

### Configuration

Grafana datasources and dashboards may be programatically provisioned as outlined [here](https://grafana.com/docs/grafana/latest/administration/provisioning/). Elasticsearch datasources define an index and networking variables. 

For the purpose of NALMS, the Grafana image automatically generates the provisioned dashboards and datasources depending on configured Elasticsearch network settings and provided configurations using templates. The dashboard template is hosted at `grafana/dashboards/alarm_logs_dashboard.json` and the datsource template is generated from the `grafana/scripts/create-datasource-file.sh` bash script executed on startup.

### Docker

The Grafana image automatically generates the provisioned dashboards and datasources depending on configured Elasticsearch network settings and provided configurations. The Docker run command for the packaged example is given below:

```
docker run \
    -p "3000:3000" \
    -e ES_HOST=${HOST_IP} \
    -e ES_PORT=5064 \
    -e CONFIG_NAME=Demo \
    --name nalms_grafana \
    -d jgarrahan/nalms-grafana:latest
```

The Grafana dashboards are then reachable at localhost:3000 in browser.

## Cruise Control

### Configuration

The `cruise-control/cruisecontrol.properties` file dictates the behavior of the cruise control server, allowing definition of relevant thresholds and networking nodes. The `jgarrahan/nalms-cruise-control` image performs interpolation on this file in order to pass the relevant environment variables. 


### Docker


The Cruise Control Image requires definition of bootstrap servers and Zookeeper addresses.  The Docker run command for the packaged example is given below:

```
docker run \
    -e BOOTSTRAP_SERVERS=${HOST_IP}:5064 \
    -e ZOOKEEPER_CONNECT=${HOST_IP}:2181 \
    --name nalms_cruise_control \
    -p "9090:9090" -d jgarrahan/nalms-cruise-control:latest
```

The Cruise Control UI is then available in browser at localhost:9090.