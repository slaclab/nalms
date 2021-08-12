#!/bin/sh
# Author: Jacqueline Garrahan
#
# Start Zookeeper 
sed -i -r 's|#(log4j.appender.ROLLINGFILE.MaxBackupIndex.*)|\1|g' $ZK_HOME/conf/log4j.properties

# copy mounted config to config path
cp $ZOOKEEPER_CONFIG $ZOOKEEPER_CONFIG_PATH

$ZK_HOME/bin/zkServer.sh start-foreground