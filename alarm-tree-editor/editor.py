import os
import json
import sys
import importlib.util
import time

from kafka import KafkaConsumer
from qtpy.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QTreeView,
    QCheckBox,
    QAbstractItemView,
    QSpacerItem,
    QSizePolicy,
    QLineEdit,
    QToolBar,
    QAction,
    QDialogButtonBox,
    QPushButton,
    QMenu,
    QGridLayout,
    QLabel,
    QApplication,
    QFileDialog,
)
from qtpy.QtCore import (
    Qt,
    Slot,
    QModelIndex,
    QItemSelection,
    QItemSelectionModel,
    QObject,
    Signal,
    Property,
    QAbstractItemModel,
    QSize,
)
from qtpy.QtGui import QBrush, QColor, QIntValidator

import xml.etree.ElementTree as ET

from functools import partial
from pydm.widgets.base import PyDMWritableWidget
from pydm import Display


# ATTEMPT IMPORT OF CONVERSION
NALMS_TOP = os.environ.get("NALMS_TOP")
if not NALMS_TOP:
    print("$NALMS_TOP must be defined.")
    sys.exit()
else:
    spec = importlib.util.spec_from_file_location(
        "module.name", f"{NALMS_TOP}/tools/alh_conversion.py"
    )
    alh_conversion = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(alh_conversion)


class AlarmTreeItem(QObject):
    data_changed = Signal()
    send_value_signal = Signal(bool)

    def __init__(
        self,
        label="",
        parent=None,
        address="",
        description="",
        enabled=True,
        latching=False,
        annunciating=False,
        count=None,
        delay=None,
        is_group=False,
        alarm_filter=None,
        alarm_configuration=None,
    ):
        # type: (str, QObject, str, str, bool, bool, bool, int, int, bool, str, str)

        super(AlarmTreeItem, self).__init__()
        self.alarm_configuration = alarm_configuration
        self.parent_item = parent

        self.children = []
        self.channel = None
        self.address = address
        self._channels = []
        self.severity = None
        self.status = None

        self.description = description
        self.enabled = enabled
        self.latching = latching
        self.count = count
        self.delay = delay
        self.label = label
        self.annunciating = annunciating
        self.alarm_filter = alarm_filter
        self.is_group = is_group
        self.tickets = "CATER: 1029"

        if hasattr(self, "channels"):
            self.destroyed.connect(functools.partial(widget_destroyed, self.channels))

    # For model logic
    def child(self, row):
        """# type: (row: int)"""
        return self.children[row] if len(self.children) > row else []

    def child_count(self):
        return len(self.children)

    def child_number(self):
        if self.parent_item != None:
            return self.parent_item.children.index(self)
        return 0

    def column_count(self):
        return 1

    def create_child(self, position, child_data):
        # type: (int, dict)
        child = AlarmTreeItem.from_dict(
            child_data, parent=self, alarm_configuration=self.alarm_configuration
        )
        self.children.insert(position, child)
        if not self.is_group:
            self.is_group = True

        return child

    def insert_child(self, position, child):
        # type: (int, QObject)
        self.children.insert(position, child)
        if not self.is_group:
            self.is_group = True
        return child

    def parent(self):
        return self.parent_item

    def remove_child(self, position):
        # type: (int)
        item = self.children.pop(position)

        return item

    def assign_parent(self, parent):
        # type: (QObject)
        self.parent_item = parent

    @property
    def label(self):
        return self._label

    @label.setter
    def label(self, label):
        self._label = label

    @property
    def address(self):
        if self.channel is None:
            return None
        return self.channel.address

    @address.setter
    def address(self, new_address):
        # type: (str)
        self._address = new_address
        if new_address is None or len(str(new_address)) < 1:
            self.channel = None
            return

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, description):
        # type: (str)
        self._description = description

    @property
    def enabled(self):
        return self._enabled

    @enabled.setter
    def enabled(self, enabled):
        # type: (bool)
        self._enabled = enabled

    @property
    def latching(self):
        return self._latching

    @latching.setter
    def latching(self, latching):
        # type: (bool)
        self._latching = latching

    @property
    def annunciating(self):
        return self._annunciating

    @annunciating.setter
    def annunciating(self, annunciating):
        # type: (bool)
        self._annunciating = annunciating

    @property
    def delay(self):
        return self._delay

    @delay.setter
    def delay(self, delay):
        # type: (int)
        self._delay = delay

    @property
    def count(self):
        return self._count

    @count.setter
    def count(self, count):
        # type: (int)
        self._count = count

    @property
    def alarm_filter(self):
        return self._filter

    @alarm_filter.setter
    def alarm_filter(self, alarm_filter):
        # type: (str)
        self._filter = alarm_filter

    # command

    # automated action

    # Update functions
    @Slot(int)
    def receiveNewSeverity(self, new_severity):
        # type: (int)
        self.severity = new_severity
        self.data_changed.emit()

    @Slot(str)
    def receiveNewValue(self, new_value):
        # type: (str)
        self.status = new_value
        self.data_changed.emit()

    @Slot(bool)
    def connectionStateChanged(self, connected):
        # type: (bool)
        pass

    @Slot(bool)
    def acknowledge(self):
        self.send_value_signal.emit(True)

    @Slot(bool)
    def unacknowledge(self):
        self.send_value_signal.emit(False)

    # For recreation
    def to_dict(self):
        return {
            "label": self.label,
            "address": self.address,
            "description": self.description,
            "enabled": self.enabled,
            "latching": self.latching,
            "count": self.count,
            "annunciating": self.annunciating,
            "delay": self.delay,
            "alarm_filter": self.alarm_filter,
        }

    @classmethod
    def from_dict(cls, data_map, parent=None, alarm_configuration=None):
        # type: (dict, QObject)
        if data_map:
            label = data_map.get("label")
            address = data_map.get("address")
            description = data_map.get("description")
            enabled = data_map.get("enabled")
            latching = data_map.get("latching")
            count = data_map.get("count")
            delay = data_map.get("delay")
            annunciating = data_map.get("annunciating")
            alarm_filter = data_map.get("alarm_filter")

            return cls(
                label,
                parent=parent,
                address=address,
                description=description,
                enabled=enabled,
                latching=latching,
                annunciating=annunciating,
                count=count,
                delay=delay,
                alarm_filter=alarm_filter,
                alarm_configuration=alarm_configuration,
            )

        else:
            return cls(None, parent=parent)

    # distinguish groups/pvs
    def mark_group(self):
        self.is_group = True

    def mark_pv(self):
        self.is_group = False


