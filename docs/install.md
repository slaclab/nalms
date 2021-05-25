# Installation

Requirements
- Kafka
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
| NALMS_TOP                | Path to NALMS installation                                    |
| KAKFA_TOP                | Path to Kafka installation                                    |
| EPICS_CA_AUTO_ADDR_LIST  | Enable network interface introspection                        |
| EPICS_CA_ADDR_LIST       | Destination addresses for CA client name resolution requests  |
| EPICS_CA_REPEATER_PORT   | UDP port for server beacon initialization                     |
| EPICS_CA_SERVER_PORT     | Port number for server                                        |
| ZOOKEEPER_HOST           | Zookeeper host and port number                                |
| NALMS_LOG_PATH           | Path for java logging                                         |
| JAVA_HOME                | File system path of JDK installation                          |
| NALMS_ENV                | dev/prod                                                      |
| KAFKA_BOOTSTRAP          | Address of Kakfa bootstrap node                               |
| ELASTICSEARCH_TOP        | Path to Elasticsearch installation                            |
| ELASTICSEARCH_LOG_DIR    | Path to the Elasticsearch log directory                       |
| ELASTICSEARCH_DATA_DIR   | Path to the ELasticsearch data directory                      |
| KAFKA_PROPERTIES         | Path to the Kafka properties file                             |
| ZOOKEEPER_PROPERTIES     | Path to the Zookeeper properties file                         |


` sudo -E bash install.sh`


Details of the scripts relevant to developers are listed below:

## Build

The build script creates all configuration artifacts and stores them in the `/tmp/nalms` directory.


## Install

Installation handles the creation of appropriate roles, movement of configuration files to their appropriate directory, configuration of systemd files...


Skip build option

Like the build script, it is possible to run this command for a single service.


### Elasticsearch

Because elasticsearch should not be run as root, a designated user is created during the installation `elasticsearch`.
Permissions to the elasticsearch log and data directories are assigned to this newly created user when the installation is executed. 

### Phoebus Alarm Logger and Alarm Server

The Phoebus installation consists of the alarm logger and server `.jar` files packages in the `alarm-logger` and `alarm-server` directories, respectively. No additional work is needed for their installation with NALMS and configuration files must be indicated at runtime. 

During installation, a designated user will be created for interacting with tmux. For this reason, the packaged scripts should be used for attaching to sessions rather than accessing directly.