import os
from PyQt6 import QtWidgets, uic
from PyQt6.QtGui import QPixmap

# needed for connectivity/opening the main menu
import MainMenu


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
        
        # for later, helps with getting files as for some reason the previous code here did not work for me (Leo)
        baseDir = os.path.dirname(__file__)

        # Loads the UI file and sets the window title ---> these 3 lines were stolen from visual menu code, but I used a variable
        ui_path = os.path.join(baseDir, "ui files", "eg_presets_menu.ui")
        uic.loadUi(ui_path, self)
        self.setWindowTitle('Preset Menu')

        # Loads the icon dynamically
        img_path = os.path.join(baseDir, "ui files", "Images", "preset_filter_icon.jpg")
        pixmap = QPixmap(img_path)
        if pixmap.isNull():
            print("could not load icon", img_path)
        self.lblImage.setPixmap(pixmap)
        self.lblImage.setScaledContents(True)

        # Connections of button click events to specific functions
        self.btnFilter.clicked.connect(self.on_btnFilter_click)
        self.btnPresetToggle.clicked.connect(self.on_btnPresetToggle_click)
        self.btnDownloads.clicked.connect(self.on_btnDownloads_click)
        self.btnBackToMain.clicked.connect(self.on_btnBackToMain_click)

    # ------------------------------------------------------------
    # Filter Options click Function:
    # - called when the given button is clicked
    def on_btnFilter_click(self):
        print("Filter button was clicked") # remove this later

    # ------------------------------------------------------------
    # Toggle Presets click Function:
    # - called when the given button is clicked
    def on_btnPresetToggle_click(self):
        print("Toggle preset button was clicked") # remove this later

    # ------------------------------------------------------------
    # Downloads Button click Function:
    # - called when the given button is clicked
    def on_btnDownloads_click(self):
        try:
            self.downloadW = PresetDownload()
            self.downloadW.show()
            self.close()
        except Exception as e:
            print(f"error: {e}")
            import traceback
            traceback.print_exc()

    # ------------------------------------------------------------
    # Back Button click Function:
    # - called when the given button is clicked
    def on_btnBackToMain_click(self):
        # return to main menu
        print("Back to main button clicked")
        try:
            print('creating main menu...')
            self.mainW = MainMenu.MainMenu()
            print('showing main menu...')
            self.mainW.show()
            print('closing audio menu...')
            self.close()
            print('done!')
        except Exception as e:
            print(f"error: {e}")
            import traceback
            traceback.print_exc()




# ------------------------------------------------------------------------------
# PresetDownload Class: 
# - inherits from the QWidget
# ------------------------------------------------------------------------------
class PresetDownload(QtWidgets.QWidget):
    # -------------------------------------------------------------
    # Initialization for ui file and connecting buttons to functions
    def __init__(self):
        super().__init__()
        
        # for later, helps with getting files
        baseDir = os.path.dirname(__file__)

        # Loads the UI file and sets the window title
        ui_path = os.path.join(baseDir, "ui files", "eg_preset_download.ui") # add file name here
        uic.loadUi(ui_path, self)
        self.setWindowTitle('Preset Download')

        # Loads the icon dynamically
        img_path = os.path.join(baseDir, "ui files", "Images", "preset_download_icon.png")
        pixmap = QPixmap(img_path)
        if pixmap.isNull():
            print("could not load icon", img_path)
        self.lblImage.setPixmap(pixmap)
        self.lblImage.setScaledContents(True)

        # Connections of button click events to specific functions
        self.btnPresetDownload.clicked.connect(self.on_btnPresetDownload_click)
        self.btnCreator.clicked.connect(self.on_btnCreator_click)
        self.btnReport.clicked.connect(self.on_btnReport_click)
        self.btnBackToPreset.clicked.connect(self.on_btnBackToPreset_click)

    # ------------------------------------------------------------
    # Preset Download click Function:
    # - called when the given button is clicked
    def on_btnPresetDownload_click(self):
        print("Download preset was clicked") # remove this later
    
    # ------------------------------------------------------------
    # Creator click Function:
    # - called when the given button is clicked
    def on_btnCreator_click(self):
        print("More from this creator was clicked") # remove this later


    # ------------------------------------------------------------
    # Report click Function:
    # - called when the given button is clicked
    def on_btnReport_click(self):
        print("Report button was clicked") # remove this later

    # ------------------------------------------------------------
    # Back Button click Function:
    # - called when the given button is clicked
    def on_btnBackToPreset_click(self):
        try:
            self.presetW = PresetMenu()
            self.presetW.show()
            self.close()
        except Exception as e:
            print(f"error: {e}")
            import traceback
            traceback.print_exc()


# ---------------------------------------------------------------------------------
# Temporary Script Execution (for testing purposes)
# ---------------------------------------------------------------------------------
if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)  # Create the application

    # -------------------------------------------------------------------
    # uncomment which menu you want to test here

    presetMenuW = PresetMenu()
    presetMenuW.show()

    #presetDownloadW = PresetDownload()
    #presetDownloadW.show()

    sys.exit(app.exec())                    # Run the application's event loop