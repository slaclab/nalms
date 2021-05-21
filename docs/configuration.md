# Configuration


An attempt has been made to centralize configurations for streamlined deployments.
All configuration files are housed in config.
Sufficiently abstracted for deployments based on environment variables.


## Elasticsearch

The elasticsearch configuration is defined using the files in `config/elasticsearch`. The configuration is indicated to the elasticsearch server during launch by the  

For security reasons, the elasticsearch service requires a user other than root so an elasticsearch user must be created with appropriate permissions




## Kafka


## Phoebus Alarm Server


## Phoebus Alarm Logger