"""
Python >= 3.7
Author: Jacqueline Garrahan

This script is intended for the conversion of alhConfig files to phoebus alarm server xml configuration files.

See configuration file description for alh here: https://epics.anl.gov/EpicsDocumentation/ExtensionsManuals/AlarmHandler/alhUserGuide-1.2.35/ALHUserGuide.html#pgfId_689941
"""
import xml.etree.ElementTree as ET
import os
import copy
import fileinput
import sys
import logging
from treelib import Node, Tree

logger = logging.getLogger(__name__)


dirname = os.path.dirname(__file__)
DEFAULT_SEVRPV_TEMPLATE = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'files/sevrpv.template'))

class ForcePV:
    """
    Representation of ForcePV entry

    Attributes:
        name (str): Name of the process variable
        is_calc (bool): Boolean indicator as to whether is a calculation forcepv.
        _calc_expressions (list): List of calculation lines.
        main_calc (str): Top level calculation.

    """

    def __init__(self) -> None:
        self.name = None
        self.is_calc = False
        self._calc_expressions = []
        self.main_calc = ""

    def add_calc(self, expression: str):
        """ Add a calculation to the forcepv.

        Args:
            expression (str): Expression to add to the calculation.

        """
        self._calc_expressions.append(expression)

    def get_text(self) -> str:
        """ Format calculation and return text.

        """
        text = ""
        if self.is_calc:
            text = self.main_calc

            for key, value in self._calc_expressions.items():
                text.replace(key, value)

        else:
            text = self.name

        return text


class AlarmNode:
    """
    Representation of an alarm tree group.

    Attributes:
        name (str): Name of the alarm group.
        alias (str): Alias to be used instead of group name.
        commands (list): List of associated commands.
        force_pv (ForcePV): Force pv associated with the node.
        sevrpv (str): Indicates severity pv to be used with group.
        parent (str): Parent variable of group.
        node_children (list): Children of the alarm node.
        guidance (list): List of guidance items. 
        guidance_url (str): URL of guidance display.
        filename (str): Generating filename.

    """

    def __init__(
        self, group_name: str, filename: str = None, parent: str = None
    ) -> None:
        self.name = group_name
        self.alias = ""
        self.commands = []
        self.force_pv = None
        self.sevrpv = None
        self.parent = parent
        self.node_children = []
        self.guidance = []
        self.guidance_url = ""
        self.filename = filename

    def add_child(self, child: str) -> None:
        """ Assign a child to the node.

        Args:
            child (str): Name of the child node 

        """
        if child in self.node_children:
            logger.warning(f"DUPLICATE CHILD FOR GROUP {self.name}: {child}")

        else:
            self.node_children.append(child)

    def remove_child(self, child: str) -> None:
        """ Remove a child from the node. 

        Args:
            child (str): Name of child to remove

        """
        idx = self.node_children.index(child)
        if idx is not None:
            self.node_children.pop(idx)


class AlarmLeaf:
    """
    Representation of an alarm tree leaf

    Attributes:
        name (str): Name of the alarm leaf.
        commands (list): List of associated commands.
        force_pv (ForcePV): Force pv associated with the leaf.
        parent (str): Parent group of group.
        guidance (list): List of guidance items. 
        guidance_url (str): URL of guidance display.
        filename (str): Generating filename.
        count (int): Alarm count.
        delay (int): Associated alarm delay.

    """

    node_children = None

    def __init__(
        self, channel_name: str, filename: str = None, parent: str = None
    ) -> None:
        self.name = channel_name
        self.commands = []
        self.force_pv = None
        self.guidance = []
        self.guidance_url = []
        self.count = None
        self.delay = None
        self.filename = ""
        self.parent = parent


class InclusionMarker:
    """
    Marker for indicating file inclusions

    Attributes:
        filename (str): Name of the inclusion file.
        name (str): Name assigned to the inclusion.
        parent (str): Name of the inclusion's parent.

    """

    node_children = None

    def __init__(self, name, filename, parent) -> None:
        self.filename = filename
        self.name = name
        self.parent = parent


