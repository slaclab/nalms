#!/bin/sh
# Author: Jacqueline Garrahan
#
# Create tmux sessions and launch alarm services
#
# Copyright @2021 SLAC National Accelerator Laboratory

EXIT=0

if [ "$1" == "-h" ]; then
  echo "Usage: create-window.sh config_name config_file [--softIoc]"
  exit 0
fi

if [[ -z "$1" || "$1" == "--softIoc" ]]; then
  echo "Configuration name not provided."
  echo "Usage: create-window.sh config_name config_file [--softIoc]"
  exit 0
else
  echo $1
fi

if [[ -z "$2" || "$2" == "--softIoc" ]]; then
  echo "Configuration file not provided."
  echo "Usage: create-window.sh config_name config_file [--softIoc]"
  exit 0
fi


BUILD_SOFTIOC=0
if [[ "$3" == "--softIoc" ]]; then
  BUILD_SOFTIOC=1
fi

if [[ -z "$LOGGING_CONFIG_FILE" ]]; then
  echo "Logging configuration file not defined. Please set \$LOGGING_CONFIG_FILE."
  exit 0
fi

if [[ -z "$ALARM_SERVER_SETTINGS" ]]; then
  echo "Alarm server settings file not defined. Please set \$ALARM_SERVER_SETTINGS."
  exit 0
fi

if [[ -z "$ALARM_LOGGER_PROPERTIES" ]]; then
  echo "Alarm logger properties file not defined. Please set \$ALARM_LOGGER_PROPERTIES."
  exit 0
fi

if [[ -z "$ALARM_SERVER_JAR" ]]; then
  echo "Alarm server jar file not defined. Please set \$ALARM_SERVER_JAR."
  exit 0
fi

if [[ -z "$ALARM_LOGGER_JAR" ]]; then
  echo "Alarm logger jar file not defined. Please set \$ALARM_LOGGER_JAR."
  exit 0
fi



export PATH="$JAVA_HOME/bin:$PATH"

CONFIG_NAME=$1
CONFIG_FILE=$2


# parse optional builds
while test $# -gt 0
do
    case "$1" in
        --softIoc) 
            CMD_FILE=$2
            ;;
    esac
    shift
done

if [[ ! -f "$CMD_FILE" ]]; then
  echo "SoftIOC start command file not found."
  exit 0
fi

# create nalms session if not running, attach otherwise
if [[ -z $(tmux list-sessions 2>/dev/null | grep nalms) ]]; then
  tmux $TMUX_OPTS new-session -s nalms -d
fi

# create config name
tmux new-window -a -t nalms -n $CONFIG_NAME -c $PWD

#create panes
tmux split-window -t nalms:$CONFIG_NAME
tmux select-layout -t nalms:$CONFIG_NAME tiled > /dev/null

if java -jar $SERVER_JAR -logging $LOGGING_CONFIG_FILE -config $CONFIG_NAME -import $CONFIG_FILE; then
  # set up server window 
  tmux send-keys -t nalms:$config_name.0 "export JAVA_HOME=$JAVA_HOME" C-m
  tmux send-keys -t nalms:$config_name.0 "export PATH=$JAVA_HOME/bin:$PATH" C-m
  tmux send-keys -t nalms:$config_name.0 "java -jar $ALARM_SERVER_JAR -config $CONFIG_NAME -logging $LOGGING_CONFIG_FILE -settings $ALARM_SERVER_SETTINGS" C-m

  # set up logger window
  tmux send-keys -t nalms:$config_name.1 "export JAVA_HOME=$JAVA_HOME" C-m
  tmux send-keys -t nalms:$config_name.1 "export PATH=$JAVA_HOME/bin:$PATH" C-m
  tmux send-keys -t nalms:$config_name.1 "java -jar $ALARM_LOGGER_JAR -logging $LOGGING_CONFIG_FILE -properties $ALARM_LOGGER_PROPERTIES -topics $CONFIG_NAME" C-m

  # set up softIoc
  if [[ -f $CMD_FILE ]]; then
    tmux send-keys -t nalms:$config_name.2 "export JAVA_HOME=$JAVA_HOME" C-m
    tmux send-keys -t nalms:$config_name.2 "export PATH=$JAVA_HOME/bin:$PATH" C-m
    tmux send-keys -t nalms:$config_name.2 "export EPICS_BASE=$EPICS_BASE" C-m
    tmux send-keys -t nalms:$config_name.2 "softIoc $CMD_FILE" C-m
  fi

  #kill the first window
  tmux kill-window -t nalms:$( tmux list-windows -t nalms -F "#{window_index}" | head -n 1 )

  tmux $TMUX_OPTS attach-session -t nalms
else
    echo "Unable to import configuration."
fi
