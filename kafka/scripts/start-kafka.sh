#!/usr/bin/env bash
#
usage() {
  cli_name=${0##*/}
  echo "Usage: start-kafka.sh\n"
  echo "Requires definition of \$KAFKA_HOME,  \$DOMAIN, \$KAFKA_ADVERTISED_LISTENERS, \$KAFKA_LISTENER_SECURITY_PROTOCOL_MAP,"
  echo "\$KAFKA_LISTENERS, \$ZOOKEEPER_CONNECT, \$BROKER_ID, \$KEYSTORE_PASSWORD, \$TRUSTSTORE_PASSWORD, \$KEY_PASSWORD, \$USE_SSL"
  exit 0
}

if [[ "$1" == "-h" ]]; then
  usage
fi

if [[ -z "$KAFKA_ADVERTISED_LISTENERS" ]]; then
    echo "\$KAFKA_ADVERTISED_LISTENERS not defined."
    usage
fi

if [[ -z "$KAFKA_LISTENER_SECURITY_PROTOCOL_MAP" ]]; then
    echo "\$KAFKA_LISTENER_SECURITY_PROTOCOL_MAP not defined."
    usage
fi

if [[ -z "$ZOOKEEPER_CONNECT" ]]; then
    echo "\$ZOOKEEPER_CONNECT not defined."
    usage
fi

if [[ -z "$BROKER_ID" ]]; then
    echo "\$BROKER_ID not defined."
    usage
fi


if [[ "$USE_SSL" = true ]]; then


    if [[ -z "$KEYSTORE_PASSWORD" ]]; then
        echo "\$KEYSTORE_PASSWORD not defined."
        usage
    fi

    if [[ -z "$TRUSTSTORE_PASSWORD" ]]; then
        echo "\$TRUSTSTORE_PASSWORD not defined."
        usage
    fi

    if [[ -z "$KEY_PASSWORD" ]]; then
        echo "\$KEY_PASSWORD not defined."
        usage
    fi


    # start ssl server
    ./opt/kafka/bin/kafka-server-start.sh /opt/kafka/server.properties --override advertised.listeners=${KAFKA_ADVERTISED_LISTENERS} \
        --override listener.security.protocol.map=${KAFKA_LISTENER_SECURITY_PROTOCOL_MAP} --override listeners=${KAFKA_LISTENERS} \
        --override zookeeper.connect=${ZOOKEEPER_CONNECT} --override boker.id=${BROKER_ID} \
        --override ssl.keystore.password=${KEYSTORE_PASSWORD} \
        --override ssl.truststore.password=${TRUSTSTORE_PASSWORD} \
        --override ssl.key.password=${KEY_PASSWORD}
else
    # start server
    ./opt/kafka/bin/kafka-server-start.sh /opt/kafka/server.properties --override advertised.listeners=${KAFKA_ADVERTISED_LISTENERS} \
        --override listener.security.protocol.map=${KAFKA_LISTENER_SECURITY_PROTOCOL_MAP} --override listeners=${KAFKA_LISTENERS} \
        --override zookeeper.connect=${ZOOKEEPER_CONNECT} --override boker.id=${BROKER_ID} 
fi
