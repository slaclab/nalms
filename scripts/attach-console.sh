#!/bin/sh
# Author: Jacqueline Garrahan
#
# Attach to existing tmux consoles for a given alarm configuration.
#
# Copyright @2021 SLAC National Accelerator Laboratory
#

if [ "$1" == "-h" ]; then
  echo "Usage: create-window.sh config_name"
  exit 0
fi

if [[ -z "$1" ]]; then
  echo "Configuration name not provided."
  echo "Usage: create-window.sh config_name"
  exit 0
fi

CONFIG_NAME=$1

if [[ $( tmux list-windows -t nalms 2>/dev/null | grep $CONFIG_NAME ) ]] ; then
    tmux $TMUX_OPTS attach -t nalms
    tmux select-window -t nalms:$CONFIG_NAME
else 
    echo "No tmux window found for $CONFIG_NAME."
fi
