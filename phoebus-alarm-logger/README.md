# Phoebus Alarm Services

NALMS utilizes CS-Studio's [Phoebus](https://github.com/ControlSystemStudio/phoebus) alarm services for for the translation of EPICS alarm events into Kafka messages and the translation of Kafka messages into Elasticsearch entries. This folder defines a Docker image for containerized deployment, tools for interacting with a deployed container, and python scripts for the conversion of legacy ALH files into Phoebus XML formatted configurations. 

The Phoebus alarm tools may be downloaded from latest release, or built locally with OpenJDK >= 11 and maven using the following:

```
$ git clone https://github.com/ControlSystemStudio/phoebus.git
$ cd phoebus
$ mvn install -pl services/alarm-server -am
$ mvn install -pl services/alarm-logger -am
```

Once installed, the `ALARM_SERVER_JAR` and `ALARM_LOGGER_JAR` environment variables should be set to point to the files in `phoebus/services/alarm-server/target/` and `phoebus/services/alarm-logger/target/`, respectively. 

## Configuration

The Phoebus Alarm server and logger configuration properties files define settings to be used by the services. This includes the EPICS configuration and Elasticsearch host configuration. A full preference list can be found in the CS-Studio [documentation](https://control-system-studio.readthedocs.io/en/latest/preference_properties.html)

Configuration files for use inside the containerized deployment are housed in the `config` directory. 

## Tools

### ALH legacy conversion

ALH files may be converted to Phoebus configuration files using the `alh_conversion.py` script (Python >= 3.7). 

```
$ python alh_conversion.py config_name input_filename output_filename
```

Several features of the ALH cannot be translated to Phoebus configurations and are deprecated in NALMS. These are the ALIAS, ACKPV, SEVRCOMMAND, STATCOMMAND, amd BEEPSEVERITY ALH configuration entries. The conversion script will print any failures to STDOUT.

### Command line tools

The `cli` directory houses a utility interface for interacting with the Phoebus alarm services. Use of these tools requires running `setup.py` for registering console entry scripts for the python tools (these tools should eventually be moved to a designated python package and out of this directory). Additionally, use of the interface requires the definition of several environment variables:

| Variable                 | Description                                                   |
|--------------------------|---------------------------------------------------------------|
| JAVA_HOME                | File system path of JDK installation                          |
| ALARM_LOGGER_PROPERTIES  | Alarm logger properties file                                  |
| ALARM_SERVER_SETTINGS    | Alarm server properties file                                  |
| ALARM_SERVER_JAR         | Path to alarm server jar file                                 |
| ALARM_LOGGER_JAR         | Path to the alarm logger jar file                             |
| EPICS_BASE               | OPTIONAL: Path to EPICS  installation if hosting summary ioc  |


## Docker image

The docker image packed in this folder defines an centos 7 image containing the Phoebus alarm server and the Phoebus alarm logger. Using the image name `phoebus`:

```
$ docker build -t phoebus .
```

In an attempt to abstract some of the docker interface commands, they've been packaged under `scripts` and all assume the `phoebus` target identifier for the docker image for compatibility with the docker-compose application packaged in the project root. 