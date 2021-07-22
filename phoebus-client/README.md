# Phoebus client docker

This image contains a phoebus product build with only the alarm tool applications, specified in the pom.xml. 

To run using XQuartz, activate the ‘Allow connections from network clients’ option in XQuartz settings and restart. Then, allow access from localhost, replacing containerId with the failed running container:

```
xhost +local:`docker inspect --format='{{ .Config.Hostname }}' $containerId`
docker start $containerId
```