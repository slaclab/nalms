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
* Grafana service (7.5.3)
* Template Grafana dashboard for any configuration
* Can be launched with multiple configurations as a comma separated list
* Automatic generation of elasticsearch datasources based on network configs and configuration names

### jgarrahan/nalms-cruise-control
* LinkendIn's Cruise Control monitor for Kafka clusters (built from HEAD of branch migrate_to_kafka_2_5, which is compatible with Kafka 2.7.0) 
* Cruise Control web UI

## Download Images
Images may be downloaded from Dockerhub on a machine with Docker installed using the command (nalms-kafka here for example):
```
$ docker pull jgarrahan/nalms-kafka:latest
```

## Client installation

At present, we will build the client from the HEAD of the main branch of the Phoebus client hosted on Github.



Requirements:
* OpenJDK 11.0.2
* Maven == 3.6.0
* Git == 1.8.3.1

### Installation: 
1. Set `$JAVA_HOME`, `$MAVEN_HOME`, and `$NALMS_HOME`. Then update the path:
```
$ export PATH=$JAVA_HOME/bin:$PATH
$ export PATH=$MAVEN_HOME/bin:$PATH
```
Note: In afs, JAVA_HOME=${PACKAGE_TOP}/java/jdk-11.0.2, MAVEN_HOME=${PACKAGE_TOP}/maven/3.6.0, and NALMS_TOP=${PACKAGE_TOP}/nalms/current.

3. `cd` into installation directory
4. Get Phoebus repository
```
$ git clone https://github.com/ControlSystemStudio/phoebus.git
$ cd phoebus 
```
5. Now replace the existing product pom file with that packaged by NALMS:
``` 
$ rm phoebus-product/pom.xml
$ mv $NALMS_HOME/phoebus-client/pom.xml phoebus-product/pom.xml 
```
6. Install the Phoebus client:
```
$ mvn install -pl phoebus-product -am
```

Define $NALMS_CLIENT_JAR in appropriate environment file.

## Deploy
After pulling the latest image, it is recommended to use the [CLI](cli.md) for launching of each image as checks for necessary environment variables are built in to the interface. A full description of each image configuration is described [here](configuration.md).

## Configuration

This sections includes an attempt to address configuration items, giving some insight to the service configuration within the Dockerized components and their Docker arguments.

An attempt has been made to sufficiently abstract scripts for deployments based on environment variables and a full descriptions of a complete environment for deployment is giving in the [CLI](cli.md) documentation.

Below, each component is outline with respect to Docker configuration variables and configuration file structure. For a full resource of available configurations, the source documentation will be linked. 

### Elasticsearch

#### Configuration

The Elasticsearch configuration consists of three main files:

* elasticsearch.yml for configuring Elasticsearch
* jvm.options for configuring Elasticsearch JVM settings
* log4j2.properties for configuring Elasticsearch logging

