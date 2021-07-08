#!/usr/bin/env bash
#
# Author: Jacqueline Garrahan
# Run phoebus-alarm-server image for given configuration
#
if [ "$1" == "-h" ]; then
  echo "Usage: deploy-configuration.sh [Configuration Name] [Configuration file] [Alarm server properties file] [Logging configuration files]"
  exit 0
fi


docker run -v $2:/tmp/nalms/$1.xml -v $3:/opt/nalms/config/alarm_server.properties -v $4:/opt/nalms/config/logging.properties phoebus-alarm-server start-server $1 /tmp/nalms/$1.xml
