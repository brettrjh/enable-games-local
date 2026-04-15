from PyQt6 import QtWidgets, QtGui, QtCore
from PyQt6.QtGui import QImage, QColor
import cv2
import numpy
import ctypes
from dataclasses import dataclass, field
from window_tracker import find_window_by_title_contains, get_window_rect, is_window_focused
from ocr_subtitles import init_tesseract_windows, OCRConfig, ocr_region
#from mss_visuals import window_capture
from capture_backend import BitBltCaptureBackend, WGCCaptureBackend

# region -DATACLASSES
# ------------------------------------------------------------------------------
# 
# 
# Settings Dataclasses
#
#
# ------------------------------------------------------------------------------
# region Visuals
# -- Visual Overlay Settings
@dataclass
class VisualSettings:
    enabled: bool = False
    cb_enabled: bool = False
    ct_enabled: bool = False
    hue_ranges: dict = field(default_factory= lambda: {})
    masks: dict = field(default_factory= lambda: {
        "red": None,
        "orange": None,
        "green": None,
        "magenta": None,
        "pastels": None
    })
    colorblind_type: str = "None"
    colorblind_slider: int = 0
    contrast_val: int = 128
    filtered_img: cv2.Mat = field(default_factory= lambda: {})

    # ----------------------------------------------------------------------------------------
    # Creates the masks; if either visual settings aren't enabled or the colorblind_type
    # is set to "None", returns false. Otherwise, returns True
    def create_masks(self, img, enabled, masks, hue_ranges, colorblind_type):
        if (not enabled):
            return False

        if (colorblind_type == "None"):
            return False
        elif (colorblind_type == "Tritanomaly"):
            masks["green"] = cv2.inRange(img, hue_ranges["lowerGreen"], hue_ranges["upperGreen"])
            masks["orange"] = cv2.inRange(img, hue_ranges["lowerOrange"], hue_ranges["upperOrange"])
            masks["magenta"] = cv2.inRange(img, hue_ranges["lowerMagenta"], hue_ranges["upperMagenta"])
            masks["pastels"] = cv2.inRange(img, hue_ranges["lowerPastels"], hue_ranges["upperPastels"])
        else:
            masks["green"] = cv2.inRange(img, hue_ranges["lowerGreen"], hue_ranges["upperGreen"])
            maskRed1 = cv2.inRange(img, hue_ranges["lowerRed1"], hue_ranges["upperRed1"])
            maskRed2 = cv2.inRange(img, hue_ranges["lowerRed2"], hue_ranges["upperRed2"])
            masks["red"] = maskRed1 + maskRed2
        return True
    
    # ----------------------------------------------------------------------------------------
    # Creates the hue ranges; if either visual settings aren't enabled or the colorblind_type
    # is set to "None", returns false. Otherwise, returns True
    def create_hue_ranges(enabled, hue_ranges, cb_slider_value):
        if (not enabled):
            return False

        # lower hue range multiplier dictionary
        lowerMults = {
            "red": 0.1,
            "orange": 0.1,
            "green": 0.2,
            "magenta": 0.4,
            "pastel": 0.01
        }
        # upper hue range multiplier dictionary
        upperMults = {
            "red": 0.1,
            "orange": 0.1,
            "green": 0.3,
            "magenta": 0.1,
            "pastel": 0.5
        }

        hue_ranges["lowerGreen"] = numpy.array([((80)-(lowerMults["green"] * cb_slider_value))/2, 50, 50]),
        hue_ranges["upperGreen"] = numpy.array([((140)+(upperMults["green"] * cb_slider_value))/2, 255, 255]),
        hue_ranges["lowerOrange"] = numpy.array([((20)-(lowerMults["orange"] * cb_slider_value))/2, 50, 50]),
        hue_ranges["upperOrange"] = numpy.array([((40)-(upperMults["orange"] * cb_slider_value))/2, 255, 255]),
        hue_ranges["lowerMagenta"] = numpy.array([((280)-(lowerMults["magenta"] * cb_slider_value))/2, 50, 50]),
        hue_ranges["upperMagenta"] = numpy.array([((320)+(upperMults["magenta"] * cb_slider_value))/2, 255, 255]),
        hue_ranges["lowerRed1"] = numpy.array([((0)-(lowerMults["red"] * cb_slider_value))/2, 50, 50]),
        hue_ranges["upperRed1"] = numpy.array([((10)+(upperMults["red"] * cb_slider_value))/2, 255, 255]),
        hue_ranges["lowerRed2"] = numpy.array([((355)-(lowerMults["red"] * cb_slider_value))/2, 50, 50]),
        hue_ranges["upperRed2"] = numpy.array([(360/2), 255, 255]),
        hue_ranges["lowerPastels"] = numpy.array([((0)-(lowerMults["pastel"] * cb_slider_value))/2, 50, 50]),
        hue_ranges["upperPastels"] = numpy.array([360/2, numpy.clip(upperMults["pastel"] * cb_slider_value, 10, 100), 255])
