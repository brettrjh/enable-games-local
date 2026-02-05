from PyQt6 import QtWidgets, QtGui, QtCore


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


class OverlayManager:
    """Manages one overlay per screen."""
    def __init__(self, app: QtWidgets.QApplication):
        self.app = app
        self.overlays = []
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
