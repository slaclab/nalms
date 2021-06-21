#!/bin/sh
# Author: Jacqueline Garrahan
#
# This script initializes the 
#
# Copyright @2021 SLAC National Accelerator Laboratory

DIRNAME=`dirname $0`
(bash ${DIRNAME}/create_alarm_template.sh 20) &

bash "${ES_HOME}/bin/elasticsearch"