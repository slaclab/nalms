from setuptools import setup, find_packages
from os import path, environ

cur_dir = path.abspath(path.dirname(__file__))

# parse requirements
with open(path.join(cur_dir, "requirements.txt"), "r") as f:
    requirements = f.read().split()

setup(
    name="nalms-phoebus-services",
    author="SLAC National Accelerator Laboratory",
    author_email="jgarra@slac.stanford.edu",
    license="SLAC Open",
    packages=find_packages(),
    install_requires=requirements,
    url="https://github.com/slaclab/lume-model",
    include_package_data=True,
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
        "convert-alh=nalms_tools.alh_conversion:main",
        "create-ioc-db=nalms_tools.create_ioc_db:main",
        "launch-editor=nalms_tools.alarm_tree_editor:main"
        ]
    },
)