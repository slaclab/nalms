#!/bin/sh
# Author: Jacqueline Garrahan
#
# This script initializes the 
#
# Copyright @2021 SLAC National Accelerator Laboratory

DIRNAME=`dirname $0`
(bash ${DIRNAME}/create_alarm_template.sh 100) &

#bash ${ES_HOME}/bin/elasticsearch -E "discovery.type=single-node"
bash /usr/local/bin/docker-entrypoint.sh eswrapper