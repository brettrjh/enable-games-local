
from PyQt6 import QtWidgets, uic

from PyQt6.QtGui import QPixmap

# needed for connectivity/opening the main menu
from MainMenu import MainMenu


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

        # commenting below out (no buttons yet in eg_visual_settings.ui)

        # self.pushButton.clicked.connect(self.on_button_click)
        # self.pushButton_2.clicked.connect(self.on_button_click_2)

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

        # Loads the icon dynamically
        pixmap = QPixmap("ui files/Images/Sound.png")
        if pixmap.isNull():
            print("could not laod icon")
        self.iconLabel.setPixmap(pixmap)
        self.iconLabel.setScaledContents(True)

        # Connections of button click events to specific functions
        self.btnSubtitles.clicked.connect(self.subtitles_clicked)
        self.btnDynRange.clicked.connect(self.dynamic_range_clicked)
        self.btnBack.clicked.connect(self.back_clicked)

    # ------------------------------------------------------------
    # [insert name] Function:
    # - called when the given button is clicked
    def subtitles_clicked(self):
        print("Subtitles button clicked!")

    # ------------------------------------------------------------
    # [insert name] Function:
    # - called when the given button is clicked
    def dynamic_range_clicked(self):
        print("Dynamic Range button clicked!")

    #back to main menu Function:
    # - called when the given button is clicked
    def back_clicked(self):
        print("Back to main menu!")

        self.close()




# ------------------------------------------------------------------------------
# PhysMenu Class: 
# - inherits from the QWidget
#     - QWidget is the name in Qt Designer for the Physical Settings widget
#     - go to the Object Inspector in Qt Designer to change it's name
# ------------------------------------------------------------------------------

from MainMenu import MainMenu

# physical menu window class
class PhysMenu(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        # load the ui file for physical menu
        uic.loadUi('ui files/PhysMenu.ui', self)

        pixmap = QPixmap("ui files/Images/physicaldisability.png")
        if pixmap.isNull():
            print("could not load icon")

        self.iconLabel.setPixmap(pixmap)
        self.iconLabel.setScaledContents(True)

        # connect buttons to function
        self.btnBack.clicked.connect(self.main_button_clicked)
        self.controlsPB.clicked.connect(self.controls_button_clicked)
        self.autofirePB.clicked.connect(self.autofire_button_clicked)




    # called when main menu button clicked, opens main menu
    def main_button_clicked(self):
        print('main menu button clicked!')


        # opening main menu window debugging

        try:
            print('creating main menu...')
            self.MainMenu_window = MainMenu()
            print('showing main menu...')
            self.MainMenu_window.show()
            print('closing physical menu...')
            self.close()
            print('done!')
        except Exception as e:
            print(f"error: {e}")
            import traceback
            traceback.print_exc()


    # other button functions called when they are clicked
    def controls_button_clicked(self):
        print('controls menu button clicked!')
    def autofire_button_clicked(self):
        print('autofire menu button clicked!')





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
