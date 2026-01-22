
from PyQt6 import QtWidgets, uic

# ------------------------------------------------------------------------------
# MainWindow Class: 
# - inherits from the QMainWindow (primary window when application will be run)
# ------------------------------------------------------------------------------
class MainMenu(QtWidgets.QMainWindow):
    # -------------------------------------------------------------
    # Initialization for ui file and connecting buttons to functions
    def __init__(self):
        super().__init__()
        
        # Loads the UI file
        uic.loadUi('file.ui', self)

        # Connections of button click events to specific functions
        self.pushButton.clicked.connect(self.on_button_click)
        self.pushButton_2.clicked.connect(self.on_button_click_2)

    # ------------------------------------------------------------
    # [insert name] Function:
    # - called when the given button is clicked
    def on_button_click(self):
        print("Button from the UI was clicked!")

    # ------------------------------------------------------------
    # [insert name] Function:
    # - called when the given button is clicked
    def on_button_click_2(self):
        self.label.setText('Hello World')



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
