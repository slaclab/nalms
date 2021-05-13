#!/bin/sh
# Author: Jacqueline Garrahan
#
# This script builds the settings.ini file used with the Phoebus tools.
# This intended to be a convenience script for creating a settings file using the EPICS
# environment variables.
# 
#
# Copyright @2021 SLAC National Accelerator Laboratory

if [ $# -ne 1 ]
then
    echo "Usage: create_settings.sh filename"
    exit 1
fi

filename=$1

echo "# ----------------------" >> $filename
echo "# Package org.phoebus.pv" >> $filename
echo "# ----------------------" >> $filename
echo "org.phoebus.pv/default=ca" >> $filename


echo "" >> $filename
echo "" >> $filename

echo "# -------------------------" >> $filename
echo "# Package org.phoebus.pv.ca" >> $filename
echo "# -------------------------" >> $filename
echo "org.phoebus.pv.ca/addr_list=${EPICS_CA_ADDR_LIST}" >> $filename
echo "org.phoebus.pv.ca/auto_addr_list=$(echo ${EPICS_CA_AUTO_ADDR_LIST} | tr  '[:upper:]' '[:lower:]')" >> $filename
echo "org.phoebus.pv.ca/server_port=${EPICS_CA_SERVER_PORT}" >> $filename
echo "org.phoebus.pv.ca/repeater_port=${EPICS_CA_REPEATER_PORT}" >> $filename
echo "org.phoebus.pv.ca/max_array_bytes=${EPICS_CA_MAX_ARRAY_BYTES}" >> $filename
echo "org.phoebus.pv.ca/connection_timeout=${EPICS_CA_CONN_TMO}" >> $filename
echo "org.phoebus.pv.ca/beacon_period=${EPICS_CA_BEACON_PERIOD}" >> $filename

# Support variable length arrays?
# auto, true, false
echo "org.phoebus.pv.ca/variable_length_array=auto" >> $filename

# Connect at lower priority for arrays
# with more elements than this threshold
echo "org.phoebus.pv.ca/large_array_threshold=100000" >> $filename

# Is the DBE_PROPERTY subscription supported
# to monitor for changes in units, limits etc?
echo "org.phoebus.pv.ca/dbe_property_supported=false" >> $filename

# Mask to use for subscriptions
# VALUE, ALARM, ARCHIVE
echo "org.phoebus.pv.ca/monitor_mask=VALUE" >> $filename

# Name server list
echo "org.phoebus.pv.ca/name_servers=" >> $filename