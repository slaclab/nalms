# Docs

This project uses [mkdocs](https://www.mkdocs.org/) for generating documentation. This can be installed with Python. Once mkdocs and mkdocs-material have been installed, the documentation may be served locally using the command:

```
$ mkdocs serve
```

A GitHub action workflow has been configured such that the docs are automatically created on merge to the `slaclab/nalms` `main` branch.

## Docker images
Significant simplifications might be made to these docker images (moving to more modern OS etc.); however, I've tried to replicate the RHEL 7 design requirement as closely as possible to demonstrate the installation outlined in the design document. 

Newer versioned releases should be indicated to the nalms package by updates to version environment variables:

```
# versions
export NALMS_DOCKER_ES_VERSION=v0.6
export NALMS_DOCKER_GRAFANA_VERSION=v0.6
export NALMS_DOCKER_ALARM_SERVER_VERSION=v0.6
export NALMS_DOCKER_ALARM_LOGGER_VERSION=v0.6
export NALMS_DOCKER_ZOOKEEPER_VERSION=v0.6
export NALMS_DOCKER_CRUISE_CONTROL_VERSION=v0.6
export NALMS_DOCKER_KAFKA_VERSION=v0.6
```


### Useful commands:
To see all running and stopped containers

```
$ sudo docker container ls -a
```

The current installation of Docker on rhel... requires sudo for use


to get the id of a running container:

```
$ sudo docker container ls
```

To get memory, CPU use:

```
sudo docker container stats ${CONTAINER_ID}
```

Container information, including networking info,  is available using:
```
$ sudo docker container inspect${CONTAINER_ID}
```

To attach to a running container:
```
$ sudo docker container exec -it fdc6ce9ce655 /bin/bash
```

## DockerHub deployment

At this current iteration, all Dockerhub images are hosted on my (Jacqueline Garrahan) personal account (jgarrahan). A Github action has been defined for the automatic build of images on tagged releases to the main slaclab/master branch. This ought to be changed to use a designated SLAC account.

Additionally, all images should be removed from this repository and moved into their own for convenient versioning.

## Ongoing projects

An attempt has been made to document development needs using Github projects [here](https://github.com/slaclab/nalms/projects).

## Helpful debugging

### Phoebus Alarm Server

In the event of problematic IOC connectivity, it may be worthwhile to connect to the Phoebus Alarm Server docker container using:

```
$ sudo docker container exec -it fdc6ce9ce655 /bin/bash
```

and edit the logging options in $LOGGING_CONFIG_FILE. 

```ini
org.phoebus.applications.alarm.level = INFO
com.cosylab.epics.caj.level = FINE # handles connectivity
org.phoebus.framework.rdb.level = WARNING
org.phoebus.pv.level = FINE
org.apache.kafka.level = SEVERE
```


## Grafana template
In order to use the Grafana dashboard with a scaling number of configurations, a json template is located in `grafana/dashboards/alarm_logs_dashboard.json`. The script `grafana/scripts/start-grafana.sh` performs an interpolation of template strings in order to create the appropriate datasources and dashboards.

For further development of the dashboard, the template must be changed using a local Grafana instance. Steps for updating are:
* Copy json representation
* Remove id from the json representation
* Replace datasource and configuration name entries from json representation