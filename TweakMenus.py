import os
from PyQt6 import QtWidgets, uic, QtGui, QtCore

from PyQt6.QtGui import QPixmap

from PyQt6.QtCore import QPoint, Qt
from PyQt6.QtGui import QAction, QFont
from overlay import SubtitleSettings

#Ben added this!!!!!-------------------------
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtCore import QUrl
#------------------------------------------------------

# needed for color / contrast correction
import cv2
import numpy
import PIL
from PyQt6.QtGui import QImage
from overlay import OverlayManager
#needed for magnifier functionality
from magnifier import MagnifierWindow

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
        base_dir = os.path.dirname(__file__)
        ui_path = os.path.join(base_dir, "ui files", "eg_visual_settings.ui")
        uic.loadUi(ui_path, self)

        # Set window title and other initialization
        self.setWindowTitle('Visual Settings')
        self.colorOptions.hide()
        self.contrastOptions.hide()
        self.poiOptions.hide()

        # overlay manager (controls full-screen overlays on all screens)
        try:
            self.overlay = OverlayManager(QtWidgets.QApplication.instance())
        except Exception:
            self.overlay = None

        # Loads the color preview dynamically
        pigment_path = os.path.join(base_dir, "ui files", "Images", "pigment.png")
        self.colorPixmap = QPixmap(pigment_path)
        if self.colorPixmap.isNull():
            print("could not laod icon")
        self.colorPreview.setPixmap(self.colorPixmap)

        # ===================================
        # Colorblind Variables / Connections
        # ===================================
            # button connections
        self.btnColorblind.clicked.connect(self.show_colorblind_menu)
        self.slideColorBlindIntensity.valueChanged.connect(self.colorblind_intensity)
        self.comboxColorBlindType.activated.connect(self.colorblind_type)
            # utilities
        self.isHiddenColorBlind = True
        self.colorblindType = "(None)"
            # get preview image and convert to HSV
        self.colorFilter = cv2.imread("ui files/Images/pigment.png")
        self.colorFilter = cv2.cvtColor(self.colorFilter, cv2.COLOR_BGR2HSV)
            # used for working with the contrast correction, updated in the Colorblind Intensity function
        #self.hueValue = (self.colorFilter[:,:,0])
        self.saturationValue = self.colorFilter[:,:,1]

        # ===================================
        # Contrast Variables / Connections
        # ===================================
            # contrast button connections
        self.btnContrast.clicked.connect(self.show_contrast_menu)
        self.isHiddenContrastCorrection = True
            # min value of slider: 0  |  max value of slider: 100  |  default value: 50 (no change)
        self.sliderContrastScreen.setValue = 50
        self.sliderContrastScreen.valueChanged.connect(self.screen_contrast_correction)
            # get preview image and convert to hsv to change values (V)
        self.contrastFilter = cv2.imread("ui files/Images/pigment.png")
        self.contrastFilter = cv2.cvtColor(self.contrastFilter, cv2.COLOR_BGR2HSV)
            # used for working with the colorblind correction, updated in the Screen Contrast Corretion function
        self.contrastValue = self.contrastFilter[:,:,2]

        # ===================================
        # POI Variables / Connections
        # ===================================
            # POI button connections
        self.btnPOIHighlight.clicked.connect(self.show_poi_menu)
        self.magnifier = self.get_magnifier()
        self.chkPoiMagnifier.toggled.connect(self.toggle_poi_magnifier)
        self.sldPoiZoom.valueChanged.connect(self.update_poi_zoom_label)
        self.isHiddenPoiMenu = True
        self.load_poi_magnifier_state()
        
        # Back to main menu button
        self.btnBack.clicked.connect(self.back)

        # ==============================
        # Overlay Connections
        # ==============================
        # connect overlay-related controls if overlay manager created
        #if getattr(self, 'overlay', None):
            # screen contrast slider -> overlay brightness
            #try:
            #    self.sliderContrastScreen.valueChanged.connect(self.overlay.set_brightness_from_slider)
            #except Exception:
            #    pass

            # colorblind selection -> overlay type
            # try:
            #    self.comboxColorBlindType.currentTextChanged.connect(self.overlay.set_colorblind_type)
            #except Exception:
            #    pass

            # colorblind intensity slider -> overlay intensity
            #try:
            #    self.slideColorBlindIntensity.valueChanged.connect(self.overlay.set_colorblind_intensity)
            #except Exception:
            #    pass

    # back button, returns to main menu
    def back(self):
        try:
            from MainMenu import MainMenu

            print('creating main menu...')
            self.mainW = MainMenu()
            print('showing main menu...')
            self.mainW.show()
            print('closing visual menu...')
            self.close()
            print('done!')
        except Exception as e:
            print(f"error: {e}")
            import traceback
            traceback.print_exc()

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
    def colorblind_intensity(self, slider_value):
        # copy of the original HSV (Hue, Saturation, Value) earlier
        img = self.colorFilter.copy()
        
        # -- [;,;,0] indicates hue    [;,;,1] indicates saturation    [;,;,2] indicates value
        #hue = img[:,:,0]                   # ranges from 0 to 180 (all hues / 2)
        saturation = img[:,:,1]             # ranges from 0 to 255
        value = self.contrastValue          # ranges from 0 to 255
        # -- Bounds are set with the following syntax:
            # lowerBound = numpy.array([hue min, saturation min, value min])
            # upperBound = numpy.array([hue max, saturation max, value max])
        
        # -- Multipliers for adjusting hue bounds based on slider values.
            # Ensures that the slider keeps the bounds between the low range and high range
            # for each color (see the Colorblind Research document for ranges)
        magenta_mult_low = 0.4
        magenta_mult_high = 0.1
        red_mult_low = 0.1
        red_mult_high = 0.1
        green_mult_low = 0.2
        green_mult_high = 0.3
        orange_mult_low = 0.1
        orange_mult_high = 0.1
        pastel_mult_low = 0.01
        pastel_mult_high = 0.5
        sat_mult = 2.55

        # Formulas: 
            # lower bound multiplier = (lower bound of small range) - (lower bound of large range) / 100
            # upper bound multiplier = (upper bound of large range) - (upper bound of small range) / 100
            # small range -> the tighter hue range when the slider is 0
            # large range -> the wider hue range when the slider is 100
            # lowBoundMask = ((lower bound of small range) - (low multiplier * slider value)) / 2
            # highBoundMask = ((upper bound of small range) + (high multiplier * slider value)) / 2

        # -- Process for alterning intensity:
            # The correction is based on getting the right hue range(s) that that color blindness has
            # particular trouble with and increasing or decreasing the saturation accordingly. The process
            # here will be to pull the hue range and create a mask of it, alter the saturation of just that
            # mask (vs the whole image) and re-apply the mask to the image. Lower intensity will utilize a
            # lower hue range and lower saturation for a less intense correciton, while higher intensity
            # will increase the hue range and increase the saturation of the range for a stronger correction. 

        # -- low slider value will shrink the HSV range, high value will increase the range
        if (self.colorblindType == "None"):
            # no colorblindness type selected
            newSat = saturation
        
        elif (self.colorblindType == "Protanomaly"):
            # Protanomaly -- increase greens and decrease reds
            # -- Create the hue ranges (divide by 2 because cv works from 0-180 instead of 0-360)
            lowerGreen = numpy.array([((80)-(green_mult_low * slider_value))/2, 50, 50])
            upperGreen = numpy.array([((140)+(green_mult_high * slider_value))/2, 255, 255])
            lowerRed1 = numpy.array([((0)-(red_mult_low * slider_value))/2, 50, 50])
            upperRed1 = numpy.array([((10)+(red_mult_high * slider_value))/2, 255, 255])
            lowerRed2 = numpy.array([((355)-(red_mult_low * slider_value))/2, 50, 50])
            upperRed2 = numpy.array([(360/2), 255, 255])

            # -- Create the masks to hold the hue ranges that we'll extract saturation from
            #    based on what hues need to increase saturation and which need to decrease it
            maskGreen = cv2.inRange(img, lowerGreen, upperGreen)
            maskRed1 = cv2.inRange(img, lowerRed1, upperRed1)
            maskRed2 = cv2.inRange(img, lowerRed2, upperRed2)
            maskRed = maskRed1 + maskRed2

            # -- Increase the saturation of the masks and make sure they stay in the valid range
            newSat = saturation
            newSat[maskGreen > 0] = numpy.clip(newSat[maskGreen > 0] + (sat_mult*slider_value), 0, 255)
            newSat[maskRed > 0] = numpy.clip(newSat[maskRed > 0] - (sat_mult*slider_value), 100, 255)
        
        elif (self.colorblindType == "Deuteranomaly"):
            # Deuteranomaly -- increase reds and decrease greens
            # -- Create the hue ranges (divide by 2 because cv works from 0-180 instead of 0-360)
            lowerGreen = numpy.array([((80)-(green_mult_low * slider_value))/2, 50, 50])
            upperGreen = numpy.array([((140)+(green_mult_high * slider_value))/2, 255, 255])
            lowerRed1 = numpy.array([((0)-(red_mult_low * slider_value))/2, 50, 50])
            upperRed1 = numpy.array([((10)+(red_mult_high * slider_value))/2, 255, 255])
            lowerRed2 = numpy.array([((355)-(red_mult_low * slider_value))/2, 50, 50])
            upperRed2 = numpy.array([(360/2), 255, 255])

            # -- Create the masks to hold the hue ranges that we'll extract saturation from
            #    based on what hues need to increase saturation and which need to decrease it
            maskGreen = cv2.inRange(img, lowerGreen, upperGreen)
            maskRed1 = cv2.inRange(img, lowerRed1, upperRed1)
            maskRed2 = cv2.inRange(img, lowerRed2, upperRed2)
            maskRed = maskRed1 + maskRed2

            # -- Increase the saturation of the masks and make sure they stay in the valid range
            newSat = saturation
            newSat[maskGreen > 0] = numpy.clip(newSat[maskGreen > 0] - (sat_mult*slider_value), 50, 255)
            newSat[maskRed > 0] = numpy.clip(newSat[maskRed > 0] + (sat_mult*slider_value), 0, 255)
 
        
        elif (self.colorblindType == "Tritanomaly"):
            # Tritanomaly -- increase purples and oranges, slightly increase greens
            #                increase saturation of all pastels
            # -- Create the hue ranges (divide by 2 because cv works from 0-180 instead of 0-360)
            lowerGreen = numpy.array([((80)-(green_mult_low * slider_value))/2, 50, 50])
            upperGreen = numpy.array([((140)+(green_mult_high * slider_value))/2, 255, 255])
            lowerPurple = numpy.array([((280)-(magenta_mult_low * slider_value))/2, 50, 50])
            upperPurple = numpy.array([((320)+(magenta_mult_high * slider_value))/2, 255, 255])
            lowerOrange = numpy.array([((20)-(orange_mult_low * slider_value))/2, 50, 50])
            upperOrange = numpy.array([((40)-(orange_mult_high * slider_value))/2, 255, 255])
            lowerPastels = numpy.array([((0)-(pastel_mult_low * slider_value))/2, 50, 50])
            upperPastels = numpy.array([360/2, numpy.clip(pastel_mult_high * slider_value, 10, 100), 255])

            # -- Create the masks to hold the hue ranges that we'll extract saturation from
            #    based on what hues need to increase saturation and which need to decrease it
            maskGreen = cv2.inRange(img, lowerGreen, upperGreen)
            maskPurple = cv2.inRange(img, lowerPurple, upperPurple)
            maskOrange = cv2.inRange(img, lowerOrange, upperOrange)
            maskPastels = cv2.inRange(img, lowerPastels, upperPastels)

            # -- Increase the saturation of the masks and make sure they stay in the valid range
            newSat = saturation
            newSat[maskGreen > 0] = numpy.clip(newSat[maskGreen > 0] + (sat_mult*slider_value), 0, 175)
            newSat[maskPurple > 0] = numpy.clip(newSat[maskPurple > 0] + (sat_mult*slider_value), 0, 255)
            newSat[maskOrange > 0] = numpy.clip(newSat[maskOrange > 0] + (sat_mult*slider_value), 0, 255)
            newSat[maskPastels > 0] = numpy.clip(newSat[maskPastels > 0] + (sat_mult*slider_value), 0, 150)
 

        # insert saturation, hue, and value into the image and set their variables'
        # values for use in the contrast correction function
        # self.colorFilter[:,:,0] = hue
        img[:,:,1] = newSat
        self.colorFilter[:,:,2] = value
        self.saturationValue = newSat
        
        # convert to RGB
        filteredImg = cv2.cvtColor(img, cv2.COLOR_HSV2RGB)
        # convert to QImage
        height, width, channel = filteredImg.shape
        bytesPerLine = channel * width
        convertedQImg = QImage(filteredImg.data, width, height, bytesPerLine, QImage.Format.Format_RGB888)

        # convert to QPixmap and display it in the preview box
        self.colorPreview.setPixmap(QPixmap.fromImage(convertedQImg))
        print(f"Slider: {slider_value}")
    
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

    def screen_contrast_correction(self, value):
        # changing the preview image
        # get a contrast value based on slider position
        # if contrast < 1.0 = dimmer  |  if contrast > 1.0 = brighter
        contrast = 1.0 + ((value - 50) / 100)
        contrast = max(0.0, contrast)

        # copy of BGR image which was coverted to HSV (Hue, Saturation, Value) earlier
        img = self.contrastFilter.copy()
            
        # This last slot in the array has a 2, meaning value | 1 means saturation | 0 means hue
        value = img[:, :, 2] # orginal value (V) of image
        mid = 128.0
        # update the value with the contrast variable
        value = (value - mid) * contrast + mid
        # ensure values stay in the valid range
        value = numpy.clip(value, 0, 255)

        # put value in image and set contrastValue for use in colorblind correction
        # and put the hue and saturation from colorblind correction into the image
        # img[:,:,0] = self.hueValue
        img[:,:,1] = self.saturationValue
        img[:, :, 2] = value
        self.contrastValue = value

        # convert to RGB
        filteredImg = cv2.cvtColor(img, cv2.COLOR_HSV2RGB)
        # convert to QImage
        height, width, channel = filteredImg.shape
        bytesPerLine = channel * width
        convertedQImg = QImage(filteredImg.data, width, height, bytesPerLine, QImage.Format.Format_RGB888)

        # convert to QPixmap and display it in the preview box
        self.colorPreview.setPixmap(QPixmap.fromImage(convertedQImg))


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
    
    def get_magnifier(self):
        app = QtWidgets.QApplication.instance()
        magnifier = getattr(app, 'poi_magnifier', None)
        if magnifier is None:
            magnifier = MagnifierWindow(zoom=2.0, size=180)
            app.poi_magnifier = magnifier
            app.poi_magnifier_enabled = False
            app.poi_magnifier_zoom = 2.0
        return magnifier

    def load_poi_magnifier_state(self):
        app = QtWidgets.QApplication.instance()
        enabled = bool(getattr(app, 'poi_magnifier_enabled', False))
        zoom = float(getattr(app, 'poi_magnifier_zoom', self.sldPoiZoom.value()))

        self.chkPoiMagnifier.blockSignals(True)
        self.chkPoiMagnifier.setChecked(enabled)
        self.chkPoiMagnifier.blockSignals(False)

        self.sldPoiZoom.blockSignals(True)
        self.sldPoiZoom.setValue(int(zoom))
        self.sldPoiZoom.blockSignals(False)
        self.update_poi_zoom_label(int(zoom))

        if enabled:
            self.magnifier.start()

    # magnifier toggle
    def toggle_poi_magnifier(self, enabled):
        app = QtWidgets.QApplication.instance()
        app.poi_magnifier_enabled = enabled
        app.poi_magnifier_zoom = float(self.sldPoiZoom.value())

        if enabled:
            self.magnifier.set_zoom(app.poi_magnifier_zoom)
            self.magnifier.start()
        else:
            self.magnifier.stop()
    
    # zoom update
    def update_poi_zoom_label(self, value):
        self.labelPoiZoomValue.setText(f"{value}x")
        app = QtWidgets.QApplication.instance()
        if app is not None:
            app.poi_magnifier_zoom = float(value)
        if self.magnifier is not None:
            self.magnifier.set_zoom(float(value))




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
        # overlay manager for subtitle preview
        self.overlay_manager = QtWidgets.QApplication.instance().overlay_manager
        
        # Loads the UI file and sets the window title
        baseDir = os.path.dirname(__file__)
        ui_path = os.path.join(baseDir, "ui files", "eg_audio_settings.ui")
        uic.loadUi(ui_path, self)
        self.subtitleOptions.hide()
        self.dynrangeOptions.hide()

        # Loads the icon dynamically
        img_path = os.path.join(baseDir, "ui files", "Images", "Sound.png")
        pixmap = QPixmap(img_path)
        if pixmap.isNull():
            print("could not laod icon")
        self.iconLabel.setPixmap(pixmap)
        self.iconLabel.setScaledContents(True)

        # ==================================
        # Subtitles Variables / Connections
        # ==================================
            # Connections of button click events to specific functions
        self.btnSubtitles.clicked.connect(self.toggle_subtitle_options)
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

        # ======================================
        # Dynamic Range Variables / Connections
        # ======================================
        self.btnDynRange.clicked.connect(self.dynamic_range_clicked)
        self.cmbRange.currentIndexChanged.connect(self.set_dynamic_range)

        self.btnBack.clicked.connect(self.back_clicked)
    def _show_menu_below_button(self, button: QtWidgets.QPushButton, menu: QtWidgets.QMenu):
        global_pos = button.mapToGlobal(QPoint(0, button.height()))
        menu.exec(global_pos)

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
        # Update the actual overlay settings
        settings = self._settings_from_ui()
        self.overlay_manager.set_subtitle_settings(settings)
        self.overlay_manager.set_subtitle_text("Overlay test subtitle\n(next: OCR will replace this)")
        if settings.enabled:
            self.overlay_manager.attach_to_window_title("Skyrim")  # Example game title, replace with actual target
            self.overlay_manager.start_ocr()
        else:
            self.overlay_manager.stop_ocr()
            self.overlay_manager.detach_window()
    # ------------------------------------------------------------
    # Function to create settings dataclass from UI for easy passing to overlay
    def _settings_from_ui(self):
        color_map = {
            "White": QtGui.QColor("white"),
            "Yellow": QtGui.QColor("yellow"),
            "Cyan": QtGui.QColor("cyan"),
            "Green": QtGui.QColor("lime"),
            "Red": QtGui.QColor("red"),
            "Blue": QtGui.QColor("deepskyblue"),
            "Default": QtGui.QColor("white"),
            "(none)": QtGui.QColor("white"),  
        }
        css_color = color_map.get(self.cmbSubtitleColor.currentText().strip(), QtGui.QColor("white"))
        pos = "top" if "top" in self.cmbSubtitlePosition.currentText().strip().lower() else "bottom"

        return SubtitleSettings(
            enabled=self.chkSubtitleEnabled.isChecked(),
            text="Overlay test subtitle",  # later replaced by OCR output
            color=color_map.get(self.cmbSubtitleColor.currentText(), QtGui.QColor("white")),
            position=self.cmbSubtitlePosition.currentText(),
            background=self.chkSubtitleBackground.isChecked(),
            bg_opacity=self.sldSubtitleBgOpacity.value(),
            font_size=self.spnSubtitleFontSize.value(),
        )


    # ------------------------------------------------------------
    # Dynamic Range Functions
    # ------------------------------------------------------------
    # Dynamic Range Options Toggle Function:
    def dynamic_range_clicked(self):
        if self.dynrangeOptions.isVisible():
            self.dynrangeOptions.hide()
        else:
            self.dynrangeOptions.show()

    def set_dynamic_range(self):
        level = self.cmbRange.currentText().strip().lower()
        self.dynamicRange = level
        #self.btnDynRange.setText(f"Dynamic Range: {level.capitalize()}")
        self.play_dynamic_range_preview(level)

    # Function fot file mapping and playing test audio
    def play_dynamic_range_preview(self, level: str):
        baseDir = os.path.dirname(__file__)
        audio_path = os.path.join(baseDir, "audio")

        file_map = {
            "low (compressed)": "Low.wav",
            "medium": "Medium.wav",
            "high (wide)": "High.wav"
        }

        filename = file_map.get(level)

        if filename:
            full_path = os.path.join(audio_path, filename)
            url = QUrl.fromLocalFile(full_path)
            self.player.setSource(url)
            self.player.play()
    

    # ------------------------------------------------------
    # back to main menu Function:
    # - called when the given button is clicked
    def back_clicked(self):
        print("Back to main menu!")
        try:
            from MainMenu import MainMenu

            print('creating main menu...')
            self.mainW = MainMenu()
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
        base_dir = os.path.dirname(__file__)
        ui_path = os.path.join(base_dir, "ui files", "eg_physical_settings.ui")
        uic.loadUi(ui_path, self)
        self.setWindowTitle('Physical Settings')

        primary_icon = os.path.join(base_dir, "ui files", "Images", "physicaldisability.png")
        fallback_icon = os.path.join(base_dir, "ui files", "Images", "Controller.png")
        icon_path = primary_icon if os.path.exists(primary_icon) else fallback_icon
        pixmap = QPixmap(icon_path)
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
            from MainMenu import MainMenu

            print('creating main menu...')
            self.mainW = MainMenu()
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
