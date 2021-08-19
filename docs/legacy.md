# Converting from ALH

The ALH -> Phoebus Python (>=3.7) conversion tool is handled by a package currently defined in the `nalms-tools` directory. 

```
$ cd nalms-tools
$ pip install -e .
```

The entry point console script is then available with:

```
$ convert-alh config_name input_filename output_filename
```

Several features of the ALH cannot be translated to Phoebus configurations and are deprecated in NALMS. These are the ALIAS, ACKPV, SEVRCOMMAND, STATCOMMAND, and BEEPSEVERITY ALH configuration entries. The conversion script will print any failures to STDOUT.

At present, ALH inclusions will parsed and reserialized into a single Phoebus XML configuration file. Future CS-Studio development with include the ability to accomodate file inclusions within the tree structure such that nested files may be similarly structured.

## Subsystem demo
In this demo we will convert an existing ALH configuration file into a suitable Phoebus XML configuration file using the packaged nalms CLI. This demo is written to run using the development environment on aird-b50-srv01 and assumes already running kafka cluster, elasticsearch, and Grafana.

Source the appropriate environment:
```
$ source ${PACKAGE_TOP}/nalms/setup/aird-b50-srv01/demo.env
```

Use the top level subsystem ALH config file to create the XML file:
```
$ nalms convert-alh ${TOOLS}/AlarmConfigsTop/mgnt/prod/lcls/alh/mgnt.alhConfig mgnt.xml Mgnt
```

Launch the Phoebus alarm server for the configuration:
```
# must use full path to the configuration file
$ nalms start-alarm-server Mgnt $(pwd)/mgnt.xml
```

Launch the Phoebus alarm logger for the configuration:
```
# must use full path to the configuration file
$ nalms start-alarm-logger Mgnt $(pwd)/mgnt.xml
```

Launch the client to view the alarm tree:
```
$ nalms start-phoebus-client Mgnt
```

Now, set up for use with Grafana. Add to the Grafana datasource:
```
$ nalms add-grafana-datasource Mgnt
```

This appended the datasource to the file $NALMS_GRAFANA_DATASOURCE_FILE. Now, create the Grafana dashboard:
```
$ nalms build-grafana-dashboard Mgnt
```

This created a dashboard for the Demo configuration in $NALMS_GRAFANA_DASHBOARD_DIR. Relaunch grafana:

```
$ docker container stop nalms_grafana
$ docker container rm nalms_grafana
$ nalms start-grafana
```