class AlarmTreeModel(QAbstractItemModel):
    def __init__(self, tree, parent=None):
        super(AlarmTreeModel, self).__init__(parent)
        self._nodes = []
        self._tree = tree
        self._root_item = AlarmTreeItem(self._tree.config_name)
        self._nodes.append(self._root_item)

    def clear(self):
        self._nodes = []
        self._root_item = None

    def columnCount(self, parent=QModelIndex()):
        # type: (QModelIndex)
        return self._root_item.column_count()

    def rowCount(self, parent=QModelIndex()):
        # type: (QModelIndex)
        parent = self.getItem(parent)

        return parent.child_count()

    def data(self, index, role):
        # type: (QModelIndex, Qt.ItemDataRole)
        if not index.isValid():
            return None

        item = self.getItem(index)

        if role in [Qt.DisplayRole, Qt.EditRole]:
            return item.label

        if role == Qt.TextColorRole:

            # no alarm
            if item.severity == 0:
                return QBrush(Qt.black)

            # minor alarm
            elif item.severity == 1:
                return QBrush(Qt.yellow)

            # major alarm
            elif item.severity == 2:
                return QBrush(Qt.red)

            # invalid
            elif item.severity == 3:
                return QBrush(GtGui.QColor(102, 0, 255))

            # disconnected
            elif item.severity == 4:
                return QBrush(Qt.black)

            # major/minor ack
            elif item.severity == 5:
                return QBrush(QColor(86, 86, 86))

            # major/minor ack
            elif item.severity == 6:
                return QBrush(QColor(86, 86, 86))

            # undefined
            elif item.severity == 7:
                return QBrush(Qt.black)

            # undefined ack
            elif item.severity == 8:
                return QBrush(QColor(86, 86, 86))

    def flags(self, index):
        # type: (QModelIndex)
        if not index.isValid():
            return Qt.ItemIsEnabled

        return (
            Qt.ItemIsEditable
            | Qt.ItemIsEnabled
            | Qt.ItemIsSelectable
            | Qt.ItemIsDragEnabled
            | Qt.ItemIsDropEnabled
        )

    def getItem(self, index):
        # type: (QModelIndex)
        if index.isValid():
            item = index.internalPointer()
            if item:
                return item

        else:
            return self._root_item

    def index(self, row, column, parent=QModelIndex()):
        # type: (int, int, QModelIndex)
        if parent.isValid() and parent.column() != 0:
            return QModelIndex()

        parent = self.getItem(parent)
        childItem = parent.child(row)
        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QModelIndex()

    def insertRow(self, position, parent=QModelIndex(), child_data=None):
        # type: (int, QModelIndex, dict)
        if not parent:
            return False

        parent_item = self.getItem(parent)

        self.beginInsertRows(parent, position, position)
        child = parent_item.create_child(position, child_data=child_data)
        child.data_changed.connect(self.update_values)

        if not parent_item.is_group:
            parent_item.mark_group()

        self.addNode(child)
        self.endInsertRows()

        return True

    def removeRow(self, position, parent=QModelIndex()):
        # type: (int, QModelIndex)

        parent_item = self.getItem(parent)

        self.beginRemoveRows(parent, position, position)
        item = parent_item.remove_child(position)
        self.removeNode(item)

        if not parent_item.child_count():
            parent_item.mark_pv()

        # disconnect
        item.data_changed.disconnect(self.update_values)
        self.endRemoveRows()

        return True

    def parent(self, index):
        # type: (QModelIndex)
        if not index.isValid():
            return QModelIndex()

        childItem = self.getItem(index)
        parent = childItem.parent()

        if not parent:
            return QModelIndex()

        if parent == self._root_item:
            return QModelIndex()

        return self.createIndex(parent.child_number(), 0, parent)

    def setData(self, index, data, role):
        # type: (QModelIndex, str, Qt.ItemDataRole)
        """
        QAbstractModel uses setData for double click line edits.
        """
        if data:
            self.set_data(index, label=data)

        return True

    def set_data(
        self,
        index,
        role=Qt.EditRole,
        label=None,
        description=None,
        address=None,
        count=None,
        delay=None,
        latching=None,
        enabled=None,
        annunciating=None,
        alarm_filter=None,
    ):
        # type: (QModelIndex, Qt.ItemDataRole, str, str, str, int, int, bool, bool, bool, str)
        if role != Qt.EditRole:
            return False

        item = self.getItem(index)

        if label:
            item.label = label

        if address:
            item.address = address

        if count:
            item.count = count

        if delay:
            item.delay = delay

        if latching is not None:
            item.latching = latching

        if enabled is not None:
            item.enabled = enabled

        if annunciating is not None:
            item.annunciating = annunciating

        if description:
            item.description = description

        if alarm_filter:
            item.alarm_filter = alarm_filter

        self.dataChanged.emit(index, index)

        return True

    @Slot()
    def update_values(self):
        self.layoutChanged.emit()

    # drag/drop
    def supportedDropActions(self):
        return Qt.MoveAction

    def mimeTypes(self):
        return ["text/plain"]

    def mimeData(self, indexes):
        # type: (List[QModelIndex])
        """Function used for preparing tree data for drag+drop. Preserves the hierarchy of the dropped item.

        """
        mimedata = QMimeData()
        item = self.getItem(indexes[0])

        # track representations and hierarchal relationships
        hierarchy_builder = MimeHierarchyTool()
        hierarchy_rep = hierarchy_builder.build_config(item)

        data = json.dumps(hierarchy_rep)
        mimedata.setText(data)
        return mimedata

    def dropMimeData(self, mimedata, action, row, column, parentIndex):
        """Function used for dropping tree items. Item hierarchy within dragged groups is preserved. 

        """
        if action == Qt.IgnoreAction:
            return True

        prior_index = self._tree.selectionModel().currentIndex()
        selected_parent = self.parent(prior_index)
        selected_row = prior_index.row()

        self.removeRow(selected_row, parent=selected_parent)

        dropped_data = json.loads(mimedata.text())

        # handle items
        new_nodes = []
        parent_item = self.getItem(parentIndex)
        for i, rep in enumerate(dropped_data):
            data_rep = rep[0]
            parent_idx = rep[1]

            if i == 0:
                base_insert = parent_item.create_child(0, child_data=data_rep)
                base_insert.data_changed.connect(self.update_values)
                self._nodes.append(base_insert)

                # track for local indices
                new_nodes.append(base_insert)

            else:
                # get nodes parent
                parent_node = new_nodes[parent_idx]
                new_node = parent_node.create_child(0, child_data=data_rep)
                new_node.data_changed.connect(self.update_values)
                self._nodes.append(new_node)
                # track for local indices
                new_nodes.append(new_node)

        # trigger layout changed signal
        self.update_values()

        # populate children
        return True

    def addNode(self, item):
        # type: (AlarmTreeItem)
        self._nodes.append(item)

    def removeNode(self, node):
        # type: (AlarmTreeItem)
        self._nodes.remove(node)
        if len(self._nodes) < 1:
            pass

    def getNodes(self):
        hierarchy = self._get_hierarchy()
        return hierarchy

    def _get_hierarchy(self):
        hierarchy = []
        for i, node in enumerate(self._nodes):
            if node.parent_item is None:
                parent_idx = None
            else:
                parent_idx = self._nodes.index(node.parent_item)

            rep = [node.to_dict(), parent_idx]
            hierarchy.append(rep)

        return json.dumps(hierarchy)

    def import_hierarchy(self, hierarchy):
        # type: (List[list])
        """
        Accepts a list of node representations in the list format [dictionary representation, parent]
        """
        self.clear()
        # trigger layout changed signal

        config_name = None

        for i, node in enumerate(hierarchy):
            node_data = node[0]
            parent_idx = node[1]

            alarm_item = AlarmTreeItem.from_dict(
                node[0], alarm_configuration=config_name
            )
            self._nodes.append(alarm_item)

            if parent_idx is not None:
                alarm_item.assign_parent(self._nodes[node[1]])
                self._nodes[node[1]].insert_child(-1, alarm_item)

            if i == 0:
                self._root_item = alarm_item
                self._tree.config_name = alarm_item.label
                config_name = alarm_item.label

        for node in self._nodes:
            node.data_changed.connect(self.update_values)
            if node.channel is not None:
                node.channel.connect()

        # trigger layout changed signal
        self.update_values()

    # configuration handling
    def import_configuration_from_kafka(self, alarm_configuration):

        # quick setup + parse of kafka compacted topic to construct tree....
        kafka_url = os.getenv("KAFKA_URL")

        consumer = KafkaConsumer(
            alarm_configuration,
            bootstrap_servers=[kafka_url],
            enable_auto_commit=True,
            key_deserializer=lambda x: x.decode("utf-8"),
        )

        while not consumer._client.poll():
            continue
        consumer.seek_to_beginning()

        key_paths = []
        keys = {}

        start = time.time() * 1000
        last_time = -100000
        while last_time < start:
            message = consumer.poll(100)
            for topic_partition in message:
                for record in message[topic_partition]:
                    last_time = record.timestamp
                    if last_time < start:
                        key_path = record.key.split(":/")[1]

                        # track key path
                        if key_path not in key_paths:

                            key_paths.append(key_path)
                            key_split = key_path.split("/")

                            if len(key_split) not in keys:
                                keys[len(key_split)] = [
                                    {"key_path": key_path, "key_split": key_split}
                                ]

                            else:
                                keys[len(key_split)].append(
                                    {"key_path": key_path, "key_split": key_split}
                                )

            if not message:
                break

        nodes = []
        hierarchy = []

        max_depth = max(keys.keys())
        for depth in range(1, max_depth + 1):

            for key in keys[depth]:
                data = {
                    "label": key["key_split"][-1],
                    "address": "alarm://{}".format(key["key_path"]),
                }

                nodes.append(key["key_path"])

                if depth > 1:
                    parent = "/".join(key["key_split"][:-1])
                    parent_idx = nodes.index(parent)

                else:
                    parent_idx = None

                rep = [data, parent_idx]
                hierarchy.append(rep)

        # import
        self.import_hierarchy(hierarchy)


