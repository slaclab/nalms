#!/bin/bash

# create datasource from configurations
bash /opt/nalms/create-datasource-file.sh 

# create dashboards
export IFS=","
for CONFIG in $CONFIG_NAME; do
    sed 's/$DATASOURCE_NAME/'"$CONFIG/"  $DASHBOARD_TEMPLATE > "${DASHBOARD_DIR}/${CONFIG_NAME}.json"
done


# update dashboards
(bash /opt/nalms/update-dashboards.sh) &

#run
/run.sh