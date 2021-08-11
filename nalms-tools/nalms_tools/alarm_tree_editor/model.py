import os
import json
import time
from functools import partial

from kafka import KafkaConsumer
from qtpy.QtCore import (
    Qt,
    Slot,
    QModelIndex,
    QObject,
    Signal,
    Property,
    QAbstractItemModel,
    QMimeData,
)
from qtpy.QtGui import QBrush, QColor

from pydm.widgets.base import widget_destroyed


class AlarmTreeItem(QObject):
    """
    Alarm tree items hold all data for an entry in the configuration heirarchy
    """

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
        guidance=None,
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

        self.guidance = guidance
        self.description = description
        self.enabled = enabled
        self.latching = latching
        self.count = count
        self.delay = delay
        self.label = label
        self.annunciating = annunciating
        self.alarm_filter = alarm_filter
        self.is_group = is_group

        if hasattr(self, "channels"):
            self.destroyed.connect(partial(widget_destroyed, self.channels))

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
                return QBrush(QColor(102, 0, 255))

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
        guidance=None,
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

        if guidance:
            item.guidance = guidance

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
