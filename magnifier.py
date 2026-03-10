from PyQt6 import QtWidgets
from PyQt6.QtCore import QPoint, Qt, QTimer
from PyQt6.QtGui import QCursor, QGuiApplication


class MagnifierWindow(QtWidgets.QWidget):
    def __init__(self, zoom: float = 2.0, size: int = 180, update_interval_ms: int = 30):
        flags = (
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        super().__init__(None, flags)
        self.zoom = max(1.0, float(zoom))
        self.size = max(50, int(size))
        self.setFixedSize(self.size, self.size)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setWindowFlag(Qt.WindowType.WindowDoesNotAcceptFocus, True)

        self.label = QtWidgets.QLabel(self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setFixedSize(self.size, self.size)
        self.label.setStyleSheet("border: 2px solid #ffffff; border-radius: 4px;")

        self.timer = QTimer(self)
        self.timer.setInterval(update_interval_ms)
        self.timer.timeout.connect(self.update_view)

    def set_zoom(self, zoom: float):
        self.zoom = max(1.0, float(zoom))
        self.update_view()

    def set_size(self, size: int):
        self.size = max(50, int(size))
        self.setFixedSize(self.size, self.size)
        self.label.setFixedSize(self.size, self.size)
        self.update_view()

    def start(self):
        self.show()
        if not self.timer.isActive():
            self.timer.start()
        self.update_view()

    def stop(self):
        self.timer.stop()
        self.hide()

    def update_view(self):
        cursor_pos = QCursor.pos()
        screen = QGuiApplication.screenAt(cursor_pos) or QGuiApplication.primaryScreen()
        if screen is None:
            return

        geom = screen.geometry()
        capture_size = max(1, int(self.size / self.zoom))
        half = capture_size // 2

        capture_x = cursor_pos.x() - geom.x() - half
        capture_y = cursor_pos.y() - geom.y() - half

        capture_x = max(0, min(capture_x, geom.width() - capture_size))
        capture_y = max(0, min(capture_y, geom.height() - capture_size))

        pixmap = screen.grabWindow(0, capture_x, capture_y, capture_size, capture_size)
        if not pixmap.isNull():
            scaled = pixmap.scaled(
                self.size,
                self.size,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            self.label.setPixmap(scaled)

        offset = QPoint(24, 24)
        target_pos = cursor_pos + offset
        max_x = geom.x() + geom.width() - self.size
        max_y = geom.y() + geom.height() - self.size
        target_x = min(max(target_pos.x(), geom.x()), max_x)
        target_y = min(max(target_pos.y(), geom.y()), max_y)
        self.move(target_x, target_y)
