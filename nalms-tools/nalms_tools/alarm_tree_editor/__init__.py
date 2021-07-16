import sys
import pydm
import os

dir_path = os.path.dirname(__file__)

def main():
    app = pydm.PyDMApplication(
        ui_file=f"{dir_path}/editor.py",
        hide_nav_bar=True, 
        stylesheet_path=f"{dir_path}/stylesheet.css" 
    )
    sys.exit(app.exec_())