# endregion

# region Subtitles
# -- Subtitle overlay settings
@dataclass
class SubtitleSettings:
    enabled: bool = False
    text: str = "Subtitle test"
    color: QColor = field(default_factory=lambda: QColor("white"))
    position: str = "Bottom"   
    background: bool = True
    bg_opacity: int = 60        
    font_size: int = 18
    ocr_x_frac: float = 0.20
    ocr_w_frac: float = 0.60
    ocr_y_frac: float = 0.78
    ocr_h_frac: float = 0.12
    clear_delay_ms: int = 700
# endregion Subtitles
# endregion DATACLASSES







# region -OVERLAYS
# ------------------------------------------------------------------------------
# 
# 
# Screen Overlays
#
#
# ------------------------------------------------------------------------------
# region Visuals
class VisualsOverlay(QtWidgets.QWidget):
    def __init__(self):
        flags = (
            QtCore.Qt.WindowType.FramelessWindowHint | 
            QtCore.Qt.WindowType.Tool | 
            QtCore.Qt.WindowType.Window
        )
        super().__init__(None, flags)
        
        # Allow mouse events to pass through the overlay so the user can interact
        # with underlying windows (prevents system from becoming unclickable)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setWindowFlag(QtCore.Qt.WindowType.WindowDoesNotAcceptFocus, True)
        self.setWindowFlag(QtCore.Qt.WindowType.WindowStaysOnTopHint)

        # -- Reference to the VisualSettings dataclass, HSV, and target window rect
        self.settings = VisualSettings()
        self.value = 0
        self.saturation = 0
        self.suspend_drawing = False

    # Called by OverlayManager: sets the game window as the parent window so that
    # the overlay stays clipped to it and will not appear on top of other windows
    #def set_parent_window(self, hwnd: int):
    #    winHandle = self.windowHandle()
    #    self.gameWindow = QtGui.QWindow.fromWinId(hwnd)
    #    winHandle.setParent(self.gameWindow)
    #def set_window_geometry(self, hwnd: int):
    #    self.winRect = get_window_rect(hwnd)

    def exclude_from_capture(self):
        hwnd = int(self.winId())
        WDA_EXCLUDEFROMCAPTURE = 0x00000011
        result = ctypes.windll.user32.SetWindowDisplayAffinity(hwnd, WDA_EXCLUDEFROMCAPTURE)
        print(f"[VisualsOverlay] SetWindowDisplayAffinity result: {result}")

    # Apply visual settings and show/hide the overlay based on the enabled state
    def apply_settings(self, s: VisualSettings):
        self.settings = s
        if s.enabled:
            self.show()
            self.raise_()
        else:
            self.hide()
        self.update()

    def apply_visuals(self, s: VisualSettings, window):
        if (s.cb_enabled):
            window[:,:,1] = self.saturation
        if (s.ct_enabled):
            window[:,:,2] = self.value
        s.filtered_img = window
        #cv2.imshow('imag', s.filtered_img)
        self.update()

    def set_contrast(self, s: VisualSettings, window):
        # window is already in HSV format
        # assumes contrast settings are enabled
        self.value = window[:,:,2]
        newVal = self.value
        newVal = numpy.clip(((newVal-128) * s.contrast_val + 128), 0, 255)
        self.value = newVal

    def set_colorblind(self, s: VisualSettings, window):
        # window is already in HSV format
        # assumes colorblind settings are enabled
        self.saturation = window[:,:,1]
        newSat = self.saturation

        s.create_masks(window, s.enabled, s.masks, s.hue_ranges, s.colorblind_type)

        # perform colorblind correction
        if (s.colorblind_type == "Protanomaly"):
            newSat[s.masks["green"] > 0] = numpy.clip(newSat[s.masks["green"] > 0] + (2.55*s.colorblind_slider), 0, 255)
            newSat[s.masks["red"] > 0] = numpy.clip(newSat[s.masks["red"] > 0] - (2.55*s.colorblind_slider), 100, 255)
        elif (s.colorblind_type == "Deuteranomaly"):
            newSat[s.masks["green"] > 0] = numpy.clip(newSat[s.masks["green"] > 0] - (2.55*s.colorblind_slider), 50, 255)
            newSat[s.masks["red"] > 0] = numpy.clip(newSat[s.masks["red"] > 0] + (2.55*s.colorblind_slider), 0, 255)
        elif (s.colorblind_type == "Tritanomaly"):
            newSat[s.masks["green"] > 0] = numpy.clip(newSat[s.masks["green"] > 0] + (2.55*s.colorblind_slider), 0, 175)
            newSat[s.masks["magenta"] > 0] = numpy.clip(newSat[s.masks["magenta"] > 0] + (2.55*s.colorblind_slider), 0, 255)
            newSat[s.masks["orange"] > 0] = numpy.clip(newSat[s.masks["orange"] > 0] + (2.55*s.colorblind_slider), 0, 255)
            newSat[s.masks["pastels"] > 0] = numpy.clip(newSat[s.masks["pastels"] > 0] + (2.55*s.colorblind_slider), 0, 150)

        self.saturation = newSat

    def debug_sct(self, s: VisualSettings, img):
        dbg = cv2.cvtColor(img, cv2.COLOR_HSV2BGR)
        cv2.imshow('imag', dbg)
        self.update()

        #s.filtered_img = cv2.imread("ui files/Images/pigment.png")
        #cv2.imshow('imag', s.filtered_img)
        #cv2.imshow('imag', img)
        #self.update()

    # -- Applies the Color and Contrast settings to the window based on the VisualSettings information
    #    this is triggered when update() is called in apply_settings and apply_visuals.
    def paintEvent(self, event: QtGui.QPaintEvent):
        s = self.settings

        if self.suspend_drawing:
            return
        
        p = QtGui.QPainter(self)

        # -- Check to see if there is an image and if not, return
        if s.filtered_img is None:
            return

        # -- Convert filtered image to QImage
        img = cv2.cvtColor(s.filtered_img, cv2.COLOR_HSV2RGB)
        height, width, channel = img.shape
        bytesPerLine = channel * width
        convertedQImg = QImage(img.data, width, height, bytesPerLine, QImage.Format.Format_RGB888)
        #finalImg = convertedQImg.scaled()

        # -- Gets the QRect of the Window
        qrect = QtCore.QRect(self.normalGeometry())

