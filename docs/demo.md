# Demo

Environment file included in examples
The configuration files packaged in ... correspond the environment variables defined in this file

First, find your IP addess by running: 

```
$ ifconfig en0 | grep -i mask
```
Set the HOST_IP environment variable to the first inet entry:

```
$ export HOST_IP={inet address}
```

Source the demo environment:

```
$ source examples/demo/demo.env
```

Edit each file in `/examples/demo/config`, setting the bracketed entries to the corresponding entries and addresses outlined in the environment file (and host ip).  For the file `/examples/demo/config/grafana_datasources/all.yml` use `localhost` in the elasticsearch url (datasource operates from client).


Start the demo ioc:

```
$ cd examples/demo
$ docker compose up -d
```

Set up Kafka cluster (from repo root): 

```
$ cd - 
$ bash cli/nalms start-zookeeper 
$ bash cli/nalms start-kafka-broker
```

Start cruise-control:
```
$ bash cli/nalms start-cruise-control
````
Navigate to [http://localhost:9090](http://localhost:9090) to view the Cruise Control interface and monitors of the Kafka cluster. 


Start the Phoebus alarm server: (Note: launch requires the absolute path for docker volume mount)


```
$ bash cli/nalms start-alarm-server Demo $(pwd)/examples/demo/demo.xml
```


Next, start the Elasticsearch service: 
```
$ bash cli/nalms start-elasticsearch
```

Wait at least a minute before starting elasticesarch. The templates for the indices must be created before starting. Start the Phoebus alarm logger:
```
$ bash cli/nalms start-alarm-logger Demo $(pwd)/examples/demo/demo.xml
```


Launch the Phoebus client:
```
$ bash cli/nalms start-phoebus-client
```

Navigate to `Applications > Alarm > Alarm Tree` to view the process variable values. 

Launch the Grafana instance:
```
$ bash cli/nalms start-grafana
```

Navigate to [http://localhost:3000](http://localhost:3000). Enter user=admin, password=admin into the login. Select AlarmLogs from the available dashboards.


All containers may be stopped using the ids listed with:

```
$ docker ps
$ docker stop {containter_id}
```

Remove lingering containers...
```
 $ docker-compose rm
```

## Client

In order to use the client in this framework connections from docker must be allowed. One option (insecure) is temporarily disabling the following:

```
$ xhost + local:root
```

Then after:

```
$ xhost - local:root
``