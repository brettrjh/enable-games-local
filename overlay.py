from PyQt6 import QtWidgets, QtGui, QtCore
from dataclasses import dataclass, field
from window_tracker import find_window_by_title_contains, get_window_rect
from ocr_subtitles import init_tesseract_windows, OCRConfig, ocr_region


class ScreenOverlay(QtWidgets.QWidget):
    def __init__(self, screen: QtGui.QScreen):
        flags = QtCore.Qt.WindowType.FramelessWindowHint | QtCore.Qt.WindowType.WindowStaysOnTopHint | QtCore.Qt.WindowType.Tool
        super().__init__(None, flags)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        # Allow mouse events to pass through the overlay so the user can interact
        # with underlying windows (prevents system from becoming unclickable)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        # Keep a reference to the screen this overlay belongs to
        self.screen = screen

        # Try to mark the window as not accepting focus/input to avoid blocking
        # system interaction. Newer Qt versions expose WindowTransparentForInput
        # and WindowDoesNotAcceptFocus; apply them if available.
        try:
            self.setWindowFlag(QtCore.Qt.WindowType.WindowDoesNotAcceptFocus, True)
        except Exception:
            pass
        try:
            # Some Qt builds expose a WindowTransparentForInput flag
            if hasattr(QtCore.Qt.WindowType, 'WindowTransparentForInput'):
                self.setWindowFlag(QtCore.Qt.WindowType.WindowTransparentForInput, True)
        except Exception:
            pass
        geom = screen.geometry()
        self.setGeometry(geom.x(), geom.y(), geom.width(), geom.height())
        self.brightness_alpha = 0  # 0..255 (black overlay)
        self.tint_color = QtGui.QColor(0, 0, 0, 0)  # RGBA
        self.colorblind_type = '(None)'
        self.colorblind_intensity = 0  # 0..100

    def paintEvent(self, event: QtGui.QPaintEvent):
        p = QtGui.QPainter(self)
        rect = self.rect()

        # Brightness: draw a semi-transparent black overlay to darken the screen
        if self.brightness_alpha > 0:
            p.fillRect(rect, QtGui.QColor(0, 0, 0, int(self.brightness_alpha)))

        # Tint: draw a color overlay to tint the screen
        if self.tint_color.alpha() > 0:
            p.fillRect(rect, self.tint_color)

        # Approximate colorblind correction by applying a faint tint overlay
        if self.colorblind_type != '(None)' and self.colorblind_intensity > 0:
            intensity_alpha = int(min(max(self.colorblind_intensity, 0), 100) * 2.0)  # 0..200
            if self.colorblind_type.lower().startswith('prot'):
                # protanomaly -> reduce perceived red by overlaying cyan-ish tint
                cb = QtGui.QColor(0, 200, 200, intensity_alpha)
            elif self.colorblind_type.lower().startswith('deut'):
                # deuteranomaly -> overlay blue-ish tint
                cb = QtGui.QColor(100, 100, 255, intensity_alpha)
            elif self.colorblind_type.lower().startswith('tri'):
                # tritanomaly -> overlay magenta-ish tint
                cb = QtGui.QColor(255, 100, 200, intensity_alpha)
            else:
                cb = QtGui.QColor(255, 255, 255, 0)
            p.fillRect(rect, cb)

# Subtitle overlay settings
@dataclass
class SubtitleSettings:
    enabled: bool = False
    text: str = "Subtitle test"
    color: QtGui.QColor = field(default_factory=lambda: QtGui.QColor("white"))
    position: str = "Bottom"   
    background: bool = True
    bg_opacity: int = 60        
    font_size: int = 18

class SubtitleOverlay(QtWidgets.QWidget):
    def __init__(self):
        flags = (
            QtCore.Qt.WindowType.FramelessWindowHint
            | QtCore.Qt.WindowType.WindowStaysOnTopHint
            | QtCore.Qt.WindowType.Tool
        )
        super().__init__(None, flags)

        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setWindowFlag(QtCore.Qt.WindowType.WindowDoesNotAcceptFocus, True)

        self.settings = SubtitleSettings()

    # Apply subtitle settings and show/hide the overlay based on the enabled state
    def apply_settings(self, s: SubtitleSettings):
        self.settings = s
        if s.enabled:
            self.show()
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
        p.setPen(s.color)
        p.drawText(box, QtCore.Qt.AlignmentFlag.AlignCenter, text)

    # Placeholder for any future adjustments needed to the inner layout based on the target window's geometry or other factors
    def update_inner_layout_for_window(self):
        pass


