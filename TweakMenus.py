import os
from PyQt6 import QtWidgets, uic

from PyQt6.QtGui import QPixmap

from PyQt6.QtCore import QPoint, Qt
from PyQt6.QtGui import QAction, QFont

# needed for connectivity/opening the main menu
import MainMenu

# needed for color / contrast correction
import cv2
import numpy
import PIL
from PyQt6.QtGui import QImage
from overlay import OverlayManager

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
   #     self.contrastOptions.hide()
        self.poiOptions.hide()

        # overlay manager (controls full-screen overlays on all screens)
        try:
            self.overlay = OverlayManager(QtWidgets.QApplication.instance())
        except Exception:
            self.overlay = None

        # Loads the color preview dynamically
        self.colorPixmap = QPixmap("ui files/Images/pigment.png")
        if self.colorPixmap.isNull():
            print("could not laod icon")
        self.colorPreview.setPixmap(self.colorPixmap)
        #self.iconLabel.setScaledContents(True)

        # ==============================
        # Button Connections
        # ==============================
        # colorblind utilities
        self.btnColorblind.clicked.connect(self.show_colorblind_menu)
        self.slideColorBlindIntensity.valueChanged.connect(self.colorblind_intensity)
        self.comboxColorBlindType.activated.connect(self.colorblind_type)
        self.isHiddenColorBlind = True
        self.colorblindType = "(None)"
        self.colorFilter = cv2.imread("ui files/Images/pigment.png")
        self.colorFilter = cv2.cvtColor(self.colorFilter, cv2.COLOR_RGB2HSV)
        
        # contrast button connections
        self.btnContrast.clicked.connect(self.show_contrast_menu)
        self.isHiddenContrastCorrection = True

        # POI button connections
        self.btnPOIHighlight.clicked.connect(self.show_poi_menu)
        self.chkPoiMagnifier.toggled.connect(self.toggle_poi_magnifier)
        self.magnifier = None
        self.sldPoiZoom.valueChanged.connect(self.update_poi_zoom_label)
        self.isHiddenPoiMenu = True
        self.update_poi_zoom_label(self.sldPoiZoom.value())

        self.btnBack.clicked.connect(self.back)

        # ==============================
        # Overlay Connections
        # ==============================
        # connect overlay-related controls if overlay manager created
        if getattr(self, 'overlay', None):
            # screen contrast slider -> overlay brightness
            try:
                self.sliderContrastScreen.valueChanged.connect(self.overlay.set_brightness_from_slider)
            except Exception:
                pass

            # colorblind selection -> overlay type
            try:
                self.comboxColorBlindType.currentTextChanged.connect(self.overlay.set_colorblind_type)
            except Exception:
                pass

            # colorblind intensity slider -> overlay intensity
            try:
                self.slideColorBlindIntensity.valueChanged.connect(self.overlay.set_colorblind_intensity)
            except Exception:
                pass

    def toggle_magnifier(self, enabled: bool):
        if enabled:
            if self.magnifier is None:
                self.magnifier = MagnifierWindow(zoom=2.0, size=180)
            self.magnifier.start()
        else:
            if self.magnifier is not None:
                self.magnifier.stop()



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

    def closeEvent(self, event):
        if self.magnifier is not None:
            self.magnifier.stop()
        super().closeEvent(event)

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

    # Colorblind Type
    def colorblind_type(self):
        self.colorblindType = self.comboxColorBlindType.currentText()
        print(f"Current Type Is: {self.colorblindType}")

    # Colorblind Intensity
    def colorblind_intensity(self, value):
        
        # Make orange blue just to test
        hue = self.colorFilter[:,:,0]
        hue = hue + 60
        #if hue[:,:] > 180:
        #    hue[:,:] - 180
        self.colorFilter[:,:,0] = hue
        filteredImg = cv2.cvtColor(self.colorFilter, cv2.COLOR_HSV2RGB)
        # Converting filtered image to Qpixmap
        height, width, channel = filteredImg.shape
        bytesPerLine = 3 * width
        convertedImg = QImage(filteredImg.data, width, height, bytesPerLine, QImage.Format.Format_RGB888)
        QPixmap.convertFromImage(self.colorPixmap, convertedImg)
        # Set colorPreview to filtered pixmap
        self.colorPreview.setPixmap(self.colorPixmap)
        print(f"Value: {value}")

    # --------------------------------------------------------------
    # Contrast Adjustment related functions
    # Contrast menu
    def show_contrast_menu(self):
        if self.isHiddenContrastCorrection:
            self.contrastOptions.show()
            self.isHiddenContrastCorrection = False
        else:
            self.contrastOptions.hide()
            self.isHiddenContrastCorrection = True


    # --------------------------------------------------------------
    # POI Highlighting related functions
    # POI menu
    def show_poi_menu(self):
        if self.isHiddenPoiMenu:
            self.poiOptions.show()
            self.isHiddenPoiMenu = False
        else:
            self.poiOptions.hide()
            self.isHiddenPoiMenu = True

    def toggle_poi_magnifier(self, enabled):
        state = "enabled" if enabled else "disabled"
        print(f"Magnifier {state}")

    def update_poi_zoom_label(self, value):
        self.labelPoiZoomValue.setText(f"{value}x")




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

