import os
from PyQt6 import QtWidgets, uic

from PyQt6.QtGui import QPixmap

from PyQt6.QtCore import QPoint, Qt
from PyQt6.QtGui import QAction, QFont

# needed for connectivity/opening the main menu
import MainMenu

# ------------------------------------------------------------------------------
# VisualMenu Class: 
# - inherits from the QWidget
#     - QWidget is the name in Qt Designer for the Visual Settings widget
#     - go to the Object Inspector in Qt Designer to change it's name
# ------------------------------------------------------------------------------

class VisualMenu(QtWidgets.QWidget):
    # --------------------------------------------------------------
    # Initialization for ui file and connecting buttons to functions
    def __init__(self, on_back=None):
        super().__init__()

        # Load the UI file
        ui_path = os.path.join(os.path.dirname(__file__), "ui files", "eg_visual_settings.ui")
        uic.loadUi(ui_path, self)

        # Set window title and other initialization
        self.setWindowTitle('Visual Settings')
        self.colorOptions.hide()
        #self.frameCard.adjustSize()
        #self.height = self.layoutWindow_2.size().height()
        #self.width = self.layoutWindow_2.size().width()
        #print(f"Here's the height: {self.height}")
        #print(f"Here's the width: {self.width}")

        # button connections
        self.btnColorblind.clicked.connect(self.show_colorblind_menu)
        self.btnContrast.clicked.connect(self.show_contrast_menu)
        self.btnPOIHighlight.clicked.connect(self.show_poi_menu)
        self.btnBack.clicked.connect(self.back)

        # utility variables
        self.isHiddenColorBlind = True

    # back button, returns to main menu
    def back(self):
        try:
            print('creating main menu...')
            self.mainW = MainMenu.MainMenu()
            print('showing main menu...')
            self.mainW.show()
            print('closing visual menu...')
            self.close()
            print('done!')
        except Exception as e:
            print(f"error: {e}")
            import traceback
            traceback.print_exc()
        
    # dropdown menu function
    def _show_menu_below_button(self, button: QtWidgets.QPushButton, menu: QtWidgets.QMenu):
        global_pos = button.mapToGlobal(QPoint(0, button.height()))
        menu.exec(global_pos)
    
    # --------------------------------------------------------------
    # Colorblindess Correction related functions
    # Colorblind menu
    def show_colorblind_menu(self):
        if self.isHiddenColorBlind:
            self.colorOptions.show()
            self.isHiddenColorBlind = False
        else:
            self.colorOptions.hide()
            self.isHiddenColorBlind = True

        #self.layoutWindow_2.frameSize()
        #self.frameCard.adjustSize()


    # Colorblind Selection
    #def colorblind_selection(self):
    
    # --------------------------------------------------------------
    # Contrast Adjustment related functions
    # Contrast menu
    def show_contrast_menu(self):
        menu = QtWidgets.QMenu()

        low_action = QAction("Low", self)
        medium_action = QAction("Medium", self)
        high_action = QAction("High", self)

        menu.addAction(low_action)
        menu.addAction(medium_action)
        menu.addAction(high_action)

        self._show_menu_below_button(self.btnContrast, menu)

    # POI menu
    def show_poi_menu(self):
        menu = QtWidgets.QMenu()

        disable_action = QAction("Disable Highlighting", self)
        enable_action = QAction("Enable Highlighting", self)

        menu.addAction(disable_action)
        menu.addAction(enable_action)

        self._show_menu_below_button(self.btnPOIHighlight, menu)




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
        baseDir = os.path.dirname(__file__)
        ui_path = os.path.join(baseDir, "ui files", "eg_audio_settings.ui")
        uic.loadUi(ui_path, self)
        self.subtitleOptions.hide()

        # Loads the icon dynamically
        img_path = os.path.join(baseDir, "ui files", "Images", "Sound.png")
        pixmap = QPixmap(img_path)
        if pixmap.isNull():
            print("could not laod icon")
        self.iconLabel.setPixmap(pixmap)
        self.iconLabel.setScaledContents(True)

        # Connections of button click events to specific functions
        self.btnSubtitles.clicked.connect(self.toggle_subtitle_options)
        self.btnDynRange.clicked.connect(self.dynamic_range_clicked)
        self.btnBack.clicked.connect(self.back_clicked)

        # Subtitle Preview Label Setup
        self.lblSubtitlePreview.setText("This is a subtitle preview.\nAdjust settings to see changes.")
        self.lblSubtitlePreview.setWordWrap(True)

        # Connections for subtitle options to update preview
        self.chkSubtitleEnabled.toggled.connect(self.update_subtitle_preview)
        self.cmbSubtitleColor.currentIndexChanged.connect(self.update_subtitle_preview)
        self.cmbSubtitlePosition.currentIndexChanged.connect(self.update_subtitle_preview)
        self.chkSubtitleBackground.toggled.connect(self.update_subtitle_preview)
        self.sldSubtitleBgOpacity.valueChanged.connect(self.update_subtitle_preview)
        self.spnSubtitleFontSize.valueChanged.connect(self.update_subtitle_preview)


        # Run once so it matches current default settings
        self.update_subtitle_preview()


    # ------------------------------------------------------------
    # Subtitle Options Toggle Function:
    def toggle_subtitle_options(self):
        if self.subtitleOptions.isVisible():
            self.subtitleOptions.hide()
        else:
            self.subtitleOptions.show()

    # ------------------------------------------------------------
    # Update Subtitle Preview Function:
    def update_subtitle_preview(self):
        enabled = self.chkSubtitleEnabled.isChecked()

    # --- Show/Hide Preview ---
        self.lblSubtitlePreview.setVisible(enabled)

        if not enabled:
            return

    # --- Text Color ---
        selected = self.cmbSubtitleColor.currentText().strip().lower()
        color_map = {
            "White": "white",
            "Yellow": "yellow",
            "Cyan": "cyan",
            "Green": "lime",
            "Red": "red",
            "Blue": "deepskyblue",
            "Default": "white",
            "(none)": "white",
            "none": "white",
        }
        txt_color = color_map.get(selected, selected if selected else "white")

        # --- Background box + opacity ---
        if self.chkSubtitleBackground.isChecked():
            alpha = self.sldSubtitleBgOpacity.value() / 100.0 
            style = (
                f"color: {txt_color};"
                f"background-color: rgba(0, 0, 0, {alpha});"
                "padding: 8px;"
                "border-radius: 6px;"
            )
        else:
            style = f"color: {txt_color}; background: transparent; padding: 8px;"

        self.lblSubtitlePreview.setStyleSheet(style)

        # --- Position in preview box ---
        pos_text = self.cmbSubtitlePosition.currentText().strip().lower()
        if "top" in pos_text:
            self.lblSubtitlePreview.setAlignment(
                Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop
            )
        elif "bottom" in pos_text:
            self.lblSubtitlePreview.setAlignment(
                Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom
            )
        else:
            self.lblSubtitlePreview.setAlignment(
                Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom
            )
        
        # --- Font Size ---
        font = self.lblSubtitlePreview.font()
        font.setPointSize(self.spnSubtitleFontSize.value())
        self.lblSubtitlePreview.setFont(font)


    # ------------------------------------------------------------
    # Dynamic Range Function:
    # - called when the given button is clicked
    def dynamic_range_clicked(self):
        print("Dynamic Range button clicked!")

    #back to main menu Function:
    # - called when the given button is clicked
    def back_clicked(self):
        print("Back to main menu!")
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
# PhysMenu Class: 
# - inherits from the QWidget
#     - QWidget is the name in Qt Designer for the Physical Settings widget
#     - go to the Object Inspector in Qt Designer to change it's name
# ------------------------------------------------------------------------------

class PhysMenu(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        # load the ui file for physical menu
        uic.loadUi('ui files/eg_physical_settings.ui', self)
        self.setWindowTitle('Physical Settings')

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
            self.mainW = MainMenu.MainMenu()
            print('showing main menu...')
            self.mainW.show()
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
#if __name__ == "__main__":
#    import sys
#
#    app = QtWidgets.QApplication(sys.argv)  # Create the application
#    visualW = VisualMenu()
#    audioW = AudioMenu()
#    physicalW = PhysMenu()

    # ***** IMPORTANT READ ME PLEASE !!!!!!! *****
    # WHEN TESTING, JUST COMMENT OUT THE .show() METHODS THAT AREN'T
    # YOURS SO IT WILL ONLY SHOW YOUR WINDOW WHILE TESTING
    #visualW.show()                          # Show the visual settings
    #audioW.show()                           # Show the audio settings
    #physicalW.show()                        # Show the physical settings
    
#    sys.exit(app.exec())                    # Run the application's event loop
