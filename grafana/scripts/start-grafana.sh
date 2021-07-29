#!/bin/bash


# create dashboards
export IFS=","
for CONFIG_ITEM in $CONFIG_NAME; do
    sed 's/$DATASOURCE_NAME/'"$CONFIG_ITEM/"  $DASHBOARD_TEMPLATE > "${DASHBOARD_DIR}/${CONFIG_ITEM}.json"
done


# create datasource from configurations
bash /opt/nalms/create-datasource-file.sh 

# update dashboards
#(bash /opt/nalms/update-dashboards.sh) &

#run
/run.sh