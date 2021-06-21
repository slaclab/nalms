# Next ALarM Sytem

NALMS is an alarm system application designed for availability, integrability, and extensibility. The NALMS development was driven by SLAC's efforts to replace the Alarm Handler, due for deprecation as a Motif-based application, and to introduce process improvements addressing hierarchy implementation overhead, limited operator engagement, and operator display integration.


# Docker

This repository is packaged with tools for Docker based deployment. There are several reasons containerization is an advantageous:
* The Kafka brokers may be straighforwardly deployed and the cluster scaled to multiple machines. Configurations are therefore transferable and port exposures may be configured directly on the Docker deployment. 
* Contained applications may run in parallel, facilitating blue/green deployment workflows. 