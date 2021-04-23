# nalms-resources

This repository contains documents pertinent to the design of the Next ALarm System at SLAC. 


# Environment variables


Source appropriate EPICS environment 

- nalms
- - alarm-server
- - - current sym link 
- - alarm-logger




Deployment:
navigate to nalms_top/alarm-server/
untar the service-alarm-server{}.tar.gz
create symbolic link from current to release


After registering as services:
#sudo systemctl stop elasticsearch.service

wget 