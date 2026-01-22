
from PyQt6 import QtWidgets, uic

# ------------------------------------------------------------------------------
# VisualMenu Class: 
# - inherits from the QWidget
#     - QWidget is the name in Qt Designer for the Visual Settings widget
#     - go to the Object Inspector in Qt Designer to change it's name
# ------------------------------------------------------------------------------
class VisualMenu(QtWidgets.QWidget):
    # -------------------------------------------------------------
    # Initialization for ui file and connecting buttons to functions
    def __init__(self):
        super().__init__()
        
        # Loads the UI file and sets the window title
        uic.loadUi('ui files/eg_visual_settings.ui', self)
        self.setWindowTitle('Visual Settings')

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




# ------------------------------------------------------------------------------
# AudioMenu Class: 
# - inherits from the QWidget
#     - QWidget is the name in Qt Designer for the Audio Settings widget
#     - go to the Object Inspector in Qt Designer to change it's name
# ------------------------------------------------------------------------------
class AudioMenu(QtWidgets.QWidget):
    # -------------------------------------------------------------
    # Initialization for ui file and connecting buttons to functions
    def __init__(self):
        super().__init__()
        
        # Loads the UI file and sets the window title
        uic.loadUi('ui files/eg_audio_settings.ui', self)
        self.setWindowTitle('Audio Settings')

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




# ------------------------------------------------------------------------------
# PhysMenu Class: 
# - inherits from the QWidget
#     - QWidget is the name in Qt Designer for the Physical Settings widget
#     - go to the Object Inspector in Qt Designer to change it's name
# ------------------------------------------------------------------------------
class PhysMenu(QtWidgets.QWidget):
    # -------------------------------------------------------------
    # Initialization for ui file and connecting buttons to functions
    def __init__(self):
        super().__init__()
        
        # Loads the UI file and sets the window title
        uic.loadUi('ui files/eg_physical_settings.ui', self)
        self.setWindowTitle('Physical Settings')

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
    visualW = VisualMenu()
    audioW = AudioMenu()
    physicalW = PhysMenu()
    
    # ***** IMPORTANT READ ME PLEASE !!!!!!! *****
    # WHEN TESTING, JUST COMMENT OUT THE .show() METHODS THAT AREN'T
    # YOURS SO IT WILL ONLY SHOW YOUR WINDOW WHILE TESTING
    visualW.show()                          # Show the visual settings
    audioW.show()                           # Show the audio settings
    physicalW.show()                        # Show the physical settings
    
    sys.exit(app.exec())                    # Run the application's event loop