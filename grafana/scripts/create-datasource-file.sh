#!/bin/bash
#
# Create dynamic datasource dir for all configs in image


DATASOURCE_FILE="${DATASOURCE_DIR}/all.yml"
export IFS=","

# convert to lowercase for index
CONFIG=$(echo "$CONFIG_NAME" | tr '[:upper:]' '[:lower:]')

# Create file
echo "apiVersion: 1"  >> $DATASOURCE_FILE
echo "" >> $DATASOURCE_FILE
echo "" >> $DATASOURCE_FILE
echo "datasources:" >> $DATASOURCE_FILE


for word in $CONFIG_NAME; do
    # convert to lowercase for index
    CONFIG=$(echo "$word" | tr '[:upper:]' '[:lower:]')
    echo "  - name: ${word}" >> $DATASOURCE_FILE
    echo "    type: elasticsearch" >> $DATASOURCE_FILE
    echo "    access: proxy" >> $DATASOURCE_FILE
    echo "    database: \"${CONFIG}_*\"" >> $DATASOURCE_FILE
    echo "    url: http://${ES_HOST}:${ES_PORT}" >> $DATASOURCE_FILE
    echo "    jsonData:" >> $DATASOURCE_FILE
    echo "      esVersion: 60" >> $DATASOURCE_FILE
    echo "      timeField: \"message_time\"" >> $DATASOURCE_FILE
    echo "      logMessageField: \"id\"" >> $DATASOURCE_FILE

done

echo "Completed writing file."