class MimeHierarchyTool:
    """Tool for constructing tree hierarchies for drag and drop transfers

    """

    def __init__(self):
        self.hierarchy = []

    def build_config(self, node):
        """Governing logic for building/organizing the hierarchy.

        """
        # index, parent
        self.hierarchy.append([node.to_dict(), None])

        for node in node.children:

            # if children, is a group
            if node.child_count():
                self._handle_group_add(node, 0)

            else:
                self._handle_pv_add(node, 0)

        return self.hierarchy

    def _handle_group_add(self, group, parent_index):
        # type: (AlarmTreeItem, QModelIndex)
        """Handles group additions to hierarchy and their subsequent children.

        """
        node_index = len(self.hierarchy) - 1

        self.hierarchy.append([group.to_dict(), parent_index])

        # don't add properties for group
        for child in group.children:

            if child.child_count():
                self._handle_group_add(child, node_index)

            else:
                self._handle_pv_add(child, node_index)

    def _handle_pv_add(self, pv, parent_index):
        # type: (AlarmTreeItem, QModelIndex)
        """Handles pv additions to hierarchy.

        """
        node_index = len(self.hierarchy) - 1
        self.hierarchy.append([pv.to_dict(), parent_index])


class PyDMAlarmTree(QTreeView, PyDMWritableWidget):
    def __init__(self, parent, init_channel=None, config_name=None, edit_mode=False):
        super(PyDMAlarmTree, self).__init__()

        QTreeView.__init__(self, parent)
        PyDMWritableWidget.__init__(self)

        self.setup_ui()

        self.setStyleSheet("background-color: rgb(179, 179, 179)")

        self._nodes = []

        self.config_name = config_name

        self.tree_model = AlarmTreeModel(self)
        self.setModel(self.tree_model)
        self.edit_mode = edit_mode

        self.setContextMenuPolicy(Qt.CustomContextMenu)

        if not edit_mode:
            self.customContextMenuRequested.connect(self._open_menu)

        self.expandAll()

    def setup_ui(self):
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.setDragDropOverwriteMode(False)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setHeaderHidden(True)
        self.setColumnWidth(0, 160)
        self.setColumnWidth(1, 160)
        self.setColumnWidth(2, 160)

    def get_configuration_name(self):
        return self.config_name

    def set_configuration_name(self, config_name):
        self.config_name = config_name

    configuration_name = Property(
        str, get_configuration_name, set_configuration_name, designable=False
    )

    def _open_menu(self, point):
        menu = QMenu()
        index = self.indexAt(point)
        item = self.model().getItem(index)
        self.value_action = QAction(item.status, self)
        self.value_action.setEnabled(False)

        menu.addAction(self.value_action)

        self.ticket_action = QAction(item.tickets, self)
        self.ticket_action.setEnabled(False)

        menu.addAction(self.ticket_action)

        self.acknowledge_action = QAction("Acknowledge", self)
        self.acknowledge_action.triggered.connect(
            partial(self._acknowledge_at_index, index)
        )
        menu.addAction(self.acknowledge_action)

        self.remove_acknowledge_action = QAction("Remove Acknowledge", self)
        self.remove_acknowledge_action.triggered.connect(
            partial(self._remove_acknowledge_at_index, index)
        )
        self.remove_acknowledge_action.setEnabled(False)

        menu.addAction(self.remove_acknowledge_action)

        menu.exec_(self.viewport().mapToGlobal(point))

    def _acknowledge_at_index(self, index):
        item = self.tree_model.getItem(index)
        item.acknowledge()

    def _remove_acknowledge_at_index(self, index):
        item = self.tree_model.getItem(index)
        item.unacknowledge()

    def mousePressEvent(self, event):
        self.clearSelection()
        self.selectionModel().reset()
        QTreeView.mousePressEvent(self, event)


