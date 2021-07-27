# Command Line Tools

In order to abstract the deployment process and interact with the Dockerized applications, a CLI has been packaged with the NALMS repository. A properly configured environment will define the following NALMS specific variables. EPICS variables must also be defined for appropriate networking. The `nalms-tools` package must be installed into the active python environment for 

| Variable                        | Description                                                   |
|---------------------------------|---------------------------------------------------------------|
| NALMS_KAFKA_PROPERTIES          | Path to Kafka properties file                                 |
| NALMS_ZOOKEEPER_PORT            | Zookeeper port                                                |
| NALMS_ES_PORT                   | Elasticsearch port                                            |
| NALMS_CRUISE_CONTROL_PORT       | Cruise control port                                           |
| NALMS_KAFKA_PORT                | Exposed broker port                                           |
| NALMS_GRAFANA_PORT              | Grafana port                                                  |
| NALMS_ES_HOST                   | Elasticsearch network host address                            |
| NALMS_KAFKA_BOOTSTRAP           | Bootstrap node for Kafka connections                          |
| NALMS_ZOOKEEPER_HOST            | Zookeeper network host address                                |
| NALMS_KAFKA_HOST                | Kafka broker network host address                             |
| NALMS_CONFIGURATIONS            | Comma separated list of configurations for launching Grafana  |

## convert-alh

Command converts ALH configuration to Phoebus XML representation.

```
$ bash cli/nalms convert-alh alh_file output_filename config_name
```

## create-alarm-ioc

Create the alarm ioc files for a given configuration.

```
$ bash cli/nalms create-alarm-ioc configuration_file config_name output_directory
```

## delete-configuration

Delete Kafka topics associated with a configuration.

```
$ bash cli/nalms delete-configuration configuration_name
```

## generate-kafka-certs

Generate certificates for Kafka trust store for configuration with SSL.

```
$ bash cli/nalms generate-kafka-certs domain password

```
## launch-editor
Launch the configuration editor.
```
$ bash cli/nalms launch-editor
```

## list-configurations
List active Kafka configurations.
```
$ bash cli/nalms list-configurations
```

## start-alarm-logger
Start the alarm logger for a given configuration name and configuration file. Configuration name must match that defined in the configuration file. This will create an image named `nalms-logger-${CONFIG_NAME}`.
```
$ bash cli/nalms start-alarm-logger config_name config_file
```

## start-alarm-server
Start the alarm server for a given configuration name and configuration file. Configuration name must match that defined in the configuration file. This will create an image named `nalms-server-${CONFIG_NAME}`.
```
$ bash cli/nalms start-alarm-server config_name config_file
```

## start-cruise-control
Start Cruise Control. This will create an image named `nalms_cruise_control`.

```
$ bash cli/nalms start-cruise-control
```

## start-grafana
Start the Grafana server, creating an image named `nalms_grafana`.
```
$ bash cli/nalms start-grafana
```

## start-kafka-broker
Start a Kafak broker. Must indicate a broker number for broker identification. This will create an image named `nalms_kafka_$BROKER_NUMBER`.

```
$ bash cli/nalms start-kafka-broker --broker_number broker_number
```

## start-phoebus-client
Launch the Phoebus client.
```
$ bash cli/nalms start-phoebus-client 
```

## start-zookeeper
Start Zookeeper, creating image named `nalms_zookeeper`.
```
$ bash cli/nalms start-zookeeper
```