import sys
import pydm
import nalms_tools.alarm_tree_editor.


def main():
    app = pydm.PyDMApplication(
        ui_file="./editor.py", # Here is your .ui or .py file
     #   hide_nav_bar=pydm_args.hide_nav_bar, # Bool
     #   hide_menu_bar=pydm_args.hide_menu_bar, # Bool
     #   hide_status_bar=pydm_args.hide_status_bar, # Bool
     #   fullscreen=pydm_args.fullscreen, # Bool
     #   read_only=pydm_args.read_only, # Bool
     #   macros=macros, # Macros as a dict
        stylesheet_path="./stylesheet.css" # Path-like string for stylesheets
    )
    sys.exit(app.exec_())