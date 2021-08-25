"""
Python = 3.8
Author: Jacqueline Garrahan

Db and template files are generated using the base name of the configuration file. 
By default, the template file used will be the default template packaged with NALMS. 
This may instead be specified.

"""
from lxml import etree
import sys
import os
import string
from importlib_resources import files
from shutil import copyfile

TEMPLATE_FILE = files("nalms_tools.files").joinpath("nalms_force_pv.template")
ALPHABET = string.ascii_uppercase


def create_force_pvs(
    filename: str, output_directory: str, force_pv_template: str, config_name: str
) -> str:
    """Utility function for creating and writing forcepv template given a configuration.

    Args:
        filename (str): Name of configuration file
        output_directory (str): Directory to write output db files
        force_pv_template (str): Filename of forcepv template
        config_name (str): Name of configuration

    """
    # load file
    with open(filename, "r") as data:
        tree = etree.parse(data)
        root = tree.getroot()

    # groups
    groups = root.findall(".//component")

    # pvs
    pvs = root.findall(".//pv")

    forcepvs = [group.get("name") for group in groups] + [pv.get("name") for pv in pvs]

    force_pv_template_base = str(force_pv_template).split("/")[-1]

    # create substitutions file
    output_filename = f"{output_directory}/nalms_{config_name}.substitutions"
    with open(output_filename, "w") as f:

        f.write(f"file db/{force_pv_template_base} {{")
        f.write("   pattern")
        f.write("       {PVNAME} \n")
        for pv in forcepvs:
            f.write(f"       {{{pv}}} \n")
        f.write("}")

    return output_filename


def create_summary_pvs(filename: str, output_directory: str, config_name: str) -> str:
    """Utility function for creating and writing summary db file.

    Args:
        filename (str): Name of configuration file
        output_directory (str): Directory to write output db files
        config_name (str): Name of configuration

    """
    # load file
    with open(filename, "r") as data:
        tree = etree.parse(data)
        root = tree.getroot()

    lines = []

    # groups
    groups = root.findall(".//component")
    for group in groups:
        name = group.get("name")
        lines.append(f"record(calc, {config_name}:{name}:STATSUMY) {{\n")
        lines += ['field(DESC, "Summary PV")\n', 'field(SCAN, "1 second")\n']

        child_idx = 0
        for child in group.iterchildren():
            child_name = child.get("name")
            if child.tag == "component":
                lines.append(
                    f'field(INP{ALPHABET[child_idx]}, "{config_name}:{child_name}:STATSUMY.SEVR NPP MS")\n'
                )

            elif child.tag == "pv":
                lines.append(
                    f'field(INP{ALPHABET[child_idx]}, "{child_name}:DP.SEVR NPP MS")\n'
                )

            child_idx += 1

        lines += ['field(CALC, "0")\n', "}\n\n"]

    # groups create FP summary
    groups = root.findall(".//component")
    for group in groups:
        name = group.get("name")
        lines.append(f"record(calc, {name}:STATSUMYFP) {{\n")
        lines += ['field(DESC, "Summary PV")\n', 'field(SCAN, "1 second")\n']

        child_idx = 0
        for child in group.iterchildren():
            child_name = child.get("name")
            if child.tag == "component":
                lines.append(
                    f'field(INP{ALPHABET[child_idx]}, "{child_name}:STATSUMYFP.SEVR NPP MS")\n'
                )

            elif child.tag == "pv":
                lines.append(
                    f'field(INP{ALPHABET[child_idx]}, "{child_name}FP.SEVR NPP MS")\n'
                )

            child_idx += 1

        lines += ['field(CALC, "0")\n', "}\n\n"]

    # create substitutions file
    output_filename = f"{output_directory}/nalms_{config_name}.db"
    with open(output_filename, "w") as f:
        for line in lines:
            f.write(line)

    return output_filename


def create_soft_ioc(
    filename: str, template_file: str, output_directory: str, config_name: str
) -> None:
    """Create softIoc from a configuration file.

    Args:
        filename (str): Name of configuration file
        output_directory (str): Directory to write output db files
        force_pv_template (str): Filename of forcepv template
        config_name (str): Name of configurations

    """

    templated_filename = create_force_pvs(
        filename, output_directory, template_file, config_name
    )
    summary_pv_filename = create_summary_pvs(filename, output_directory, config_name)

    # get working directory
    with open(f"{output_directory}/st.cmd", "w") as f:
        f.write(f'dbLoadRecords("{summary_pv_filename}") \n')
        f.write(f'dbLoadTemplate("{templated_filename}") \n')
        f.write("iocInit \n")

    template_base = str(template_file).split("/")[-1]
    copyfile(template_file, f"{output_directory}/{template_base}")

    print(f"Created {templated_filename}, {summary_pv_filename}, and st.cmd.")


def main():
    if sys.argv[1] == "-h":
        print("Format softIOC for a NALMS configuration.")
        print(
            "Usage: python create_soft_iocs.py configuration_file output_directory config_name"
        )

    elif len(sys.argv) not in [2, 3, 4, 5]:
        print("Incorrect number of arguments.")
        print(
            "Usage: python create_soft_iocs.py configuration_file output_directory config_name"
        )

    else:
        configuration_file = sys.argv[1]
        output_directory = sys.argv[2]
        config_name = sys.argv[3]
        create_soft_ioc(
            configuration_file, TEMPLATE_FILE, output_directory, config_name
        )


if __name__ == "__main__":
    main()
