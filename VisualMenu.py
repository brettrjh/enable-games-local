import os
from PyQt6 import QtWidgets, uic
from PyQt6.QtCore import QPoint
from PyQt6.QtGui import QAction


class VisualMenu(QtWidgets.QWidget):
    def __init__(self, on_back=None):
        super().__init__()

        # Load the UI file
        ui_path = os.path.join(os.path.dirname(__file__), "ui files", "visual_settings.ui")
        uic.loadUi(ui_path, self)

        # button connections
        self.btnColorblind.clicked.connect(self.show_colorblind_menu)
        self.btnContrast.clicked.connect(self.show_contrast_menu)
        self.btnPOIHighlight.clicked.connect(self.show_poi_menu)

        # back button (just closes now, later will return to main menu)
        if on_back:
            self.btnBack.clicked.connect(on_back)
        else:
            self.btnBack.clicked.connect(self.close)
        
    # dropdown menu function
    def _show_menu_below_button(self, button: QtWidgets.QPushButton, menu: QtWidgets.QMenu):
        global_pos = button.mapToGlobal(QPoint(0, button.height()))
        menu.exec(global_pos)
    
    # Colorblind menu
    def show_colorblind_menu(self):
        menu = QtWidgets.QMenu()

        none_action = QAction("None", self)
        deuteranopia_action = QAction("Deuteranopia", self)
        protanopia_action = QAction("Protanopia", self)
        tritanopia_action = QAction("Tritanopia", self)

        menu.addAction(none_action)
        menu.addAction(deuteranopia_action)
        menu.addAction(protanopia_action)
        menu.addAction(tritanopia_action)

        self._show_menu_below_button(self.btnColorblind, menu)
    
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

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    w = VisualMenu()
    w.setWindowTitle("Visual Tweaks")
    w.show()
    sys.exit(app.exec())