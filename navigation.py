from PyQt6 import QtWidgets


def switch_window(current_window: QtWidgets.QWidget, next_window: QtWidgets.QWidget) -> None:
    """Keep a strong application-level reference while switching top-level windows."""
    app = QtWidgets.QApplication.instance()
    if app is not None:
        app.current_window = next_window

    next_window.show()
    current_window.hide()
    current_window.deleteLater()
