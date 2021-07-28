# Configuration

Alarm configurations are XML files organized with component (group), and PV tags. Component tags accept specifications for guidance, display, commands, and automated actions. Configuration options for groups are defined below:

| Configuration tag        | Description                                                                               |
|--------------------------|-------------------------------------------------------------------------------------------|
| guidance                 | Message explaining the meaning of an alarm to the user and who to contact for resolution  |
| display                  | Link to the associated control system display                                             |
| command                  | Commands that may be invoked from user interfaces                                         |
| automated_action         | Action performed when a group enters and remains in an active alarm state.                |

PV tags accept specifications for enabling, latching, annunciating, description, delay, commands, associated displays, guidance, alarm count, filter, and automated actions. A configuration schema is provided [here](https://github.com/slaclab/nalms/blob/main/phoebus-alarm-server/files/phoebus_alarm_server.xsd).

| Configuration tag        | Description                                                                               |
|--------------------------|-------------------------------------------------------------------------------------------|
| guidance                 | Message explaining the meaning of an alarm to the user and who to contact for resolution  |
| display                  | Link to the associated control system display                                             |
| command                  | Commands that may be invoked from user interfaces                                         |
| automated_action         | Action performed when a group enters and remains in an active alarm state.                |
| description              | Text displayed in the alarm table when the alarm is triggered                             |
| delay                    | Alarm will be triggered if the PV remains in alarm for at least this time                 |
| enabled                  | If false, ignore the value of this PV                                                     | 
| latching                 | Alarms will latch to the highest severity until the alarm is acknowledged and cleared.    |
|                          | If false, alarm may recover without requiring acknowledgment                              |
| count                    | If the trigger PV exhibits a not-OK alarm severity for more than ‘count’ times within the |
|                          | alarm delay, recognize the alarm                                                          |
| filter                   | An optional expression that can enable the alarm based on other PVs.                      |

![Components](img/server_sequence.png)


## Alarm Configuration Editor Tool

![tree editor](img/tree_editor.png)

The alarm configuration editor is be a PyQt tool for designing the alarm configuration XML files for use with the Phoebus alarm server as outlined in Section 3.2. Alternatively, any XML editor may be used to build the document directly. The editor has the following features:  
* Ability to edit alarm hierarchy, create new groups and new PVs 
* Ability to define all configuration items
* Optional conversion and import of legacy ALH files 

Requirements for running the editor are given in the `environment.yml` file bundled with the NALMS package. This environment can be created with conda using:
```
$ conda env create -f environment.yml
```

And subsequently activated:
```
$ conda activate nalms
```

If choosing to build your own environment without conda, the requirements follow:
  - python =3.8
  - treelib
  - lxml
  - pyqt5
  - kafka-python
  - pydm

PyDM dependence will eventually be dropped.   

To launch the editor run:
```
$ bash cli/nalms launch-editor
```