# NALMS

The Next ALarM System...


# Docker system
The entirety of the NALMS services may be run using the `docker-compose.yml` packed in this repository. Significant simplifications might be made to these docker images (moving to more modern OS etc.); however, I've tried to replicate the RHEL 7 design requirement as closely as possible to demonstrate the istallation outlined in the design document. 

To run the full application, first pull the relevant images:

```
$ docker pull centos/python-38-centos7
$ docker pull docker.elastic.co/elasticsearch/elasticsearch:6.8.16

```

