import os
from PyQt6 import QtWidgets, uic

from PyQt6.QtGui import QPixmap

from PyQt6.QtCore import QPoint
from PyQt6.QtGui import QAction

from TweakMenus import VisualMenu, AudioMenu, PhysMenu
from PresetMenu import PresetMenu


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
        
        # Loads the UI file and sets the window title
        uic.loadUi('ui files/eg_main_menu.ui', self)
        self.setWindowTitle('Enable Games')

        # Loads the icon dynamically
        pixmap = QPixmap("ui files/Images/Controller.png")
        if pixmap.isNull():
            print("could not laod icon")
        self.iconLabel.setPixmap(pixmap)
        #self.iconLabel.setScaledContents(True)

        # Connections of button click events to specific functions
        self.btnVisTweaks.clicked.connect(self.visTweaks_clicked)
        self.btnAudTweaks.clicked.connect(self.audTweaks_clicked)
        self.btnPhysTweaks.clicked.connect(self.physTweaks_clicked)
        self.btnPresMenu.clicked.connect(self.presMenu_clicked)

    # ------------------------------------------------------------
    # visTweaks Function:
    # - called when the Visual Tweaks button is clicked

    def visTweaks_clicked(self):
        print("Visual Tweaks button clicked!")
        self.visualW = VisualMenu()
        self.visualW.show()
        self.close()

    # ------------------------------------------------------------
    # audTweaks Function:
    # - called when the Audio Tweaks button is clicked
    def audTweaks_clicked(self):
        print("Audio Tweaks button clicked!")
        self.audioW = AudioMenu()
        self.audioW.show()
        self.close()

    # ------------------------------------------------------------
    # physTweaks Function:
    # - called when the Physical Tweaks button is clicked
    def physTweaks_clicked(self):
        print("Physical Tweaks button clicked!")
        self.physicalW = PhysMenu()
        self.physicalW.show()
        self.close()

    # ------------------------------------------------------------
    # presMenu Function:
    # - called when the Preset Menu button is clicked
    def presMenu_clicked(self):
        print("Preset Menu button clicked!")
        self.presetW = PresetMenu()
        self.presetW.show()
        self.close()




# ---------------------------------------------------------------------------------
# Temporary Script Execution (for testing purposes)
# ---------------------------------------------------------------------------------
#if __name__ == "__main__":
#    import sys
#
#    app = QtWidgets.QApplication(sys.argv)  # Create the application
#    mainW = MainMenu()                      # Create an instance of the MainMenu class
#    mainW.show()                            # Show the main menu
#    sys.exit(app.exec())                    # Run the application's event loop