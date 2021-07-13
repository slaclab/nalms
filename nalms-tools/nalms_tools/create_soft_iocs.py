"""
Template file is generated using the base name of the configuration file. 
By default, the template file used will be the default template packaged with nalms. 
This may instead be specified.

"""
from lxml import etree
import sys
import os

def create_soft_iocs(filename: str, template_file: str, output_directory: str, config_name: str = None) -> None:

    if not config_name:
        config_name  = filename.split("/")[-1]

    # load file
    with open(filename, "r") as data:
        tree = etree.parse(data)
        root = tree.getroot()

        # find automated_action entries
        actions = root.findall(".//automated_action")
        sevrpvs = []

        for action in actions:
            details = action.findall(".//details")
            for detail in details:
                if "sevrpv" in detail.text:
                    sevrpv = detail.text.strip("sevrpv:")
                    sevrpvs.append(sevrpv)

        if not template_file:
            print("No template file provided.")
            sys.exit()

        # create substitutions file
        output_filename = f"{output_directory}/{config_name}.template"
        with open(output_filename, "w") as f:

            f.write(f"file {template_file} {{ ")
            f.write("   pattern")
            f.write("       {SEVRPVNAME}")
            for sevrpv in sevrpvs:
                f.write(f"       {{{sevrpv}}}")
            f.write("}")

        working_dir = os.getcwd()

        # get working directory
        with open(f"{output_directory}/st.cmd", "w") as f:

            f.write(f"dbLoadTemplate(\"{output_filename}\") \n")
            f.write("iocInit \n")

        print(f"Created {output_filename} and st.cmd.")

def main():
    if sys.argv[1] == "-h":
        print("Create a substitutions file for configuration.")
        print(
            "Usage: python create_soft_iocs.py configuration_file template_file output_directory [config_name]"
        )

    elif len(sys.argv) not in [2, 3, 4, 5]:
        print("Incorrect number of arguments.")
        print(
            "Usage: python create_soft_iocs.py configuration_file template_file output_directory [config_name]"
        )

    else:
        create_soft_iocs(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])

if __name__ == "__main__":
    main()
