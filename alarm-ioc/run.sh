#!/usr/bin/env bash
#
# Author: Jacqueline Garrahan
# Run ioc creation and launch
#
if [ "$1" == "-h" ]; then
  echo "Usage: run.sh"
  exit 0
fi

if [[ -z "$CONFIG_FILE" ]]; then
  echo "Configuration file not defined. Please set \$CONFIG_FILE."
  exit 0
fi

if [[ -z "$TEMPLATE_FILE" ]]; then
  echo "Template file not defined. Please set \$TEMPLATE_FILE."
  exit 0
fi

if [[ -z "$IOC_DIR" ]]; then
  echo "IOC directory not defined. Please set \$IOC_DIR."
  exit 0
fi

if [[ -z "$CONFIG_NAME" ]]; then
  echo "Configuration name not provided. Please set \$CONFIG_NAME."
  exit 0
fi



python /opt/nalms/create_soft_iocs.py ${CONFIG_FILE} ${TEMPLATE_FILE} ${IOC_DIR} ${CONFIG_NAME}
softIoc ${IOC_DIR}/st.cmd