#!/bin/sh

# sleep while elasticsearch starts
if [[ ! -z "$1" ]]; then
  sleep $1
fi

if [[ -z "$ES_HOST" ]]; then
  echo "ES_HOST is not set."
  exit 0
fi

if [[ -z "$ES_PORT" ]]; then
  echo "ES_PORT is not set."
  exit 0
fi

# Add a pipeline to be used in the templates for setting the create datetime of all documents
curl -X PUT http://${ES_HOST}:${ES_PORT}/_ingest/pipeline/add_created_date -H 'Content-Type: application/json' -d'
{
  "description": "Add the insertion date in the timezone of the box this is being run in",
  "processors": [
    {
      "script": {
        "source": "ctx.timestamp = new SimpleDateFormat(\"yyyy-MM-dd HH:mm:ss\").format(new Date());"
      }
    }
  ]
}
'

# The mapping names used in here need to match those used in the ElasticClientHelper:
# "alarm", ""alarm_cmd", "alarm_config"

# Create the elastic template with the correct mapping for alarm state messages.
curl -XPUT http://${ES_HOST}:${ES_PORT}/_template/alarms_state_template -H 'Content-Type: application/json' -d'
{
  "index_patterns":["*_alarms_state*"],
  "settings": {
    "index.default_pipeline": "add_created_date"
  },
  "mappings" : {  
    "alarm" : {
        "properties" : {
          "APPLICATION-ID" : {
            "type" : "text"
          },
          "config" : {
            "type" : "keyword"
          },
          "pv" : {
            "type" : "keyword"
          },
          "severity" : {
            "type" : "keyword"
          },
          "latch" : {
            "type" : "boolean"
          },
          "message" : {
            "type" : "text",
            "fields": {
              "keyword": { 
                "type": "keyword"
              }
            }
          },
          "value" : {
            "type" : "text"
          },
          "time" : {
            "type" : "date",
            "format" : "yyyy-MM-dd HH:mm:ss.SSS"
          },
          "message_time" : {
            "type" : "date",
            "format" : "yyyy-MM-dd HH:mm:ss.SSS"
          },
          "current_severity" : {
            "type" : "keyword"
          },
          "current_message" : {
            "type" : "text",
            "fields": {
              "keyword": { 
                "type": "keyword"
              }
            }
          },
          "mode" : {
            "type" : "keyword"
          }
        }
      }
  }
}
'

# Create the elastic template with the correct mapping for alarm command messages.
curl -XPUT http://${ES_HOST}:${ES_PORT}/_template/alarms_cmd_template -H 'Content-Type: application/json' -d'
{
  "index_patterns":["*_alarms_cmd*"],
  "mappings" : {  
    "alarm_cmd" : {
        "properties" : {
          "APPLICATION-ID" : {
            "type" : "text"
          },
          "config" : {
            "type" : "keyword"
          },
          "user" : {
            "type" : "keyword"
          },
          "host" : {
            "type" : "keyword"
          },
          "command" : {
            "type" : "keyword"
          },
          "message_time" : {
            "type" : "date",
            "format" : "yyyy-MM-dd HH:mm:ss.SSS"
          }
        }
      }
  }
}
'

# Create the elastic template with the correct mapping for alarm config messages.
curl -XPUT http://${ES_HOST}:${ES_PORT}/_template/alarms_config_template -H 'Content-Type: application/json' -d'
{
  "index_patterns":["*_alarms_config*"],
  "mappings" : {  
    "alarm_config" : {
        "properties" : {
          "APPLICATION-ID" : {
            "type" : "text"
          },
          "config" : {
            "type" : "keyword"
          },
          "user" : {
            "type" : "keyword"
          },
          "host" : {
            "type" : "keyword"
          },
          "enabled" : {
            "type" : "keyword"
          },
          "latching" : {
            "type" : "keyword"
          },
          "config_msg" : {
            "type" : "keyword"
          },
          "message_time" : {
            "type" : "date",
            "format" : "yyyy-MM-dd HH:mm:ss.SSS"
          }
        }
      }
  }
}
'


echo "Alarm templates:"
curl -X GET "${ES_HOST}:${ES_PORT}/_template/*alarm*"

