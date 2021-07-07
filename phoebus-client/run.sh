#!/bin/bash
dbus-uuidgen > /var/lib/dbus/machine-id
dbus-daemon 
#--config-file=/etc/dbus-1/myCustomDbus.conf --print-address
java -jar /opt/phoebus/phoebus-product/target/product-*-SNAPSHOT.jar -settings /opt/phoebus/phoebus.properties