

## Services
Kafka, Zookeeper, and Elasticsearch will all be installed as services.

A utility script has been provided to aid with the installation...



## Submodules

Cruise control will be deployed as a submodule...


Kafka
```
$ sudo systemctl start nalms-kafka.service
$ sudo systemctl stop nalms-kafka.service
```


Zookeeper
```
$ sudo systemctl start nalms-zookeeper.service
$ sudo systemctl stop nalms-zookeeper.service
```

Elasticsearch
```
$ sudo systemctl start nalms-elasticsearch.service
$ sudo systemctl stop nalms-elasticsearch.service
```