#        print(f"Normal geometry ig: {self.normalGeometry()}")
#        print(f"Image Geometry is: {convertedQImg.rect()}")

        # -- Draw the image
        #p.drawImage(QtCore.QRect.qrect, convertedQImg, QtCore.QRect(convertedQImg.rect()))
        p.drawImage(0, 0, convertedQImg, 0, 0, -1, -1)
# endregion Visuals

# region Subtitles
class SubtitleOverlay(QtWidgets.QWidget):
    def __init__(self):
        flags = (
            QtCore.Qt.WindowType.FramelessWindowHint | 
            QtCore.Qt.WindowType.Tool | 
            QtCore.Qt.WindowType.Window
        )
        super().__init__(None, flags)

        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setWindowFlag(QtCore.Qt.WindowType.WindowDoesNotAcceptFocus, True)
        self.setWindowFlag(QtCore.Qt.WindowType.WindowStaysOnTopHint, True)

        self.settings = SubtitleSettings()

    # Called by OverlayManager: sets the game window as the parent window so that
    # the overlay stays clipped to it and will not appear on top of other windows
    #def set_parent_window(self, hwnd: int):
    #    winHandle = self.windowHandle()
    #    self.gameWindow = QtGui.QWindow.fromWinId(hwnd)
    #    winHandle.setParent(self.gameWindow)

    # Apply subtitle settings and show/hide the overlay based on the enabled state
    def apply_settings(self, s: SubtitleSettings):
        self.settings = s
        if s.enabled:
            self.show()
            self.raise_()
        else:
            self.hide()
        self.update()
    
    # Set the subtitle text and trigger a repaint to update the display
    def set_text(self, text: str):
        self.settings.text = text
        self.update()

    # Override paintEvent to draw the subtitle text with background if enabled
    def paintEvent(self, event: QtGui.QPaintEvent):
        s = self.settings
        if not s.enabled:
            return

        p = QtGui.QPainter(self)
        p.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)

        # Font
        font = QtGui.QFont()
        font.setPointSize(s.font_size)
        p.setFont(font)

        # Measure text
        fm = QtGui.QFontMetrics(font)
        text = s.text or ""
        text_rect = fm.boundingRect(text)

        pad_x, pad_y = 18, 10
        w = text_rect.width() + pad_x * 2
        h = text_rect.height() + pad_y * 2

        x = (self.width() - w) // 2
        if s.position.lower() == "top":
            y = 40
        else:
            y = self.height() - h - 40

        box = QtCore.QRect(x, y, w, h)

        # Background box (only behind text)
        if s.background:
            alpha = int(max(0, min(100, s.bg_opacity)) * 2.55)
            p.setBrush(QtGui.QColor(0, 0, 0, alpha))
            p.setPen(QtCore.Qt.PenStyle.NoPen)
            p.drawRoundedRect(box, 12, 12)

        # Text
        outline_offsets = [(-1, -1), (-1, 0), (-1, 1),
                           (0, -1),           (0, 1),
                           (1, -1),  (1, 0),  (1, 1)]
        
        p.setPen(QtGui.QColor(0, 0, 0))
        for dx, dy in outline_offsets:
            outline_box = QtCore.QRect(box.x() + dx, box.y() + dy, box.width(), box.height())
            p.drawText(outline_box, QtCore.Qt.AlignmentFlag.AlignCenter, text)
        
        p.setPen(s.color)
        p.drawText(box, QtCore.Qt.AlignmentFlag.AlignCenter, text)

    # Placeholder for any future adjustments needed to the inner layout based on the target window's geometry or other factors
    def update_inner_layout_for_window(self):
        pass
