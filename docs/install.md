# Installation

Requirements
- Kafka (cruise-control-metrics-reporter-A.B.B.jar)
- Elasticsearch
- tmux
- 

```
$ git clone nalms
```

## Environment variables

The installation depends on properly configured environment variables for EPICS specifications and configuration paths. The following variables must be defined during the execution of `install.sh`.

| Variable                 | Description                                                   |
|--------------------------|---------------------------------------------------------------|
| NALMS_HOME               | Path to NALMS installation                                    |
| KAKFA_HOME               | Path to Kafka installation                                    |
| EPICS_CA_AUTO_ADDR_LIST  | Enable network interface introspection                        |
| EPICS_CA_ADDR_LIST       | Destination addresses for CA client name resolution requests  |
| EPICS_CA_REPEATER_PORT   | UDP port for server beacon initialization                     |
| EPICS_CA_SERVER_PORT     | Port number for server                                        |
| ZOOKEEPER_HOST           | Zookeeper host and port number                                |
| NALMS_LOG_PATH           | Path for java logging                                         |
| JAVA_HOME                | File system path of JDK installation                          |
| NALMS_ENV                | dev/prod                                                      |
| KAFKA_BOOTSTRAP          | Address of Kakfa bootstrap node                               |
| ELASTICSEARCH_HOME       | Path to Elasticsearch installation                            |
| ELASTICSEARCH_LOG_DIR    | Path to the Elasticsearch log directory                       |
| ELASTICSEARCH_DATA_DIR   | Path to the ELasticsearch data directory                      |
| KAFKA_PROPERTIES         | Path to the Kafka properties file                             |
| ZOOKEEPER_PROPERTIES     | Path to the Zookeeper properties file                         |


Details of the scripts relevant to developers are listed below:

## Build

The build script creates all configuration artifacts and stores them in the `/tmp/nalms` directory. The build script may be used to build a subset of services by specifying via `--elasticsearch`, `--kafka`, `--zookeeper`.


```
sudo -E bash build.sh
``` 

## Install

Installation handles the creation of appropriate roles, builds and deploys relevant systemd files. The install script may be used to build a subset of services by specifying via `--elasticsearch`, `--kafka`, `--zookeeper`.


```
sudo -E bash install.sh
``` 


### Elasticsearch

Because elasticsearch should not be run as root, a designated user is created during the installation `elasticsearch`.
Permissions to the elasticsearch log and data directories are assigned to this newly created user when the installation is executed. 

### Phoebus Alarm Logger and Alarm Server

The Phoebus alarm tools may be downloaded from latest release, or built locally with OpenJDK >= 11 and maven using the following:

```
$ git clone https://github.com/ControlSystemStudio/phoebus.git
$ cd phoebus
$ mvn install -pl services/alarm-server -am
$ mvn install -pl services/alarm-logger -am
```

Once installed, the `ALARM_SERVER_JAR` and `ALARM_LOGGER_JAR` environment variables should be set to point to the files in `phoebus/services/alarm-server/target/` and `phoebus/services/alarm-logger/target/`, respectively. 
