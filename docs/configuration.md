# Configuration

An attempt has been made to centralize configurations for streamlined Dockerized deployments. All configuration files are housed within the `config` directory of their respective subfolders. These files will need to be modified for deployment into particular networks; however, this sections includes an attempt to isolate the important configuration items to be addressed. 

An attempt has been made to sufficiently abstract scripts for deployments based on environment variables.


## Elasticsearch

The Elasticsearch configuration is defined using the files in `elasticsearch/config`. The configuration is indicated to the Elasticsearch server during launch by the INSERT_ENV_VAR environment variable. 

For security reasons, the Elasticsearch service requires a user other than root and so an Elasticsearch user must be created with appropriate permissions. Package managers (rpm, yum, etc.) typically handle this during installation, creating a designated `elasticsearch` user, and register the Elasticsearch service as a systemd service. If installing from source, this workflow must be replicated and a designated user assigned. A utility script for user creation and sytemd deployment has been provided in `tools`, requiring root privileges. This will automatically generate and register the `nalms-elasticsearch` service with systemd, but not start (see installation notes).

```
$ ./build.sh --elasticsearch
```

This requires the following environment variable be set:

| Variable                 | Description                                                   |
|--------------------------|---------------------------------------------------------------|
| JAVA_HOME                | File system path of JDK installation                          |
| ELASTICSEARCH_DATA_DIR   | Directory containing elasticsearch data                       |
| ELASTICSEARCH_LOG_DIR    | Logging driectory                                             |
| ELASTICSEARCH_HOME       | Path to the elasticsearch installation                        |

The service may then be started using:
```
$ systemd start nalms-elasticsearch.
```
Depending on the location of the Elasticsearch installation, it may be desireable to redirect Java logs such that they...

- INSERT PORT EXPOSURES
- INSERT COMMUNICATIONS PROTOCOL
- Java logging notes

In order for the Elasticsearch fields to be properly formatted, a template matching the topic scheme must be posted to the server. These may be versioned and are automatically applied to newly created indices. The initial script for templating NALMS topics is hosted in `elasticsearch/scripts/create_alarm_template.sh`.


## Kafka
The Kafka configuration packaged with this repository is only suitable for a single broker deployment, withe the `replication.factor` set to 1. A cluster deployment can accomodate a larger replication factor across the cluster and this file must be modified for the purpose. 

Also hard coded in this file is the reference to the zookeeper docker image resource:
```
zookeeper.connect=zookeeper:2181
```
This must be modified with respect to deployment (or abstracted...).

This file may also be used to configure communications protocols within the cluster and ouside the cluster. Instructions for configuring the Kafka truststore may be found [here](https://docs.confluent.io/platform/current/kafka/authentication_ssl.html). Listeners are defined with respect to configured protocols and binding ports. Advertised listeners are configured with respect to configured protocol and exposed ports. 

Certain configurations options may be defined on the topic level. In `kafka/scripts/create-configuration.sh`, state topics are created with a single partition and replication factor = 1, partitions = 1. This will require change depending on the Kafka configuration. After initial creation, the Talk and Command topics are modified to use the deletion cleanup policy with set retention time. At present, the Talk command is created though unused.

There are many other settings pertaining to the optimization of the cluster and must be determined by traffic demands. 

A full catalog of available configurations may be found in the documentation, [here](https://kafka.apache.org/documentation/).

## Phoebus Alarm Services

The Phoebus Alarm server and logger configuration properties files define settings to be used by the services. This includes the EPICS configuration and Elasticsearch host configuration. A full preference list can be found in the CS-Studio [documentation](https://control-system-studio.readthedocs.io/en/latest/preference_properties.html)

Of particular importance is the EPICS, Kakfa, and Elasticsearch configuration variables. The Alarm Server requires:

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


The Alarm Logger requires the definition of the following:
```ini
# location of elastic node/s
es_host=localhost
es_port=9200

# Kafka server location
bootstrap.servers=localhost:9092
```