
from PyQt6 import QtWidgets, uic

# ------------------------------------------------------------------------------
# PresetMenu Class: 
# - inherits from the QWidget
#     - QWidget is the name in Qt Designer for the Preset Menu widget
#     - go to the Object Inspector in Qt Designer to change it's name
# ------------------------------------------------------------------------------
class PresetMenu(QtWidgets.QWidget):
    # -------------------------------------------------------------
    # Initialization for ui file and connecting buttons to functions
    def __init__(self):
        super().__init__()
        
        # Loads the UI file and sets the window title
        uic.loadUi('ui files/eg_presets_menu.ui', self)
        self.setWindowTitle('Preset Menu')

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
# Temporary Script Execution (for testing purposes)
# ---------------------------------------------------------------------------------
if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)  # Create the application
    presetW = PresetMenu()                  # Create an instance of the PresetMenu class
    presetW.show()                          # Show the preset menu
    sys.exit(app.exec())                    # Run the application's event loop