A reference for elasticsearch configuration files can be found [here](https://www.elastic.co/guide/en/elasticsearch/reference/6.8/settings.html).

In order for the Elasticsearch fields to be properly formatted, a template matching the topic scheme must be posted to the server. These may be versioned and are automatically applied to newly created indices. The initial script for templating NALMS topics is hosted in `elasticsearch/scripts/create_alarm_template.sh`. This template has been taken from the Phoebus source [examples](https://github.com/ControlSystemStudio/phoebus/blob/master/app/alarm/examples/create_alarm_topics.sh).

#### Docker 
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
### Zookeeper

#### Configuration
At present, Zookeeper is launched using the default settings. For more sophisticated deployments, a configuration with mounted configuration files would be preferable.

#### Docker
The following command will run Zookeeper accessible on the host machine at port 2181:

```
docker run -p "2181:2181" --name nalms_zookeeper -d jgarrahan/nalms-zookeeper
```

### Kafka

#### Configuration
This file is used to configure general properties of a Kafka broker including replication settings and communications protocols. Listeners are defined with respect to configured protocols and binding ports. Advertised listeners are configured with respect to configured protocol and exposed ports. 

The `replication.factor` must be appropriately modified based off of the number of nodes in the deployment. A single broker deployment would require `replication.factor` set to 1. A cluster deployment can accomodate a larger replication factor across the cluster and this file must be modified for the purpose. 

Networking configurations for SSL/TLS configuration settings are described [here](networking.md).

Also defined in this file is the reference to the zookeeper docker image resource:
```
zookeeper.connect=zookeeper:2181
```

Certain configurations options may be defined on the topic level. In `phoebus-alarm-server/cli/commands/create-kafka-indices`, state topics are created with partitions and replications dependent on the cluster settings. After initial creation, the Talk and Command topics are modified to use the deletion cleanup policy with set retention time. At present, the Talk command unused. The create-kafka-indices command is automatically executed during alarm server docker image startup.

There are many other settings pertaining to the optimization of the cluster and must be determined by traffic demands. A full catalog of available configurations may be found in the documentation, [here](https://kafka.apache.org/documentation/).

#### Docker

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


### Phoebus Alarm Server

#### Configuration

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

The Phoebus alarm server requires mounting of the configuration file with the Docker volume option and the definition of environment variables indicating Kafka networking address, whether the alarm IOC is to be used, and the EPICS configuration settings to access the alarm and variable iocs.  The image supports the substitution of networking variables ($KAFKA_BOOTSTRAP and EPICS variables). Alternatively, these can be defined directly in the configuration file.

The Docker run command for the packaged example is given below:

```
$ docker run -v $CONFIG_FILE:/tmp/nalms/$CONFIG_NAME.xml \
  --name nalms_server_$CONFIG_NAME \
  -v "${NALMS_ALARM_SERVER_PROPERTIES}:/opt/nalms/config/alarm_server.properties" \
  -e ALARM_IOC=false \
  -e KAFKA_BOOTSTRAP="${NALMS_KAFKA_BOOTSTRAP}" \
  -e EPICS_CA_ADDR_LIST="${EPICS_CA_ADDR_LIST}" \
  -e EPICS_CA_SERVER_PORT="${EPICS_CA_SERVER_PORT}" \
  -e EPICS_CA_REPEATER_PORT="${EPICS_CA_REPEATER_PORT}" \
  -e EPICS_PVA_ADDR_LIST="${EPICS_PVA_ADDR_LIST}" \
  -e EPICS_PVA_SERVER_PORT="${EPICS_PVA_SERVER_PORT}" \
  -e EPICS_PVA_REPEATER_PORT="${EPICS_PVA_REPEATER_PORT}" \
  -e ALARM_SERVER_PROPERTIES="/opt/nalms/config/alarm_server.properties" \
  -d -t jgarrahan/nalms-phoebus-alarm-server:latest start-server $CONFIG_NAME /tmp/nalms/$CONFIG_NAME.xml
```

The configuration file must be mounted to `/tmp/nalms/${CONFIG_NAME}, for internal identification.

### Phoebus Alarm Logger

#### Configuration

The alarm logger properties file requires the definition of Elasticsearch and Kafka networking environment variables. The templated file used by the image is hosted at `phoebus-alarm-logger/logger.properties`.  

```ini
# location of elastic node/s
es_host=localhost
es_port=9200

# Kafka server location
bootstrap.servers=localhost:9092
```
Additionally, logging for the logger is configurable and defined in `phoebus-alarm-server/logger.properties`.  

#### Docker

The Phoebus alarm logger requires the mounting of the configuration file with the Docker volume option. The image supports the interpolation of networking variables $NALMS_ES_HOST, $NALMS_ES_PORT, and $NALMS_KAFKA_BOOTSTRAP in this file. The Docker run command for the packaged example is given below:

```
$ docker run -v $CONFIG_FILE:/tmp/nalms/$CONFIG_NAME.xml \
  -e ES_HOST="${NALMS_ES_HOST}" \
  -e ES_PORT="${NALMS_ES_PORT}" \
  -e BOOTSTRAP_SERVERS="${NALMS_KAFKA_BOOTSTRAP}" \
  -e ALARM_LOGGER_PROPERTIES="/opt/nalms/config/alarm_logger.properties" \
  -v "${ALARM_LOGGER_PROPERTIES}:/opt/nalms/config/alarm_logger.properties" \
  --name nalms_logger_$CONFIG_NAME \
  -d jgarrahan/nalms-phoebus-alarm-logger:latest start-logger $CONFIG_NAME /tmp/nalms/$CONFIG_NAME.xml
```
The configuration file must be mounted to `/tmp/nalms/${CONFIG_NAME}, for internal identification.

### Phoebus Client

#### Configuration

Like the alarm server and logger, the client also accepts a properties file that defines networking: [here](https://control-system-studio.readthedocs.io/en/latest/preference_properties.html).

### Grafana

#### Configuration

Grafana datasources and dashboards may be programatically provisioned as outlined [here](https://grafana.com/docs/grafana/latest/administration/provisioning/). Elasticsearch datasources define an index and networking variables. 

General Grafana configuration is described [here](https://grafana.com/docs/grafana/v7.5/administration/configuration/).

The dashboard template is hosted at `grafana/dashboards/alarm_logs_dashboard.json` and a configuration dashboard can be created using the `cli/nalms build-grafana-dashboard config-name` command. The datasource may be added to an existing datasource file using the  `cli/nalms add-grafana-datasource config-name` command or manually created.

#### Docker

The Grafana image requires mounting of the dashboards, datasource file, and configuration file. The Docker run command for the packaged example is given below:

docker run \
    -p "${NALMS_GRAFANA_PORT}:3000" \
    -v "${NALMS_GRAFANA_DASHBOARD_DIR}:/var/lib/grafana/dashboards" \
    -v "${NALMS_GRAFANA_DATASOURCE_FILE}:/etc/grafana/provisioning/datasources/all.yml" \
    -v "${NALMS_GRAFANA_CONFIG}:/etc/grafana/config.ini" \
    -e ES_HOST=$NALMS_ES_HOST \
    -e ES_PORT=$NALMS_ES_PORT \
    --name nalms_grafana \
    -d jgarrahan/nalms-grafana:latest


The Grafana dashboards are then reachable at localhost:${NALMS_GRAFANA_PORT} in browser.

### Cruise Control

#### Configuration

The `cruise-control/cruisecontrol.properties` file dictates the behavior of the cruise control server, allowing definition of relevant thresholds and networking nodes. The `jgarrahan/nalms-cruise-control` image performs interpolation on this file in order to pass the relevant environment variables. 

See wiki:
https://github.com/linkedin/cruise-control/wiki
https://github.com/linkedin/cruise-control-ui/wiki/Single-Kafka-Cluster

#### Docker


In order to run this image, you must mount a cruisecontrol.properties to a path specified with the $CRUISE_CONTROL_PROPERTIES env variable. The image will perform interpolation on properties files with $BOOTSTRAP_SERVERS or $ZOOKEEPER_CONNECT as placeholders and defined $BOOTSTRAP_SERVERS or $ZOOKEEPER_CONNECT environment variables. The Docker run command for the packaged example is given below:

docker run \
    -e BOOTSTRAP_SERVERS="${NALMS_KAFKA_BOOTSTRAP}" \
    -e ZOOKEEPER_CONNECT="${NALMS_ZOOKEEPER_HOST}:${NALMS_ZOOKEEPER_PORT}" \
    -e CRUISE_CONTROL_PROPERTIES="/opt/cruise-control/config/cruisecontrol.properties" \
    -v "${NALMS_CRUISE_CONTROL_PROPERTIES}:/opt/cruise-control/config/cruisecontrol.properties" \
    --name nalms_cruise_control \
    -p "$NALMS_CRUISE_CONTROL_PORT:9090" -d jgarrahan/nalms-cruise-control:latest

The Cruise Control UI is then available in browser at localhost:9090.