# NALMS at SLAC

## aird-

Environment setup:

```
$ source ${PACKAGE_TOP}/nalms/setup/aird-b50-srv01/dev.env
```

Variables:

| Variable                        | Description                                                     |
|---------------------------------|-----------------------------------------------------------------|
| NALMS_ZOOKEEPER_PORT            | 2181                                                            |
| NALMS_ES_PORT                   | 9000                                                            |
| NALMS_CRUISE_CONTROL_PORT       | 9090                                                            |
| NALMS_KAFKA_PORT                | 9092                                                            |
| NALMS_GRAFANA_PORT              | 3000                                                            |
| NALMS_ES_HOST                   | aird-b50-srv01                                                  |
| NALMS_KAFKA_BOOTSTRAP           | aird-b50-srv01:9092                                             |
| NALMS_ZOOKEEPER_HOST            | aird-b50-srv01                                                  |
| NALMS_KAFKA_HOST                | aird-b50-srv01                                                  |
| NALMS_HOME                      | ${PACKAGE_TOP}/nalms/current                                    |
| NALMS_CLIENT_JAR                | /opt/phoebus/phoebus-product/target/product-4.6.6-SNAPSHOT.jar  |
| NALMS_KAFKA_PROPERTIES          | ${PACKAGE_TOP}/setup/aird-b50-srv01/config/server.properties    |



#!/bin/bash
export DEMO_DIR="$(cd -P "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

export EPICS_CA_AUTO_ADDR_LIST=YES
export EPICS_CA_ADDR_LIST=134.79.216.60:5066
export EPICS_CA_REPEATER_PORT=5067
export EPICS_CA_SERVER_PORT=5066

export NALMS_KAFKA_PROPERTIES=${DEMO_DIR}/config/server.properties

export NALMS_ZOOKEEPER_PORT=2181
export NALMS_ES_PORT=9200
export NALMS_CRUISE_CONTROL_PORT=9090
export NALMS_KAFKA_PORT=9092
export NALMS_GRAFANA_PORT=3000

export NALMS_ES_HOST=$HOST_IP
export NALMS_KAFKA_BOOTSTRAP=$HOST_IP:$NALMS_KAFKA_PORT
export NALMS_ZOOKEEPER_HOST=$HOST_IP
export NALMS_KAFKA_HOST=$HOST_IP

