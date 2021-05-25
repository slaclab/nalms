# Tools

## Alarm Configuration Editor Tool

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
$ pydm alarm-tree-editor/editor.py
```

## PyDM widgets

PyDM widgets are in the development stage and relevant code is hosted in [pydm-nalms](https://github.com/slaclab/pydm-nalms). The integration of the datasource with PyDM is largely dependent upon the development of [entrypoints](https://github.com/slaclab/pydm/issues/720) for datasources. This feature request is still open and therefore intermediate use will require modifying PyDM directly or monkeypatching... 