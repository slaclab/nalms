#!/usr/bin/env bash
#
# Author: Jacqueline Garrahan
# Run ioc creation and launch
#
if [ "$1" == "-h" ]; then
  echo "Usage: run.sh"
  exit 0
fi

python /opt/nalms/create_soft_iocs.py ${CONFIG_FILE} ${TEMPLATE_FILE} ${IOC_DIR} ${CONFIG_NAME}
softIoc ${IOC_DIR}/st.cmd