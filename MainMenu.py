
from PyQt6 import QtWidgets, uic

# ------------------------------------------------------------------------------
# MainMenu Class: 
# - inherits from the QMainWindow 
#     - (QMainWindow is Qt's name for the primary window when the 
#        application is run, it is not our name for the MainMenu)
# ------------------------------------------------------------------------------
class MainMenu(QtWidgets.QWidget):
    # -------------------------------------------------------------
    # Initialization for ui file and connecting buttons to functions
    def __init__(self):
        super().__init__()
        
        # Loads the UI file
        uic.loadUi('ui files/eg_main_menu.ui', self)

        # Connections of button click events to specific functions
        #self.pushButton.clicked.connect(self.on_button_click)
        #self.pushButton_2.clicked.connect(self.on_button_click_2)

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
# Temporary Script Execution (for testing purposes)
# ---------------------------------------------------------------------------------
if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)  # Create the application
    mainW = MainMenu()                      # Create an instance of the MainMenu class
    mainW.show()                            # Show the main menu
    sys.exit(app.exec())                    # Run the application's event loop