
from PyQt6 import QtWidgets, uic
from MainMenu import MainMenu



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