class ALHFileParser:
    """
    Tool for parsing ALH files.

    Attributes:
        _filepath (str): Path of file being parsed.
        _base (str): Base node path, used for inclusions.
        _current_target (str): Current leaf/node being updated.
        _items (dict): Dictionary of processed items.
        _inclusions (dict): Dictionary of file inclusions.
        _inclusion_count (int): Count of inclusion for tracking.
        _config_name (str): Name of the configuration. 
        _failures (str): Failure to convert messages.
        _rel_parent (dict): Mapping of relative group entries to full node path

    """

    def __init__(self, filepath: str, config_name: str, base: str = None):
        self._filepath = filepath

        # current tracked item
        self._current_target = None

        # for tracking items
        self._items = {}
        self._inclusions = {}
        self._inclusion_count = 0

        # create root node
        self._items[config_name] = AlarmNode(config_name)
        self._config_name = config_name

        # markers for tracking where at in parsing
        if base:
            self._base = base
            self._items[base] = AlarmNode(
                base.split("/")[-1], parent=self._items[config_name]
            )

        else:
            self._base = config_name

        # track conversion failures
        self._failures = []

        # track items whose parents aren't found
        self._out_of_scope = {}

        # relative parent path
        self._rel_parent = {}

    def parse_file(self) -> tuple:
        """ Parse stored file and return items, failures, and inclusions.

        Returns:
            items (dict): Dictionary of processed items
            failures (list): List of failures
            inclusions (dict): List of file inclusions

        """
        self._line_iterator = fileinput.input(self._filepath)

        next_line = next(self._line_iterator, None)

        while next_line:

            split_line = next_line.split()

            if len(split_line) > 0:

                # process group entry
                if split_line[0] == "GROUP":
                    self._process_group(split_line)

                # process channel entry
                elif split_line[0] == "CHANNEL":
                    self._process_channel(split_line)

                # process command entry
                elif split_line[0] == "$COMMAND":
                    self._process_command(split_line)

                # process sevrpv command entry
                elif split_line[0] == "$SEVRPV":
                    self._process_sevrpv(split_line)

                # process forcepv command entry
                elif split_line[0] == "$FORCEPV":
                    self._process_forcepv(split_line)

                # process guidance entry
                elif split_line[0] == "$GUIDANCE":
                    self._process_guidance(split_line)

                # process alias entry
                elif split_line[0] == "$ALIAS":
                    self._process_alias(split_line)

                # skip comments
                elif split_line[0][0] == "#":
                    pass

                # process heartbeatpv
                elif split_line[0] == "$HEARTBEATPV":
                    self._failures.append(
                        {
                            "Reason": "Heartbeat pv must be configured",
                            "File": self._filepath,
                            "Line": next_line,
                        }
                    )

                elif split_line[0] == "INCLUDE":
                    self._process_inclusion(split_line)

                elif split_line[0] == "$ALARMCOUNTFILTER":
                    self._process_alarm_count(split_line)

                # Handle deprecated commands
                elif split_line[0] == "$SEVRCOMMAND":
                    self._failures.append(
                        {
                            "Reason": "SEVRCOMMAND is deprecated",
                            "File": self._filepath,
                            "Line": next_line,
                        }
                    )

                elif split_line[0] == "$STATCOMMAND":
                    self._failures.append(
                        {
                            "Reason": "STATCOMMAND is deprecated",
                            "File": self._filepath,
                            "Line": next_line,
                        }
                    )

                elif split_line[0] == "BEEPSEVERITY":
                    self._failures.append(
                        {
                            "Reason": "BEEPSEVERITY is deprecated",
                            "File": self._filepath,
                            "Line": next_line,
                        }
                    )

                elif split_line[0] == "BEEPSEVR":
                    self._failures.append(
                        {
                            "Reason": "BEEPSEVR is deprecated",
                            "File": self._filepath,
                            "Line": next_line,
                        }
                    )

                # process ackpv entry
                elif split_line[0] == "$ACKPV":
                    self._failures.append(
                        {
                            "Reason": "ACKPV is deprecated",
                            "File": self._filepath,
                            "Line": next_line,
                        }
                    )

                else:
                    self._failures.append(
                        {
                            "Reason": "Line element not found.",
                            "File": self._filepath,
                            "Line": next_line,
                        }
                    )

            next_line = next(self._line_iterator, None)

        return self._items, self._failures, self._inclusions, self._out_of_scope

    def _process_group(self, split_line: list) -> None:
        """ Process group ALH entry.

        Args:
            split_line (list): List generated by splitline

        """

        # group name is stored as third element
        group_name = split_line[2]

        # parent is stored in second element
        parent = None
        if split_line[1] != "NULL":
            parent = split_line[1]

        # if this is not the top level of the file, store parent path and node path
        if parent:
            rel_parent = self._rel_parent.get(parent, parent)
            parent_path = f"{self._base}/{rel_parent}"
            node_path = f"{parent_path}/{group_name}"
            self._rel_parent[group_name] = f"{rel_parent}/{group_name}"

        # if no parent is specified, top level or downstream inclusion
        else:
            parent_path = self._base
            node_path = f"{self._base}/{group_name}"
            self._rel_parent[group_name] = group_name

        if parent_path not in self._items:
            self._out_of_scope[node_path] = parent_path

        # add to child to parent
        else:
            self._items[parent_path].add_child(node_path)

        # add the node path tso items and create node object
        if node_path not in self._items:
            self._items[node_path] = AlarmNode(group_name, parent=parent_path)

        # update target and parent group
        self._current_target = node_path

    def _process_channel(self, split_line: list) -> None:
        """ Process channel ALH entry.

        Args:
            split_line (list): List generated by splitline

        """

        # channel name is stored as the third element
        channel_name = split_line[2]

        # parent is stored as the second element
        parent = split_line[1]

        # if we currently have a defined parent group and this is different than the parent given
        # adjust path based on parent group and parent
        if parent:
            rel_parent = self._rel_parent.get(parent, parent)
            parent_path = f"{self._base}/{rel_parent}"
            channel_path = f"{parent_path}/{channel_name}"

        # otherwise, just use base
        else:
            parent_path = self._base
            channel_path = f"{self._base}/{channel_name}"

        # update item and assign parent
        self._items[channel_path] = AlarmLeaf(
            channel_name, filename=self._filepath, parent=parent_path
        )

        # update children and parents
        self._items[channel_path].parent = parent_path
        self._items[parent_path].add_child(channel_path)

        # update current tracked item
        self._current_target = channel_path

    def _process_command(self, split_line: list) -> None:
        """ Process ALH COMMAND entry.

        Args:
            split_line (list): List generated by splitline

        """
        command = " ".join(split_line[1:])
        # if multiple commands, break apart
        commands = command.split("!")
        # store commands on item as list of commands
        self._items[self._current_target].commands += commands

    def _process_sevrpv(self, split_line: list) -> None:
        """ Process ALH SEVRPV entry.

        Args:
            split_line (list): List generated by splitline

        """
        self._items[self._current_target].sevrpv = split_line[1]

    def _process_forcepv(self, split_line: list) -> None:
        """ Process ALH FORCEPV entry.

        Args:
            split_line (list): List generated by splitline

        """
        # force mask is stored as the third entry
        force_mask = split_line[2]

        force_value = None
        reset_value = None

        # force value is stored as the fourth entry
        if len(split_line) >= 4:
            force_value = split_line[3]

        # reset value is stored as the fifth entry
        if len(split_line) == 5:
            reset_value = split_line[4]

        self._failures.append(
            {
                "Reason": "Reset value and force value are deprecated.",
                "File": self._filepath,
                "Line": " ".join(split_line),
            }
        )

        # create a force pv for the item
        self._items[self._current_target].force_pv = ForcePV()

        # if this is a calc type force pv, mark as calc type
        if split_line[1] == "CALC":
            self._items[self._current_target].force_pv.is_calc = True

            # process following calc lines
            reached_end = False
            while not reached_end:
                next_line = next(self._line_iterator)
                if next_line:
                    next_split = next_line.split()

                    # get representative calculation
                    if next_split[0] == "FORCEPV_CALC":
                        self._items[self._current_target].main_calc = split_line[1]

                    # Force pvs use letter standins for complicated calcs, eg. FORCEPV_CALC_A
                    # Track these values
                    elif "FORCEPV_CALC_" in next_split[0]:
                        identifier = next_split[0][-1]
                        self._items[self._current_target].calcs[
                            identifier
                        ] = next_split[1]

                    # otherwise have reached end
                    else:
                        reached_end = True

        # if not calc, name of the pv is the second element
        # update forcepv with the name of the forcepv
        else:
            force_pv_name = split_line[1]
            self._items[self._current_target].force_pv.name = force_pv_name

    def _process_guidance(self, split_line: list) -> None:
        """ Process ALH guidance entry.

        Args:
            split_line (list): List generated by splitline

        """

        # if this is a multiline guidance entry, collect all lines
        if len(split_line) == 1:

            reached_end = False
            while not reached_end:
                next_line = next(self._line_iterator)
                if next_line:

                    # check for summary pv entry 
                    if "Summary PV" in next_line:
                        summary_pvname = next_line.strip("Summary PV:").strip()
                        # track sevrpv
                        self._items[self._current_target].sevrpv = summary_pvname

                    next_split = next_line.split()

                    if len(next_split) > 0:
                        if next_split[0] == "$END":
                            reached_end = True

                        else:
                            self._items[self._current_target].guidance.append(
                                next_line.replace("\n", ",").strip()
                            )

        # if it is a single line guidance, will be a url reference
        else:
            urlname = split_line[1]
            self._items[self._current_target].guidance_url = urlname

    def _process_alias(self, split_line: list) -> str:
        """ Process ALH alias entry.

        Args:
            split_line (list): List generated by splitline

        """
        self._items[self._current_target].alias = split_line[1]

    def _process_inclusion(self, split_line: list) -> None:
        """ Process ALH inclusion entry.

        Args:
            split_line (list): List generated by splitline

        """
        parent = split_line[1]

        # requires full filename declaration
        file_base = "/".join(self._filepath.split("/")[:-1])
        include_filename = f"{file_base}/{split_line[2]}"

        if parent:
            rel_parent = self._rel_parent.get(parent, parent)
            parent_path = f"{self._base}/{rel_parent}"
        else:
            parent_path = self._base

        # mark an inclusion with unique placeholder
        item_key = f"/{parent_path}/INCLUDE_{self._inclusion_count}"
        self._items[item_key] = InclusionMarker(item_key, include_filename, parent_path)
        self._items[self._current_target].add_child(item_key)
        self._inclusion_count += 1

        # track the inclusion for processing
        self._inclusions[item_key] = include_filename

    def _process_alarm_count(self, split_line: list) -> None:
        """ Process alarm count entry.

        Args:
            split_line (list): List generated by splitline

        """
        self._items[self._current_target].count = split_line[1]
        self._items[self._current_target].delay = split_line[2]