class PhoebusConfigTool:
    """
    Tool for building and parsing Phoebus configuration files

    """

    def __init__(self):
        self._nodes = []
        self._tree = None
        self._root = None

    def _clear(self):
        self._tree = None
        self._root = None
        self._nodes = []

    def parse_config(self, filename):
        """
        Parses a configuration file
        """
        # clear
        self._clear()

        # parse filename
        self._tree = ET.parse(filename)
        self._root = self._tree.getroot()

        if self._root.tag == "config":
            self._config_name = self._root.attrib["name"]

            # add root item to tree
            self._nodes.append([{"label": self._config_name}, None])

            for child in self._root:
                if child.tag == "component":
                    self._handle_group_parse(child, 0)

                elif child.tag == "pv":
                    self._handle_pv_parse(child, 0)

        return self._nodes

    def _build_data(self, elem):
        data = {"label": elem.attrib.get("name")}

        for child in elem:
            if child.tag == "description":
                data["description"] = child.text

            elif child.tag == "enabled":
                data["enabled"] = child.text

            elif child.tag == "latching":
                data["latching"] = child.text

            elif child.tag == "annunciating":
                data["annunciating"] = child.text

            elif child.tag == "delay":
                data["delay"] = child.text

            elif child.tag == "count":
                data["count"] = child.text

            elif child.tag == "filter":
                data["alarm_filter"] = child.text

            elif child.tag == "command":
                pass  # TODO

            elif child.tag == "automated_action":
                pass  # TODO

        return data

    def _handle_pv_parse(self, pv, parent_idx):
        data = self._build_data(pv)
        self._nodes.append([data, parent_idx])

    def _handle_group_parse(self, group, parent_idx):
        # add group
        data = self._build_data(group)
        self._nodes.append([data, parent_idx])
        group_idx = len(self._nodes) - 1

        for child in group:
            if child.tag == "component":
                self._handle_group_parse(child, group_idx)

            elif child.tag == "pv":
                self._handle_pv_parse(child, group_idx)

    def save_configuration(self, root_node, filename):
        # disregard root and create new
        self._build_config(root_node)

        with open(filename, "wb") as f:
            file_str = ET.tostring(self._tree, encoding="utf8")
            f.write(file_str)

    def _build_config(self, root_node):
        # clear tree and start again
        self._tree = ET.ElementTree()
        self._tree = ET.Element("config", name=root_node.label)

        for node in root_node.children:

            # if children, is a group
            if node.child_count():
                self._handle_group_add(node, self._tree)

            else:
                self._handle_pv_add(node, self._tree)

    def _handle_property_add(self, elem, alarm_tree_item):

        if alarm_tree_item.enabled is not None:
            enabled = ET.SubElement(elem, "enabled")

            if alarm_tree_item.enabled:
                enabled.text = "true"

            else:
                enabled.text = "false"

        if alarm_tree_item.latching is not None:
            latching = ET.SubElement(elem, "latching")

            if alarm_tree_item.latching:
                latching.text = "true"

            else:
                latching.text = "false"

        if alarm_tree_item.annunciating is not None:
            annunciating = ET.SubElement(elem, "annunciating")

            if alarm_tree_item.annunciating:
                annunciating.text = "true"

            else:
                annunciating.text = "false"

        if alarm_tree_item.description:
            description = ET.SubElement(elem, "description")
            description.text = alarm_tree_item.description

        if alarm_tree_item.delay:
            delay = ET.SubElement(elem, "delay")
            delay.text = alarm_tree_item.delay

        if alarm_tree_item.count:
            count = ET.SubElement(elem, "count")
            count.text = alarm_tree_item.count

        if alarm_tree_item.alarm_filter:
            alarm_filter = ET.SubElement(elem, "filter")
            alarm_filter.text = alarm_tree_item.alarm_filter

    def _handle_group_add(self, group, parent):
        group_comp = ET.SubElement(parent, "component", name=group.label)

        # don't add properties for group
        for child in group.children:

            if child.child_count():
                self._handle_group_add(child, group_comp)

            else:
                self._handle_pv_add(child, group_comp)

    def _handle_pv_add(self, pv, parent):
        pv_comp = ET.SubElement(parent, "pv", name=pv.label)
        self._handle_property_add(pv_comp, pv)


