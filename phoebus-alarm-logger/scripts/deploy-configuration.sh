#!/usr/bin/env bash
#
# Author: Jacqueline Garrahan
# Run phoebus-alarm-logger image for given configuration
#


if [ "$1" == "-h" ]; then
  echo "Usage: deploy-configuration.sh [Configuration Name] [Configuration file] [Alarm logger properties file] [Logging configuration files]"
  exit 0
fi

docker run -v $2:/tmp/nalms/$1.xml -v $3:/opt/nalms/config/alarm_logger.properties -v $4:/opt/nalms/config/logging.properties -t phoebus-alarm-logger start-logger $1 /tmp/nalms/$1.xml