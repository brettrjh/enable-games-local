
from PyQt6 import QtWidgets, uic
from MainMenu import MainMenu
from TweakMenus import VisualMenu, AudioMenu, PhysMenu
from PresetMenu import PresetMenu

# **** READ ME !!!! **** ------------------------------------------------------
# 
# For the sake of consistency with naming the UI elements within Qt Designer,
# and being able to use the names as objects/functions in python,
# we'll use the following naming conventions:
#    - Widgets ------> name will end with "W" and start w/ a (lowercase)
#                        relevant name (EX: "visualW", "QWmain", etc.)
#    - Push Buttons -> name will end with "PB" and start w/ a (lowercase)
#                        relevant name (EX: "returnPB")
#    - ***ALL OF YOU CAN ADD ADDITIONAL APPROPRIATE CONVENTIONS AS YOU FIND
#         NEW ELEMENTS TO USE, UTILIZE THE SAME IDEA AS ABOVE***
# 
# Recall that to edit the names of elements, go to the Object Inspector in
# Qt Designer and double click the name of your chosen object/element

# *****
# ALSO !!!! For those doing the accessibility settings menus, see the 
# Script Execution section within that .py file for an important commment
# on getting your window to display while testing
# *****

# ---------------------------------------------------------------------------------
# Script Execution
# ---------------------------------------------------------------------------------
if __name__ == "__main__":
    import sys

    # ----------------------------------------------
    # Initialization & Variable Dictionary
    app = QtWidgets.QApplication(sys.argv)  # Create the application
    menuW = MainMenu()                      # Create an instance of the MainWindow class
    menuW.show()                            # Show the main window
    sys.exit(app.exec())                    # Run the application's event loop