class XMLBuilder:
    """
    Class for building the XML configuration representation.

    Attributes:
        _groups (dict): Dictionary of group tree elements.
        _tree (Tree): treelib tree for representing the hierarchy.
        _added_pvs (list): List of pvs already added.

    """

    def __init__(self, recurse: bool = True):
        """ Running without the recursive setting assembles the file using xinclude tags, 
        which aren't handled at present. 

        """
        self._groups = {}
        self._added_pvs = []
        self._tree = None
        self._sevrpvs = []

    def build_tree(self, items, top_level_node: str) -> None:
        """Function for building tree using items and a top level configuration.

        Args:
            items (dict): Dictionary of parsed ALH items.
            top_level_node (str): Name of configuration

        """
        self._tree = Tree()

        self._configuration = ET.Element("config", name=top_level_node)
        self._groups[top_level_node] = self._configuration

        self._config_name = top_level_node

        # create root node
        self._tree.create_node(
            top_level_node, top_level_node, data=items[top_level_node]
        )

        processed = []

        to_process = [top_level_node]

        while len(to_process) > 0:
            node = to_process.pop(0)
            children = items[node].node_children

            if children:
                for child in children:
                    self._tree.create_node(
                        items[child].name, child, parent=node, data=items[child]
                    )

                # add children to process
                to_process += children

        processed.append(node)

        root_node = self._tree.get_node(self._config_name)
        self._handle_children(root_node)

    def save_configuration(self, output_filename: str):
        """ Method for saving configuration to an output file.

        Args:
            output_filename (str): Name of output file.

        """

        with open(output_filename, "wb") as f:
            file_str = ET.tostring(self._configuration, encoding="utf8")
            f.write(file_str)

    def _handle_children(self, node: Node, parent_group: str = None) -> None:
        """ Process children of a node.

        Args: 
            node: treelib representation of the node
            parent_group: Name of parent group

        """
        children = self._tree.children(node.identifier)

        self._add_group(node.tag, node.data, parent_group=parent_group)

        if children:

            for child in children:
                if isinstance(child.data, AlarmLeaf):
                    self._add_pv(child.tag, node.tag, child.data)

                elif isinstance(child.data, AlarmNode):
                    self._handle_children(child, parent_group=node.tag)

                # if not recursing
                elif isinstance(child.data, InclusionMarker):
                    self._add_inclusion(node, child.data.filename)

    def _add_group(self, group: str, data: AlarmNode, parent_group: str = None) -> None:
        """ Add group to the element tree representation.

        Args:
            group (str): Name of group
            data (AlarmNode): AlarmNode representation of data
            parent_group (str): Name of parent group

        """
        group_name = group
        if data.alias:
            group_name = data.alias

        if group not in self._groups:
            if not parent_group:
                self._groups[group] = ET.SubElement(
                    self._configuration, "component", name=group_name
                )
            else:
                self._groups[group] = ET.SubElement(
                    self._groups[parent_group], "component", name=group_name
                )

        # add guidance
        if data.guidance:
            guidance = ET.SubElement(self._groups[group], "guidance")
            guidance.text = " ".join(data.guidance)

        # add display url
        if data.guidance_url:
            display = ET.SubElement(self._groups[group], "display")
            display.text = data.guidance_url

        # add all commands
        if data.commands:
            for command in data.commands:
                command_item = ET.SubElement(self._groups[group], "command")
                command_item.text = command

        if data.sevrpv is not None:
            command_item = ET.SubElement(self._groups[group], "automated_action")
            command_item.text = f"sevrpv:{data.sevrpv}"
            self._sevrpvs.append(data.sevrpv)

    def _add_pv(self, pvname: str, group: str, data: AlarmLeaf) -> None:
        """ Add a pv to the tree representation.

        Args:
            pvname (str): Name of the pv.
            group (str): Name of parent group.
            data (AlarmLeaf): Data object associated with the alarm leaf.

        """
        if pvname in self._added_pvs:
            pass

        else:
            self._added_pvs.append(pvname)
            pv = ET.SubElement(self._groups[group], "pv", name=pvname)
            enabled = ET.SubElement(pv, "enabled")
            enabled.text = "true"

            # disable latching by default
            latching = ET.SubElement(pv, "latching")
            latching.text = "false"

            if data.force_pv is not None:
                filter_pv = ET.SubElement(pv, "filter")
                filter_pv.text = self._process_forcepv(data.force_pv)

            # add guidance
            if data.guidance:
                guidance = ET.SubElement(pv, "guidance")
                guidance.text = " ".join(data.guidance)

            # add display url
            if data.guidance_url:
                display = ET.SubElement(pv, "display")
                display.text = data.guidance_url

            # add all commands
            if data.commands:
                for command in data.commands:
                    command_item = ET.SubElement(pv, "command")
                    command_item.text = command

            # add count
            if data.count:
                count = ET.SubElement(pv, "count")
                count.text = data.count

            # add delay
            if data.delay:
                delay = ET.SubElement(pv, "delay")
                delay.text = data.delay

    def _add_inclusion(self, group_node: Node, filename: str) -> None:
        """ Add Xinclude tag for inclusion.

        Args:
            group_node (Node): Alarm group node.
            filename (str): String filename.

        """
        inclusion = ET.SubElement(
            self._groups[group_node.tag],
            "xi:include",
            href=filename,
            xpointer="xpointer(/config/*",
            attrib={"xmlns:xi": "http://www.w3.org/2001/XInclude"},
        )

    def _process_forcepv(self, force_pv: ForcePV) -> str:
        """ Get text appropriate for force pv

        Args:
            force_pv (ForcePV): ForcePV representation.

        """
        return force_pv.get_text()

    def build_substitutions_file(self, output_filename: str, template_file: str = DEFAULT_SEVRPV_TEMPLATE):
        """ Method for creating a substitutions file for severity pvs.

        Args:
            output_filename (str): Substitutions filename
            template_file (str): File to use as a template

        """
        if not output_filename:
            # write directly to substitutions
            output_filename = f"{self._configuration}.substitutions"

        # create substitutions file
        with open(output_filename, "w") as f:

            f.write(f"file {template_file} {{ \n")
            f.write("   pattern {SEVRPVNAME}\n")
            for sevrpv in self._sevrpvs:
                f.write(f"   {{{sevrpv}}}\n")
            f.write("}\n")

        working_dir = os.getcwd()


        # get working directory
        with open("std.cmd", "w") as f:

            f.write(f"dbLoadTemplate(\"{working_dir}/{output_filename}\") \n")
            f.write("iocInit \n")


