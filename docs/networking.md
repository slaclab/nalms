# Kafka SSL
The Kafka docker image defined in this repository has been configured to run with SSL enabled or not, indicated by the `USE_SSL=true` environment variable. For SSL use, it is necessary to mount a configuration file with the following relevant items defined in `server.properties` to the `/opt/kafka/server.properties`:
```
ssl.truststore.location=/opt/kafka/ssl/server.truststore.jks
ssl.keystore.location=/opt/kafka/ssl/server.keystore.jks
security.inter.broker.protocol=SSL
ssl.client.auth=requested
ssl.keystore.type=JKS
ssl.endpoint.identification.algorithm=
```

Additionally, the listener security protocol map defined in the environment variables must be reflect outgoing SSL messages. For example:
```
KAFKA_ADVERTISED_LISTENERS: SSL://kafka.broker1:9092,CONNECTIONS_FROM_HOST://localhost:19093
KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: SSL:SSL,CONNECTIONS_FROM_HOST:PLAINTEXT
KAFKA_LISTENERS: SSL://kafka.broker1:9092,CONNECTIONS_FROM_HOST://0.0.0.0:19093
```
Relevant passwords must also be passed:
```
TRUSTSTORE_PASSWORD: kafkabroker
KEYSTORE_PASSWORD: kafkabroker
KEY_PASSWORD: kafkabroker
```
A utility script for generating the truststore/keystore can be run:
```
$ bash cli/nalms generate-kafka-certs domain password
```
This utility might be decomposed further into truststore/keystore/key passwords. The appropriate keystore will then be mounted to the docker volume at `/opt/kafka/ssl`. Keys for each broker will need to be added to the respective trust stores of each broker node.Documentation on SSL for Kafka may be found [here](https://kafka.apache.org/documentation/#security_ssl).

# Phoebus

The Phoebus alarm server and logger to not accomodate SSL/TLS out of the box and will require development. The workflow that must be changed to accomodate SSL on the Phoebus side can be found in the following file: 
[`phoebus/app/alarm/model/src/main/java/org/phoebus/applications/alarm/client/KafkaHelper.java
`](https://github.com/ControlSystemStudio/phoebus/blob/master/app/alarm/model/src/main/java/org/phoebus/applications/alarm/client/KafkaHelper.java). Logically, this will mean exposing the following additional streams settings to the application:
```
security.protocol=SSL
ssl.truststore.location=/path/to/kafka.client.truststore.jks
ssl.truststore.password=truststore_password
ssl.keystore.location=/path/to/kafka.client.keystore.jks
ssl.keystore.password=keystore_password
ssl.key.password=key_password
```

More information for setting up these settings may be found [here](https://kafka.apache.org/10/documentation/streams/developer-guide/security.html).

# Elasticsearch

Instructions for configuring elasticsearch security may be found here:
https://www.elastic.co/guide/en/elasticsearch/reference/6.8/ssl-tls.html

The Docker image provided with this repository is based off of the official Elasticsearch 6.8 image and the following guide can be used to configure SSL/TLS with this image: https://www.elastic.co/guide/en/elasticsearch/reference/6.8/docker.html

# Grafana

Grafana Elasticsearch datasources may be configured to use certificates during setup. Options for provisioning datasources may be found here:
https://grafana.com/docs/grafana/latest/administration/provisioning/


# PyDM 

The PyDM datasource and client widgets will need to be built to accomodate authentication. See project board here: https://github.com/jacquelinegarrahan/pydm/projects/1?add_cards_query=is%3Aopen