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
| NALMS_HOME                      | Path to NALMS repository                                      |
| NALMS_CLIENT_JAR                | Path to NALMS client jar file                                 |
| NALMS_ALARM_SERVER_PROPERTIES   | Path to alarm server properties file                          |
| NALMS_ALARM_LOGGER_PROPERTIES   | Path to alarm logger properties file                          |
| NALMS_CRUISE_CONTROL_PROPERTIES | Path to cruise control properties file                        |
| NALMS_GRAFANA_DASHBOARD_DIR     | Path to Grafana dashboard directory                           |
| NALMS_GRAFANA_CONFIG            | Path to Grafana configuration file                            |
| NALMS_GRAFANA_DATASOURCE_FILE   | Path to Grafana datasource file                               |
| NALMS_ZOOKEEPER_CONFIG          | Path to Zookeeper configuration file                          |
| NALMS_ES_CONFIG                 | Path to elasticsearch configuration file                      |

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

## add-grafana-datasource 
Add a Grafana datasource for a configuration(s).
```
$ bash cli/nalms add-grafana-datasource config_names
```

## build-grafana-dashboard
Build a Grafana dashboard for a configuration
```
$ bash cli/nalms build-grafana-dashboard config_name
```