class AlarmTreeEditorDisplay(Display):
    def __init__(self):
        super(AlarmTreeEditorDisplay, self).__init__()

        self.app = QApplication.instance()

        # set up the ui
        self.setup_ui()

        # allow add and remove row
        self.add_button.clicked.connect(self.insertChild)
        self.remove_button.clicked.connect(self.removeItem)
        self.remove_button.setEnabled(True)

        # connect save changes
        self.button_box.accepted.connect(self.save_property_changes)

        # upon tree view selection, change the item view
        self.tree_view.selectionModel().selectionChanged.connect(self.handle_selection)
        self.tree_view.tree_model.dataChanged.connect(self.item_change)

        self.file_dialog = QFileDialog()
        self.open_config_action = QAction("Open", self)
        self.open_config_action.triggered.connect(self.open_file)
        self.toolbar.addAction(self.open_config_action)

        self.save_config_action = QAction("Save", self)
        self.save_config_action.triggered.connect(self.save_configuration)
        self.toolbar.addAction(self.save_config_action)

        # update configuration name
        self.tree_label.editingFinished.connect(self._update_config_name)

        # default open size
        self.resize(800, 600)

        self.config_tool = PhoebusConfigTool()

    def setup_ui(self):
        self.main_layout = QGridLayout()
        self.setLayout(self.main_layout)

        # add toolbar
        self.toolbar = QToolBar()
        self.main_layout.setMenuBar(self.toolbar)

        # create the tree view layout and add/remove buttons
        self.tree_view_layout = QVBoxLayout()
        self.tree_view = PyDMAlarmTree(self, config_name="UNITITLED", edit_mode=True)
        self.tree_view.setEditTriggers(QAbstractItemView.DoubleClicked)
        self.tree_view.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tree_view.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tree_view.setHeaderHidden(True)

        # Drag/drop
        self.tree_view.setDragDropMode(QAbstractItemView.InternalMove)
        self.tree_view.setDragEnabled(True)
        self.tree_view.setAcceptDrops(True)

        # view sizing
        self.tree_view.setColumnWidth(0, 160)
        self.tree_view.setColumnWidth(1, 160)
        self.tree_view.setColumnWidth(2, 160)

        # lable for tree view
        configuration_indicator = QLabel("Configuration:")
        self.tree_label = QLineEdit("Untitled")

        self.tree_label_layout = QHBoxLayout()
        self.tree_label_layout.addWidget(configuration_indicator)
        self.tree_label_layout.addWidget(self.tree_label)

        self.tree_view_layout.addLayout(self.tree_label_layout)
        self.tree_view_layout.addWidget(self.tree_view)

        # add/ remove buttons
        self.add_remove_layout = QHBoxLayout()
        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.add_remove_layout.addItem(spacer)
        self.add_button = QPushButton("New", self)
        self.add_remove_layout.addWidget(self.add_button)
        self.remove_button = QPushButton("Remove", self)
        self.add_remove_layout.addWidget(self.remove_button)
        self.tree_view_layout.addLayout(self.add_remove_layout)

        # add the tree view to the window
        self.main_layout.addLayout(self.tree_view_layout, 0, 0)

        # crate property view
        self.property_layout = QVBoxLayout()
        self.property_label_layout = QHBoxLayout()
        self.property_label_layout.addWidget(QLabel("Alarm Properties"))
        self.property_layout.addLayout(self.property_label_layout)

        self.property_view_layout = QGridLayout()

        # add label
        self.label_edit = QLineEdit()
        self.property_view_layout.addWidget(QLabel("LABEL"), 1, 0)
        self.property_view_layout.addWidget(self.label_edit, 1, 1, 1, 3)

        # add description
        self.description_edit = QLineEdit()
        self.property_view_layout.addWidget(QLabel("DESCRIPTION"), 2, 0)
        self.property_view_layout.addWidget(self.description_edit, 2, 1, 1, 3)

        # add delay
        self.delay_edit = QLineEdit()
        self.property_view_layout.addWidget(QLabel("DELAY"), 3, 0)
        self.property_view_layout.addWidget(self.delay_edit, 3, 1, 1, 3)
        self.delay_edit.setValidator(QIntValidator())

        # add count
        self.count_edit = QLineEdit()
        self.property_view_layout.addWidget(QLabel("COUNT"), 4, 0)
        self.property_view_layout.addWidget(self.count_edit, 4, 1, 1, 3)
        self.count_edit.setValidator(QIntValidator())

        # add filter/force pv
        self.filter_edit = QLineEdit()
        self.property_view_layout.addWidget(QLabel("ENABLING FILTER"), 5, 0)
        self.property_view_layout.addWidget(self.filter_edit, 5, 1, 1, 3)

        # enabled, latching, annunciating
        self.enabled_check = QCheckBox("ENABLED")
        self.annunciating_check = QCheckBox("ANNUNCIATING")
        self.latching_check = QCheckBox("LATCHING")
        self.logging_check = QCheckBox("LOGGING")
        self.property_view_layout.addWidget(self.enabled_check, 6, 0)
        self.property_view_layout.addWidget(self.annunciating_check, 6, 1)
        self.property_view_layout.addWidget(self.latching_check, 6, 2)
        self.property_view_layout.addWidget(self.logging_check, 6, 3)

        spacer = QSpacerItem(40, 200, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.property_view_layout.addItem(spacer, 6, 0)

        # create save button
        self.button_box = QDialogButtonBox(self)
        self.button_box.setOrientation(Qt.Horizontal)
        self.button_box.addButton("Save Properties", QDialogButtonBox.AcceptRole)

        self.property_view_layout.addWidget(self.button_box, 7, 2)

        self.property_layout.addLayout(self.property_view_layout)

        # TODO: command, automated actions tables
        self.main_layout.addLayout(self.property_layout, 0, 1)

        self.setWindowTitle("Alarm Tree Editor")
        self.tree_view.expandAll()

    def minimumSizeHint(self):
        # This is the default recommended size
        # for this screen
        return QSize(400, 200)

    def insertChild(self):
        index = self.tree_view.selectionModel().currentIndex()
        model = self.tree_view.model()

        if model.columnCount(index) == 0:
            if not model.insertColumn(0, index):
                return

        if not model.insertRow(0, index):
            return

        for column in range(model.columnCount(index)):
            child = model.index(0, column, index)
            model.set_data(child, label="NEW_ITEM", role=Qt.EditRole)

    def removeItem(self):
        index = self.tree_view.selectionModel().currentIndex()
        self.tree_view.model().removeRow(index.row(), index.parent())

    @Slot()
    def save_property_changes(self):
        index = self.tree_view.selectionModel().currentIndex()
        self.tree_view.model().set_data(
            index,
            label=self.label_edit.text(),
            description=self.description_edit.text(),
            delay=self.delay_edit.text(),
            count=self.count_edit.text(),
            enabled=self.enabled_check.isChecked(),
            annunciating=self.annunciating_check.isChecked(),
            latching=self.latching_check.isChecked(),
            alarm_filter=self.filter_edit.text(),
            role=Qt.EditRole,
        )

    @Slot()
    def handle_selection(self):
        self.remove_button.setEnabled(self.tree_view.selectionModel().hasSelection())

        index = self.tree_view.selectionModel().currentIndex()
        item = self.tree_view.model().getItem(index)

        self.description_edit.setText(item.description)
        self.label_edit.setText(item.label)
        self.delay_edit.setText(item.delay)
        self.count_edit.setText(item.count)
        self.filter_edit.setText(item.alarm_filter)

        if item.is_group:
            self.description_edit.setEnabled(False)
            self.count_edit.setEnabled(False)
            self.delay_edit.setEnabled(False)
            self.latching_check.setEnabled(False)
            self.annunciating_check.setEnabled(False)
            self.filter_edit.setEnabled(False)

        else:
            self.description_edit.setEnabled(True)
            self.count_edit.setEnabled(True)
            self.delay_edit.setEnabled(True)
            self.latching_check.setEnabled(True)
            self.annunciating_check.setEnabled(True)
            self.filter_edit.setEnabled(True)

            if item.enabled:
                self.enabled_check.setChecked(True)
            else:
                self.enabled_check.setChecked(False)

            if item.latching:
                self.latching_check.setChecked(True)
            else:
                self.latching_check.setChecked(False)

            if item.annunciating:
                self.annunciating_check.setChecked(True)
            else:
                self.annunciating_check.setChecked(False)

    @Slot()
    def item_change(self):
        index = self.tree_view.selectionModel().currentIndex()
        item = self.tree_view.model().getItem(index)

        self.description_edit.setText(item.description)
        self.label_edit.setText(item.label)

        self.delay_edit.setText(item.delay)
        self.count_edit.setText(item.count)

        if item.enabled:
            self.enabled_check.setChecked(True)
        else:
            self.enabled_check.setChecked(False)

        if item.is_group:
            self.description_edit.setEnabled(False)
            self.count_edit.setEnabled(False)
            self.delay_edit.setEnabled(False)
            self.latching_check.setEnabled(False)
            self.annunciating_check.setEnabled(False)
            self.filter_edit.setEnabled(False)

        else:
            self.description_edit.setEnabled(True)
            self.count_edit.setEnabled(True)
            self.delay_edit.setEnabled(True)
            self.latching_check.setEnabled(True)
            self.annunciating_check.setEnabled(True)
            self.filter_edit.setEnabled(True)

            if item.latching:
                self.latching_check.setChecked(True)
            else:
                self.latching_check.setChecked(False)

            if item.annunciating:
                self.annunciating_check.setChecked(True)
            else:
                self.annunciating_check.setChecked(False)

    def ui_filepath(self):
        # No UI file is being used
        return None

    @Slot(bool)
    def open_file(self, checked):
        modifiers = QApplication.keyboardModifiers()
        try:
            curr_file = self.current_file()
            folder = os.path.dirname(curr_file)
        except Exception:
            folder = os.getcwd()

        filename = QFileDialog.getOpenFileName(
            self, "Open File...", folder, "XML (*.xml);; ALH Config (*.alhConfig)"
        )
        filename = filename[0] if isinstance(filename, (list, tuple)) else filename

        if filename:
            filename = str(filename)

            # if alh file selected, open conversion prompt
            if filename[-9:] == "alhConfig":
                self.legacy_window = LegacyWindow(filename)
                self.legacy_window.exec_()

                if self.legacy_window.converted_filename:
                    self.import_configuration(self.legacy_window.converted_filename)

            else:
                self.import_configuration(filename)

    def import_configuration(self, filename):
        nodes = self.config_tool.parse_config(filename)
        self.tree_view.model().import_hierarchy(nodes)
        self.tree_label.setText(self.tree_view.model()._nodes[0].label)

    @Slot()
    def save_configuration(self):
        modifiers = QApplication.keyboardModifiers()
        try:
            curr_file = self.current_file()
            folder = os.path.dirname(curr_file)
        except Exception:
            folder = os.getcwd()

        filename = QFileDialog.getSaveFileName(
            self, "Save File...", folder, "Configration files (*.xml)"
        )
        filename = filename[0] if isinstance(filename, (list, tuple)) else filename

        self.config_tool.save_configuration(self.tree_view.model()._root_item, filename)

    def _update_config_name(self):
        name = self.tree_label.text()
        self.tree_view.model()._nodes[0].label = name

    def _import_legacy_file(self):
        convert_alh_to_phoebus()


class LegacyWindow(QDialog):
    def __init__(self, filename, parent=None):
        super(LegacyWindow, self).__init__(parent)

        self.parent = parent

        self.legacy_filename = filename
        self.converted_filename = None

        # Create widgets
        self.dialog = QLabel(
            "You have chosen a legacy file (.alhConfig). Opening this file requires conversion to the Phoebus Alarm Server format. Would you like to continue?"
        )
        self.dialog.setWordWrap(True)

        self.cancel_button = QPushButton("Cancel")
        self.convert_button = QPushButton("Convert File")

        self.name_edit = QLineEdit(text="Configuration name")

        # Create layout and add widgets

        layout = QVBoxLayout()
        layout.addWidget(self.dialog)
        layout.addWidget(self.name_edit)

        button_box = QHBoxLayout()
        button_box.addWidget(self.cancel_button)
        button_box.addWidget(self.convert_button)

        layout.addLayout(button_box)

        self.setLayout(layout)

        self.cancel_button.clicked.connect(self.reject)
        self.convert_button.clicked.connect(self._open_file_selection)

    @Slot()
    def _open_file_selection(self):

        config_name = self.name_edit.text()

        if config_name:
            modifiers = QApplication.keyboardModifiers()
            try:
                curr_file = self.current_file()
                folder = os.path.dirname(curr_file)
            except Exception:
                folder = os.getcwd()

            filename = QFileDialog.getSaveFileName(
                self, "Save File...", folder, "Configration files (*.xml)"
            )
            filename = filename[0] if isinstance(filename, (list, tuple)) else filename

            alh_conversion.convert_alh_to_phoebus(
                config_name, self.legacy_filename, filename
            )
            self.converted_filename = filename
            self.accept()
