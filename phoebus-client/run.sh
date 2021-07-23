#!/bin/bash
#
# Author: Jacqueline Garrahan
# Start up phoebus client
usage() {
  cli_name=${0##*/}
  echo "Usage: run.sh"
  echo "Requires definition of \$CONFIG_NAME, \$ES_HOST, \$ES_PORT"
  exit 0
}

if [[ "$1" == "-h" ]]; then
  usage
fi

if [[ -z "$CONFIG_NAME" ]]; then
  echo "Config name not defined."
  usage
fi

if [[ -z "$ES_HOST" ]]; then
  echo "Elasticsearch host not provided."
  usage
fi

if [[ -z "$ES_PORT" ]]; then
  echo "Elasticsearch port not provided."
  usage
fi

if [[ -z "$KAFKA_HOST" ]]; then
  echo "Elasticsearch host not provided."
  usage
fi

if [[ -z "$KAFKA_PORT" ]]; then
  echo "Elasticsearch port not provided."
  usage
fi

ES_INDEX=val=$(echo "$CONFIG_NAME" | tr '[:upper:]' '[:lower:]')

sed -i 's/$CONFIG_NAME/'"$CONFIG_NAME/" /opt/nalms/client.properties
sed -i 's/$KAFKA_HOST/'"$KAFKA_HOST/" /opt/nalms/client.properties
sed -i 's/$KAFKA_PORT/'"$KAFKA_PORT/" /opt/nalms/client.properties
sed -i 's/$ES_HOST/'"$ES_HOST/" /opt/nalms/client.properties
sed -i 's/$ES_PORT/'"$ES_PORT/" /opt/nalms/client.properties
sed -i 's/$ES_INDEX/'"$ES_INDEX*/" /opt/nalms/client.properties


dbus-uuidgen > /var/lib/dbus/machine-id
dbus-daemon 
#--config-file=/etc/dbus-1/myCustomDbus.conf --print-address
java -jar /opt/phoebus/phoebus-product/target/product-*-SNAPSHOT.jar -settings /opt/nalms/client.properties