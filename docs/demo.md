# Demo
This demo is intended for running on SLAC's RHEL7 dev server. NALMS uses named Docker containers and so this demo cannot be run if the existing demo containers are running. The commands below are run using the existing RHEL7 docker installation, therefore requiring sudo. In the future, this installation should be changed for user use other than root. 

Additionally, given that $NALMS_HOME is defined (in afs: $PACKAGE_TOP/nalms/current), the command line tool `bash ${NALMS_HOME}/cli/nalms` may be used directly by modifying the path:
```
$ export PATH=$NALMS_HOME/cli:$PATH
```

For client use: $NALMS_CLIENT_JAR must be defined as well as $NALMS_HOME. The client launch script creates a templated configuration file for the client from a template provided in $NALMS_HOME. 

During this demo, we set up all services using the package CLI and the Docker images. On aird-b50-srv01, this can be sourced using: 


```
$ source ${PACKAGE_TOP}/nalms/setup/aird-b50-srv01/dev.env
```

Start the demo ioc:

```
$ tmux new -s demo-ioc
$ softIoc -d examples/demo/demo.db 
```
Exit the tmux window using: `Ctr + b + d`

Set up Kafka cluster (from repo root): 

```
$ sudo -E bash nalms start-zookeeper 
$ sudo -E bash nalms start-kafka-broker --broker 0
```

Start cruise-control:
```
$ sudo -E bash nalms start-cruise-control
```
Navigate to [http://localhost:9090](http://localhost:9090) to view the Cruise Control interface and monitors of the Kafka cluster. 


Start the Phoebus alarm server: (Note: launch requires the absolute path of the configuration file for docker volume mount)


```
$ sudo -E nalms start-alarm-server Demo ${NALMS_HOME}/examples/demo/demo.xml
```


Next, start the Elasticsearch service: 
```
$ sudo -E nalms start-elasticsearch
```

Wait at least a minute before starting elasticsearch. The templates for the indices must be created before starting. Start the Phoebus alarm logger:
```
$ sudo -E nalms start-alarm-logger Demo ${NALMS_HOME}/examples/demo/demo.xml
```

Navigate to `Applications > Alarm > Alarm Tree` to view the process variable values. 

Launch the Grafana instance:
```
$ sudo -E nalms start-grafana --config Demo
```

Launch firefox and navigate to [http://localhost:3000](http://localhost:3000). Enter user=admin, password=admin into the login. Select AlarmLogs from the available dashboards.


Launch the Phoebus client:
```
$ sudo -E nalms start-phoebus-client Demo
```


All containers may be stopped using the ids listed with:

```
$ sudo docker ps
$ sudo docker stop {containter_id}
```

Remove lingering containers...
```
 $ sudo docker container rm
```

You can access and exit the demo ioc by attaching to the tmux session:

```
$ tmux attach -t demo-ioc
```
Exiting the softIOC, and `Ctrl + b + d`.