class OverlayManager:
    """Manages one overlay per screen."""
    def __init__(self, app: QtWidgets.QApplication):
        self.app = app
        
        init_tesseract_windows() # Prepare Tesseract for OCR use

        # Subtitle overlay is a single overlay that we will position on top of the target window to show subtitles
        self.subtitle_overlay = SubtitleOverlay()
        self.subtitle_overlay.hide()
        
        # State for tracking the target window for subtitle overlay attachment
        self.target_hwnd = None
        self.target_title_hint = None

        # Timer to track the target window's position and update the subtitle overlay geometry accordingly
        self.track_timer = QtCore.QTimer()
        self.track_timer.setInterval(100)
        self.track_timer.timeout.connect(self._tick_track_window)

        # Create one ScreenOverlay per screen and keep them in a list
        self.overlays = []

        # OCR timer for periodically updating subtitles from the target window's subtitle region
        self.ocr_timer = QtCore.QTimer()
        self.ocr_timer.setInterval(300)
        self.ocr_timer.timeout.connect(self._tick_ocr)

        for screen in QtGui.QGuiApplication.screens():
            o = ScreenOverlay(screen)
            o.hide()
            self.overlays.append(o)

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

    def set_brightness_from_slider(self, value: int):
        # Map slider 0..100 -> alpha 0..200 (0 = no darkening, 100 = strong)
        alpha = int(value / 100.0 * 200)
        primary = QtGui.QGuiApplication.primaryScreen()
        for o in self.overlays:
            # compare by name/handle if direct object compare fails
            o_screen = getattr(o, 'screen', None)
            is_primary = False
            try:
                is_primary = (o_screen is primary) or (o_screen.name() == primary.name())
            except Exception:
                is_primary = (o_screen is primary)
            if is_primary:
                o.brightness_alpha = alpha
                o.update()
            else:
                # ensure other overlays don't show brightness unless explicitly set
                if getattr(o, 'brightness_alpha', 0) != 0:
                    o.brightness_alpha = 0
                    o.update()
        if alpha > 0:
            self.show()
        else:
            # if turning off brightness, refresh visibility for all overlays
            self.show()

    def set_tint(self, r: int, g: int, b: int, a_percent: int):
        a = int(max(0, min(100, a_percent)) * 2.55)
        primary = QtGui.QGuiApplication.primaryScreen()
        for o in self.overlays:
            o_screen = getattr(o, 'screen', None)
            is_primary = False
            try:
                is_primary = (o_screen is primary) or (o_screen.name() == primary.name())
            except Exception:
                is_primary = (o_screen is primary)
            if is_primary:
                o.tint_color = QtGui.QColor(r, g, b, a)
            else:
                # clear tint on non-primary screens
                if getattr(o, 'tint_color', QtGui.QColor(0,0,0,0)).alpha() != 0:
                    o.tint_color = QtGui.QColor(0, 0, 0, 0)
            o.update()
        if a > 0:
            self.show()

    def set_colorblind_type(self, txt: str):
        primary = QtGui.QGuiApplication.primaryScreen()
        for o in self.overlays:
            o_screen = getattr(o, 'screen', None)
            is_primary = False
            try:
                is_primary = (o_screen is primary) or (o_screen.name() == primary.name())
            except Exception:
                is_primary = (o_screen is primary)
            if is_primary:
                o.colorblind_type = txt
            else:
                if getattr(o, 'colorblind_type', '(None)') != '(None)':
                    o.colorblind_type = '(None)'
            o.update()
        if txt != '(None)':
            self.show()

    def set_colorblind_intensity(self, value: int):
        primary = QtGui.QGuiApplication.primaryScreen()
        for o in self.overlays:
            o_screen = getattr(o, 'screen', None)
            is_primary = False
            try:
                is_primary = (o_screen is primary) or (o_screen.name() == primary.name())
            except Exception:
                is_primary = (o_screen is primary)
            if is_primary:
                o.colorblind_intensity = value
            else:
                if getattr(o, 'colorblind_intensity', 0) != 0:
                    o.colorblind_intensity = 0
            o.update()
        if value > 0:
            self.show()

    # Subtitle overlay management
    def set_subtitle_text(self, text: str):
        self.subtitle_overlay.set_text(text)

    # Attach the subtitle overlay to a window by searching for a title substring
    def attach_to_window_title(self, title_hint: str):
        self.target_title_hint = title_hint
        self.target_hwnd = find_window_by_title_contains(title_hint)
        if self.target_hwnd:
            print(f"[OverlayManager] Attached to hwnd={self.target_hwnd} for '{title_hint}'")
            self._update_subtitle_overlay_geometry()
            self.track_timer.start()
        else:
            print(f"[OverlayManager] Could not find window containing: {title_hint}")

    # Update the subtitle overlay geometry to match the target window's position and size
    def _update_subtitle_overlay_geometry(self):
        if not self.target_hwnd:
            return
        rect = get_window_rect(self.target_hwnd)
        if not rect:
            return
        self.subtitle_overlay.setGeometry(rect.x, rect.y, rect.w, rect.h)

    # Update subtitle settings and apply them to the overlay
    def set_subtitle_settings(self, settings: SubtitleSettings):
        # keep attached geometry updated before showing
        self._update_subtitle_overlay_geometry()
        self.subtitle_overlay.apply_settings(settings)

    # Detach the subtitle overlay from any window and stop tracking
    def detach_window(self):
        self.track_timer.stop()
        self.target_hwnd = None
        self.target_title_hint = None
        self.subtitle_overlay.hide()
        print("[OverlayManager] Detached window tracking")
    
    # Timer tick to track the target window's position and update the subtitle overlay geometry accordingly
    def _tick_track_window(self):
        if self.target_title_hint and (self.target_hwnd is None):
            self.target_hwnd = find_window_by_title_contains(self.target_title_hint)

        if self.target_hwnd is None:
            return
        
        rect = get_window_rect(self.target_hwnd)
        if rect is None:
            return
        
        self.subtitle_overlay.setGeometry(rect.x, rect.y, rect.w, rect.h)
        self.subtitle_overlay.update_inner_layout_for_window()
    
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
        x = rect.x + int(rect.w * 0.10)
        w = int(rect.w * 0.80)
        y = rect.y + int(rect.h * 0.70)
        h = int(rect.h * 0.25)

        cfg = OCRConfig(x=x, y=y, w=w, h=h, psm=6)

        try:
            text = ocr_region(cfg)
        except Exception as e:
            print("[OCR] error:", e)
            return
        
        # If OCR result is empty or garbage, clear overlay text
        if not text or len(text) < 2:
            self.set_subtitle_text("")
            return
        
        if len(text) > 140:
            return
        
        self.set_subtitle_text(text)
