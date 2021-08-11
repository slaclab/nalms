# NALMS cruise-control image

In order to run this image, you must mount a cruisecontrol.properties file to `/opt/cruise-control/config/cruisecontrol.properties`. The image will perform interpolation on properties files with $BOOTSTRAP_SERVERS or $ZOOKEEPER_CONNECT as placeholders and defined $BOOTSTRAP_SERVERS or $ZOOKEEPER_CONNECT environment variables. 