# endregion Subtitles
# endregion OVERLAYS





# region -OVERLAY MANAGER
# ------------------------------------------------------------------------------
# 
# 
# Overlay Manager
#
#
# ------------------------------------------------------------------------------
class OverlayManager:
    """Manages one overlay per screen."""
    def __init__(self, app: QtWidgets.QApplication):
        self.app = app
        
        # ==============================
        # Window Tracking (used by all)
        # ==============================
        # State for tracking the target window for overlay attachment
        self.target_hwnd = None
        self.target_title_hint = None

        # Used to track whether or not the game window is in focus
        self.currently_focused = False

        # self.capture_backend = BitBltCaptureBackend()
        self.capture_backend = WGCCaptureBackend()

        # Timer to track the target window's position and update the overlay geometry accordingly
        self.track_timer = QtCore.QTimer()
        self.track_timer.setInterval(100)
        self.track_timer.timeout.connect(self._tick_track_window)

        # ==============================
        # Visuals Initialization 
        # ==============================
        # Visual overlay is a single overlay that we will position on top of the target window to show subtitles
        self.visuals_overlay = VisualsOverlay()
        self.visuals_overlay.hide()

        # Visuals timer for updating visuals every "frame" in the target window
        self.visuals_timer = QtCore.QTimer()
        self.visuals_timer.setInterval(50)
        self.visuals_timer.timeout.connect(self._tick_frame_update)

        # ==============================
        # Subtitles Initialization 
        # ==============================
        init_tesseract_windows() # Prepare Tesseract for OCR use

        # Subtitle overlay is a single overlay that we will position on top of the target window to show subtitles
        self.subtitle_overlay = SubtitleOverlay()
        self.subtitle_overlay.hide()
        self.current_subtitle_settings = SubtitleSettings()

        # OCR timer for periodically updating subtitles from the target window's subtitle region
        self.ocr_timer = QtCore.QTimer()
        self.ocr_timer.setInterval(300)
        self.ocr_timer.timeout.connect(self._tick_ocr)

        self.last_ocr_text = ""
        self.last_text_time = 0
        self.clear_delay_ms = 700

        #for screen in QtGui.QGuiApplication.screens():
        #    o = ScreenOverlay(screen)
        #    o.hide()
        #    self.overlays.append(o)

    # ==============================
    # Show / Hide Functions 
    # ==============================
    def show(self):
        for o in self.overlays:
            # Only show overlays which have a visible effect
            has_brightness = getattr(o, 'brightness_alpha', 0) > 0
            has_tint = getattr(o, 'tint_color', QtGui.QColor(0, 0, 0, 0)).alpha() > 0
            has_cb = getattr(o, 'colorblind_type', '(None)') != '(None)' and getattr(o, 'colorblind_intensity', 0) > 0
            if has_brightness or has_tint or has_cb:
                o.show()
            else:
                o.hide()

    def hide(self):
        for o in self.overlays:
            o.hide()

    #region Window-ing
    # ==============================================
    #
    # Window Tracking, Attach, and Detach Functions
    #
    # ==============================================
    # Attach the overlays to a window by searching for a title substring
    def attach_to_window_title(self, title_hint: str):
        self.target_title_hint = title_hint
        self.target_hwnd = find_window_by_title_contains(title_hint)
        # If the supplied window title exists, proceed with attaching
        if self.target_hwnd:
            self.capture_backend.attach(self.target_hwnd, title_hint)
            print(f"[OverlayManager] Attached to hwnd={self.target_hwnd} for '{title_hint}'")
            self._update_overlay_geometry()
            self.track_timer.start()    # Overlays timers will be started / stopped here

            # Check which overlays have been enabled 
            if self.subtitle_overlay.settings.enabled:
                print(f"[OverlayManager] Subtitles Overlay Attached")
            if self.visuals_overlay.settings.cb_enabled or self.visuals_overlay.settings.ct_enabled:
                print(f"[OverlayManager] Visuals Overlay Attached")
        else:
            print(f"[OverlayManager] Could not find window containing: {title_hint}")

    # ---------------------------------------------------------------------------
    # Update the overlay geometry to match the target window's position and size
    def _update_overlay_geometry(self):
        if not self.target_hwnd:
            return
        rect = get_window_rect(self.target_hwnd)
        if not rect:
            return
        self.subtitle_overlay.setGeometry(rect.x, rect.y, rect.w, rect.h)   # Attaching subtitles overlay
        self.visuals_overlay.setGeometry(rect.x, rect.y, rect.w, rect.h)    # Attaching visuals overlay

    # ------------------------------------------------------------------------------
    # Timer tick to track the target window's position, update the overlay geometry
    # accordingly, and check if the game window is the focused window
    def _tick_track_window(self):
        if self.target_title_hint and (self.target_hwnd is None):
            self.target_hwnd = find_window_by_title_contains(self.target_title_hint)

        if self.target_hwnd is None:
            return
        
        rect = get_window_rect(self.target_hwnd)
        if rect is None:
            return

