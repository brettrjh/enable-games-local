
from PyQt6 import QtWidgets, uic
from MainMenu import MainMenu
from overlay import OverlayManager


# ---------------------------------------------------------------------------------
# Script Execution
# ---------------------------------------------------------------------------------
if __name__ == "__main__":
    import sys

    # ----------------------------------------------
    # Initialization & Variable Dictionary
    app = QtWidgets.QApplication(sys.argv)  # Create the application
    app.overlay_manager = OverlayManager(app)
    menuW = MainMenu()                      # Create an instance of the MainWindow class
    menuW.show()                            # Show the main window
    sys.exit(app.exec())                    # Run the application's event loop

