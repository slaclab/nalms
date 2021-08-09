# Next ALarM Sytem

NALMS is an alarm system application designed for availability, integrability, and extensibility. The NALMS development was driven by SLAC's efforts to replace the Alarm Handler, due for deprecation as a Motif-based application, and to introduce process improvements addressing hierarchy implementation overhead, limited operator engagement, and operator display integration.

Full documentation is hosted at: https://slaclab.github.io/nalms/


# Docker

This repository is packaged with tools for Docker based deployment. There are several reasons containerization is an advantageous:  

* The Kafka brokers may be straighforwardly deployed and the cluster scaled. Configurations are therefore transferable and port exposures may be configured directly on the Docker deployment.
* Contained applications may run in parallel, facilitating blue/green deployment workflows. 

This docker application consists of the following containers:

* Zookeeper
* Kafka
* Phoebus Alarm Server
* Phoebus Alarm Logger
* Elasticsearch
* Grafana
* An Example IOC
* Cruise Control

Docker-compose may be used to run a packaged example with all components.
```
$ docker-compose up
```

Once running, the cruise control dashboard is available at http://localhost:9090, and the grafana alarm log dashboard is available at http://localhost:3000. To access the alarm log dashboard, log in using the grafana default accounts, username: admin, password: admin. The alarm logger may need to be restarted if using docker compose, due to a slight delay in the alarm server startup. 

Operations on the IOC for this demo can be performed by running caputs/cagets after attaching to the running container. 
