import os
from functools import partial
from xml.dom import minidom
import xml.etree.ElementTree as ET

from qtpy.QtWidgets import (
    QDialog,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QStackedLayout,
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
    Signal,
    Property,
    QAbstractItemModel,
    QSize,
    QMimeData,
)
from qtpy.QtGui import QIntValidator

from nalms_tools import alh_conversion
from nalms_tools.alarm_tree_editor.model import AlarmTreeModel
from pydm.widgets.base import PyDMWritableWidget
from pydm import Display



class PyDMAlarmTree(QTreeView, PyDMWritableWidget):
    def __init__(self, parent, init_channel=None, config_name=None, edit_mode=False):
        super(PyDMAlarmTree, self).__init__()

        QTreeView.__init__(self, parent)
        PyDMWritableWidget.__init__(self)

        self.setup_ui()

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
        #  self.setHeaderHidden(True)
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

            elif child.tag == "guidance":
                data["guidance"] = child.text

            elif child.tag == "command":
                pass  # unused at present

            elif child.tag == "automated_action":
                pass  # unused at present

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
        self._build_config(root_node)

        with open(filename, "w") as f:
            file_str = minidom.parseString(
                ET.tostring(self._tree, encoding="utf8")
            ).toprettyxml(indent="   ")
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

        if alarm_tree_item.guidance:
            alarm_guidance = ET.SubElement(elem, "guidance")
            alarm_guidance.text = alarm_tree_item.guidance

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
    def __init__(self, parent=None):
        super(AlarmTreeEditorDisplay, self).__init__(parent=parent)

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

        self.property_layout = QVBoxLayout()
        self.property_layout.addWidget(QLabel("Alarm Properties"))

        # crate property view
        self.property_data_layout = QStackedLayout()
        self.property_layout.addLayout(self.property_data_layout)

        self.property_widget_config = QWidget()
        self.property_widget_config.setWindowTitle("config")

        # create group widget
        self.property_widget_group = QWidget()
        self.property_widget_group.setWindowTitle("group")

        self.property_view_layout_group = QGridLayout()

        # add label
        self.label_edit_group = QLineEdit()
        self.label_label_group = QLabel("NAME")

        # add guidance
        self.guidance_edit_group = QLineEdit()
        self.guidance_label_group = QLabel("GUIDANCE")

        self.property_view_layout_group.addWidget(self.label_label_group, 1, 0)
        self.property_view_layout_group.addWidget(self.label_edit_group, 1, 1)

        self.property_view_layout_group.addWidget(self.guidance_label_group, 2, 0)
        self.property_view_layout_group.addWidget(self.guidance_edit_group, 2, 1)

        spacer = QSpacerItem(40, 200, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.property_view_layout_group.addItem(spacer, 3, 0)
        self.property_view_layout_group.addItem(spacer, 4, 0)
        self.property_view_layout_group.addItem(spacer, 5, 0)
        self.property_view_layout_group.addItem(spacer, 6, 0)
        self.property_view_layout_group.addItem(spacer, 7, 0)
        self.property_view_layout_group.addItem(spacer, 8, 0)

        # create pv widget
        self.property_widget_pv = QWidget()
        self.property_widget_pv.setWindowTitle("pv")

        self.property_view_layout_pv = QGridLayout()

        # add label
        self.label_edit_pv = QLineEdit()
        self.label_label_pv = QLabel("NAME")

        # add guidance
        self.guidance_edit_pv = QLineEdit()
        self.guidance_label_pv = QLabel("GUIDANCE")

        self.property_view_layout_pv.addWidget(self.label_label_pv, 1, 0)
        self.property_view_layout_pv.addWidget(self.label_edit_pv, 1, 1, 1, 3)

        self.property_view_layout_pv.addWidget(self.guidance_label_pv, 2, 0)
        self.property_view_layout_pv.addWidget(self.guidance_edit_pv, 2, 1, 1, 3)

        # add description
        self.description_edit = QLineEdit()
        self.description_label = QLabel("DESCRIPTION")
        self.property_view_layout_pv.addWidget(self.description_label, 3, 0)
        self.property_view_layout_pv.addWidget(self.description_edit, 3, 1, 1, 3)

        # add delay
        self.delay_edit = QLineEdit()
        self.delay_label = QLabel("DELAY")
        self.property_view_layout_pv.addWidget(self.delay_label, 4, 0)
        self.property_view_layout_pv.addWidget(self.delay_edit, 4, 1, 1, 3)
        self.delay_edit.setValidator(QIntValidator())

        # add count
        self.count_edit = QLineEdit()
        self.count_label = QLabel("COUNT")
        self.property_view_layout_pv.addWidget(self.count_label, 5, 0)
        self.property_view_layout_pv.addWidget(self.count_edit, 5, 1, 1, 3)
        self.count_edit.setValidator(QIntValidator())

        # add filter/force pv
        self.filter_edit = QLineEdit()
        self.filter_label = QLabel("ENABLING FILTER")
        self.property_view_layout_pv.addWidget(self.filter_label, 6, 0)
        self.property_view_layout_pv.addWidget(self.filter_edit, 6, 1, 1, 3)

        # enabled, latching, annunciating
        self.enabled_check = QCheckBox("ENABLED")
        self.annunciating_check = QCheckBox("ANNUNCIATING")
        self.latching_check = QCheckBox("LATCHING")
        self.property_view_layout_pv.addWidget(self.enabled_check, 7, 0)
        self.property_view_layout_pv.addWidget(self.annunciating_check, 7, 1)
        self.property_view_layout_pv.addWidget(self.latching_check, 7, 2)

        self.property_view_layout_pv.addItem(spacer, 8, 0)

        # create save button
        self.button_box = QDialogButtonBox(self)
        self.button_box.setOrientation(Qt.Horizontal)
        self.button_box.addButton("Save Properties", QDialogButtonBox.AcceptRole)

        self.property_layout.addWidget(self.button_box)
        # self.property_layout.addLayout(self.property_view_layout)

        self.property_widget_pv.setLayout(self.property_view_layout_pv)
        self.property_widget_group.setLayout(self.property_view_layout_group)

        self.property_data_layout.addWidget(self.property_widget_config)
        self.property_data_layout.addWidget(self.property_widget_pv)
        self.property_data_layout.addWidget(self.property_widget_group)

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
        item = self.tree_view.model().getItem(index)
        if item.is_group:
            guidance = self.guidance_edit_group.text()
            label = self.label_edit_group.text()
        else:
            guidance = self.guidance_edit_pv.text()
            label = self.label_edit_pv.text()

        self.tree_view.model().set_data(
            index,
            label=label,
            description=self.description_edit.text(),
            delay=self.delay_edit.text(),
            count=self.count_edit.text(),
            enabled=self.enabled_check.isChecked(),
            annunciating=self.annunciating_check.isChecked(),
            latching=self.latching_check.isChecked(),
            alarm_filter=self.filter_edit.text(),
            guidance=guidance,
            role=Qt.EditRole,
        )

    @Slot()
    def handle_selection(self):
        self.remove_button.setEnabled(self.tree_view.selectionModel().hasSelection())

        index = self.tree_view.selectionModel().currentIndex()
        item = self.tree_view.model().getItem(index)

        if item.is_group:
            self.guidance_edit_group.setText(item.guidance)
            self.label_edit_group.setText(item.label)
        else:
            self.guidance_edit_pv.setText(item.guidance)
            self.label_edit_pv.setText(item.label)

        if item.is_group:
            # black for configuration screen
            if not item.parent:
                self.property_data_layout.setCurrentWidget(self.property_widget_config)
            # otherwise show group screen and set all disables
            else:
                self.property_data_layout.setCurrentWidget(self.property_widget_group)
                self.description_edit.setEnabled(False)
                self.description_edit.setVisible(False)
                self.description_label.setVisible(False)

                self.count_edit.setEnabled(False)
                self.count_edit.setVisible(False)
                self.count_label.setVisible(False)

                self.delay_edit.setEnabled(False)
                self.delay_edit.setVisible(False)
                self.delay_label.setVisible(False)

                self.latching_check.setEnabled(False)
                self.latching_check.setVisible(False)

                self.annunciating_check.setEnabled(False)
                self.annunciating_check.setVisible(False)

                self.filter_edit.setEnabled(False)
                self.filter_edit.setVisible(False)
                self.filter_label.setVisible(False)

        # set pv enabled
        else:
            self.property_data_layout.setCurrentWidget(self.property_widget_pv)
            self.description_edit.setEnabled(True)
            self.description_edit.setVisible(True)
            self.description_label.setVisible(True)

            self.count_edit.setEnabled(True)
            self.count_edit.setVisible(True)
            self.count_label.setVisible(True)

            self.delay_edit.setEnabled(True)
            self.delay_edit.setVisible(True)
            self.delay_label.setVisible(True)

            self.latching_check.setEnabled(True)
            self.latching_check.setVisible(True)

            self.annunciating_check.setEnabled(True)
            self.annunciating_check.setVisible(True)

            self.filter_edit.setEnabled(True)
            self.filter_edit.setVisible(True)
            self.filter_label.setVisible(True)

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

        if item.is_group:
            self.guidance_edit_group.setText(item.guidance)
            self.label_edit_group.setText(item.label)
        else:
            self.guidance_edit_pv.setText(item.guidance)
            self.label_edit_pv.setText(item.label)

        if item.is_group:
            if not item.parent():
                self.property_data_layout.setCurrentWidget(self.property_widget_config)

            else:
                self.property_data_layout.setCurrentWidget(self.property_widget_group)

            self.description_edit.setEnabled(False)
            self.description_edit.setVisible(False)
            self.description_label.setVisible(False)

            self.count_edit.setEnabled(False)
            self.count_edit.setVisible(False)
            self.count_label.setVisible(False)

            self.delay_edit.setEnabled(False)
            self.delay_edit.setVisible(False)
            self.delay_label.setVisible(False)

            self.latching_check.setEnabled(False)
            self.latching_check.setVisible(False)

            self.annunciating_check.setEnabled(False)
            self.annunciating_check.setVisible(False)

            self.filter_edit.setEnabled(False)
            self.filter_edit.setVisible(False)
            self.filter_label.setVisible(False)

        else:
            self.delay_edit.setText(item.delay)
            self.count_edit.setText(item.count)

            if item.enabled:
                self.enabled_check.setChecked(True)
            else:
                self.enabled_check.setChecked(False)

            self.property_data_layout.setCurrentWidget(self.property_widget_pv)
            self.description_edit.setEnabled(True)
            self.description_edit.setVisible(True)
            self.description_label.setVisible(True)

            self.count_edit.setEnabled(True)
            self.count_edit.setVisible(True)
            self.count_label.setVisible(True)

            self.delay_edit.setEnabled(True)
            self.delay_edit.setVisible(True)
            self.delay_label.setVisible(True)

            self.latching_check.setEnabled(True)
            self.latching_check.setVisible(True)

            self.annunciating_check.setEnabled(True)
            self.annunciating_check.setVisible(True)

            self.filter_edit.setEnabled(True)
            self.filter_edit.setVisible(True)
            self.filter_label.setVisible(True)

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

    def ui_filepath(self):
        # No UI file is being used
        return None