def convert_alh_to_phoebus(
    config_name: str, input_filename: str, output_filename: str, build_substitutions=True,
) -> None:
    """ Method for converting the alarm handler configuration files to the Phoebus xml representations.

    Args:
        config_name (str): Name of the configuration.
        input_filename (str): Name of input file.
        output_filename (str): Name of output file.

    """
    parser = ALHFileParser(input_filename, config_name)
    items, failures, inclusions, out_of_scope = parser.parse_file()
    directory = "/".join(input_filename.split("/")[:-1])

    recurse = True
    # recurse over inclusion files
    if recurse:
        while len(inclusions) > 0:
            inclusion = list(inclusions.keys())[0]
            parent = items[inclusion].parent

            filename = inclusions[inclusion]
            if "./" == filename[:2]:
                filename = filename.replace("./", f"{directory}/")

            parser = ALHFileParser(filename, parent, base=parent)
            (
                next_items,
                next_failures,
                next_inclusions,
                next_out_of_scope,
            ) = parser.parse_file()

            # remove inclusion
            inclusions.pop(inclusion)
            items.pop(inclusion)

            #  link the tree
            for child in next_items[parent].node_children:
                items[parent].add_child(child)

            items[parent].remove_child(inclusion)

            # remove parent from items
            next_items.pop(parent)

            inclusions.update(next_inclusions)
            out_of_scope.update(next_out_of_scope)
            items.update(next_items)

            failures += next_failures

        # clean up out of scope
        for entry, missing_parent in out_of_scope.items():
            if missing_parent in items:
                items[missing_parent].add_child(entry)
            else:
                logger.error(f"{entry} still missing parent {missing_parent}")

    tree_builder = XMLBuilder()
    tree_builder.build_tree(items, config_name)
    tree_builder.save_configuration(output_filename)

    if build_substitutions:
        substitutions_filename = output_filename.replace(".xml", ".substitutions")
        tree_builder.build_substitutions_file(substitutions_filename)

    logger.info(f"Configuration file saved: {output_filename}")
    if len(failures) > 0:
        logger.warning("Conversion failed on the following points:")

        for failure in failures:
            logger.warning(failure)


if __name__ == "__main__":
    logger.setLevel("INFO")

    if len(sys.argv) == 0 or sys.argv[1] == "-h":
        print(
            "Usage: python alh_conversion.py config_name input_filename output_filename"
        )

    elif len(sys.argv) != 4:
        print("Incorrect number of arguments.")
        print(
            "Usage: python alh_conversion.py config_name input_filename output_filename"
        )

    else:
        convert_alh_to_phoebus(sys.argv[1], sys.argv[2], sys.argv[3])