#        # Reduce terminal spam with a focus check every tick, only print when focus state changes        
#        focused = is_window_focused(self.target_hwnd)
#        print(f"focused is: {focused}. abd currently is: {self.currently_focused}")
#        if focused is False and self.currently_focused is True:
#            print("BOOOOO")
#            if self.subtitle_overlay.settings.enabled:
#                self.stop_ocr()
#                self.subtitle_overlay.hide()
#            if self.visuals_overlay.settings.cb_enabled or self.visuals_overlay.settings.ct_enabled:
#                self.stop_frame_update()
#                self.visuals_overlay.hide()
#            self.currently_focused = False
#        if focused is True and self.currently_focused is False:
#            print("AAAAAAAAA")
#           if self.subtitle_overlay.settings.enabled:
#                self.start_ocr()
#                self.subtitle_overlay.show()
#               self.subtitle_overlay.raise_()
#            if self.visuals_overlay.settings.cb_enabled or self.visuals_overlay.settings.ct_enabled:
#                self.start_frame_update()
#                self.visuals_overlay.show()
#                self.visuals_overlay.raise_()
#            self.currently_focused = True

        # new focus check logic
        focused = is_window_focused(self.target_hwnd)

        if focused and not self.currently_focused:
            print("[OverlayManager] Target window gained focus")
            if self.subtitle_overlay.settings.enabled:
                self.start_ocr()
                self.subtitle_overlay.show()
                self.subtitle_overlay.raise_()
            if self.visuals_overlay.settings.cb_enabled or self.visuals_overlay.settings.ct_enabled:
                self.start_frame_update()
                self.visuals_overlay.show()
                self.visuals_overlay.raise_()
                self.capture_backend.start()
            if self.subtitle_overlay.settings.enabled:
                self.subtitle_overlay.raise_()
            self.currently_focused = True

        elif (not focused) and self.currently_focused:
            print("[OverlayManager] Target window lost focus")
            if self.subtitle_overlay.settings.enabled:
                self.stop_ocr()
                self.subtitle_overlay.hide()
            if self.visuals_overlay.settings.cb_enabled or self.visuals_overlay.settings.ct_enabled:
                self.stop_frame_update()
                self.visuals_overlay.hide()
                self.capture_backend.stop()
            self.currently_focused = False

        # Update subtitle overlay
        self.subtitle_overlay.setGeometry(rect.x, rect.y, rect.w, rect.h)
        self.subtitle_overlay.update_inner_layout_for_window()

        # Update visuals overlay
        self.visuals_overlay.setGeometry(rect.x, rect.y, rect.w, rect.h)

    # -----------------------------------------------------
    # Detach the overlay from any window and stop tracking
    def detach_window(self):
        self.track_timer.stop()
        self.target_hwnd = None
        self.target_title_hint = None
        self.subtitle_overlay.hide()    # Detaching subtitle overlay
        self.stop_frame_update()
        self.stop_ocr()
        self.visuals_overlay.hide()     # Detaching visuals overlay
        print("[OverlayManager] Detached window tracking")
    #endregion


    #region Visuals
    # ============================================================
    #
    # Visuals Management
    # -- To be called in the TweakMenus class 
    #
    # ============================================================
    # ==================
    # Settings Functions
    # Update visual settings and apply them to the overlay
    def set_visuals_settings(self, s: VisualSettings):
        # keep attached geometry updated before showing
        # self._update_overlay_geometry()
        self.visuals_overlay.apply_settings(s)
    
    # ======================
    # Frame Update Functions
    # Start the frame update
    def start_frame_update(self):
        self.visuals_timer.start()

    # Stop the frame update to halt visual processing
    def stop_frame_update(self):
        self.visuals_timer.stop()

    def _tick_frame_update(self):
        # Must have a target window handle
        if not self.target_hwnd:
            return
        
        # Get window rectangle each tick (from Window_Tracker.py)
        # And get window capture w/n that rectangle
        frame = self.capture_backend.get_latest_frame()
        if frame is None:
            return

        #bgr = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
        window = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        if (self.visuals_overlay.settings.ct_enabled):
            self.visuals_overlay.set_contrast(self.visuals_overlay.settings, window)
        if (self.visuals_overlay.settings.cb_enabled):
            self.visuals_overlay.set_colorblind(self.visuals_overlay.settings, window)
        if (self.visuals_overlay.settings.ct_enabled or self.visuals_overlay.settings.cb_enabled):
            self.visuals_overlay.apply_visuals(self.visuals_overlay.settings, window)


    #endregion
    #region Subtitles
    # ==============================================================
    #
    # Subtitle Management
    #
    # ==============================================================
    def set_subtitle_text(self, text: str):
        self.subtitle_overlay.set_text(text)

    # =======================================================
    # Update subtitle settings and apply them to the overlay
    def set_subtitle_settings(self, settings: SubtitleSettings):
        # keep attached geometry updated before showing
        self.current_subtitle_settings = settings
        self.clear_delay_ms = settings.clear_delay_ms
        self._update_overlay_geometry()
        self.subtitle_overlay.apply_settings(settings)
    
    # ===============
    # OCR management
    def start_ocr(self):
        self.ocr_timer.start()

    # Stop the OCR timer to halt periodic OCR processing
    def stop_ocr(self):
        self.ocr_timer.stop()

    # Timer tick to perform OCR on the target window's subtitle region and update the subtitle overlay text
    def _tick_ocr(self):
        # Must have a target window handle
        if not self.target_hwnd:
            return
        
        # Get window rectangle each tick
        rect = get_window_rect(self.target_hwnd)
        if not rect:
            return

        # OCR bottom-center region
        s = self.current_subtitle_settings
        
        x = rect.x + int(rect.w * s.ocr_x_frac)
        w = int(rect.w * s.ocr_w_frac)
        y = rect.y + int(rect.h * s.ocr_y_frac)
        h = int(rect.h * s.ocr_h_frac)

        cfg = OCRConfig(x=x, y=y, w=w, h=h, psm=6)

        try:
            text = ocr_region(cfg)
            print(f"[OCR] '{text}'")
        except Exception as e:
            print("[OCR] error:", e)
            return
        
        import re
        import time

        now = int(time.time() * 1000)

        # If OCR result is empty, don't instantly clear
        if not text or len(text) < 2:
            return

        # Reject absurdly long garbage
        if len(text) > 160:
            return

        # Must contain at least 1 actual word of length 2+
        #words = re.findall(r"[A-Za-z]{2,}", text)
        #if len(words) < 1:
        #   return

        # Ignore if it's exactly the same as last frame; just refresh timer
        if text == self.last_ocr_text:
            self.last_text_time = now
            return

        self.last_ocr_text = text
        self.last_text_time = now
        self.set_subtitle_text(text)

  #endregion
#endregion