# Installation

Requirements
- Kafka
- Elasticsearch

```
$ git clone nalms
```




` sudo install.sh []`



Details of the scripts relevant to developers are listed below:

## Build

The build script creates all configuration artifacts and stores them in the `/tmp/nalms` directory.


## Install

Installation handles the creation of appropriate roles, movement of configuration files to their appropriate directory, configuration of systemd files...


Skip build option

Like the build script, it is possible to run this command for a single service.


### Elasticsearch

Because elasticsearch should not be run as root, a designated user is created during the installation `nalmselasticsearch`.
Permissions to the elasticsearch log and data directories are assigned to this newly created user. 