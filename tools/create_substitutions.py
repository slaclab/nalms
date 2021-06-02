"""
Template file is generated using the base name of the configuration file. 
By default, the template file used will be the default template packaged with nalms. 
This may instead be specified.

"""
from lxml import etree
import sys
import os

def create_substitutions(filename: str, template_file: str = None) -> None:

    output_filename = ".".join(filename.split(".")[:-1]) + ".template"

    # load file
    with open(filename, "r") as data:
        tree = etree.parse(data)
        root = tree.getroot()

        # find automated_action entries
        actions = root.findall(".//automated_action")
        sevrpvs = []

        for action in actions:
            if "sevrpv" in action.text:
                sevrpv = action.text.strip("sevrpv:")
                sevrpvs.append(sevrpv)

        if not template_file:
            template_file = sevrpv.template

        # create substitutions file
        with open(output_filename, "w") as f:

            f.write(f"file {template_file} {{ ")
            f.write("   pattern")
            f.write("       {SEVRPVNAME}")
            for sevrpv in sevrpvs:
                f.write(f"       {{{sevrpv}}}")
            f.write("}")

        working_dir = os.getcwd()
        
        # get working directory
        with open("st.cmd", "w") as f:

            f.write(f"dbLoadTemplate(\"{working_dir}/{output_filename}\") \n")
            f.write("iocInit \n")

if __name__ == "__main__":
    if sys.argv[1] == "-h":
        print("Create a substitutions file for configuration.")
        print(
            "Usage: python create_substitutions.py configuration_file [template_file]"
        )

    elif len(sys.argv) not in [2, 3]:
        print("Incorrect number of arguments.")
        print(
            "Usage: python create_substitutions.py configuration_file [template_file]"
        )

    else:
        create_substitutions(sys.argv[1])
