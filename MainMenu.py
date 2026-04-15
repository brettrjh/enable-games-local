import os
from PyQt6 import QtWidgets, uic

from PyQt6.QtGui import QPixmap

from PyQt6.QtCore import QPoint
from PyQt6.QtGui import QAction

from navigation import get_navigation_manager

from overlay import OverlayManager
from window_tracker import list_open_window_titles

from cognito_auth import CognitoAuth
import webbrowser


# ------------------------------------------------------------------------------
# MainMenu Class: 
# - inherits from the QMainWindow 
#     - (QMainWindow is Qt's name for the primary window when the 
#        application is run, it is not our name for the MainMenu)
# ------------------------------------------------------------------------------
class MainMenu(QtWidgets.QWidget):
    # -------------------------------------------------------------
    # Initialization for ui file and connecting buttons to functions
    def __init__(self):
        super().__init__()
        
        baseDir = os.path.dirname(__file__)

        # overlay manager for subtitle preview
        self.overlay_manager = QtWidgets.QApplication.instance().overlay_manager

        # Loads the UI file and sets the window title
        ui_path = os.path.join(baseDir, "ui files", "eg_main_menu.ui")
        uic.loadUi(ui_path, self)
        self.setWindowTitle('Enable Games')

        # Loads the icon dynamically
        img_path = os.path.join(baseDir, "ui files", "Images", "Controller.png")
        pixmap = QPixmap(img_path)
        if pixmap.isNull():
            print("could not laod icon")
        self.iconLabel.setPixmap(pixmap)
        #self.iconLabel.setScaledContents(True)

        # Connections of button click events to specific functions
        self.btnVisTweaks.clicked.connect(self.visTweaks_clicked)
        self.btnAudTweaks.clicked.connect(self.audTweaks_clicked)
        self.btnPhysTweaks.clicked.connect(self.physTweaks_clicked)
        self.btnPresMenu.clicked.connect(self.presMenu_clicked)

        self.auth = CognitoAuth()

        if hasattr(self, "btnLogout"):
            self.btnLogout.clicked.connect(self.logout_clicked)

        # Connections for game selection and refresh
        self.btnRefreshWindows.clicked.connect(self.refresh_window_list)
        self.btnApplySettings.clicked.connect(self.attach_selected_window)

        # Connections for saving settings
        # === CONNECTIONS FOR SAVING TO DATABASE GO HERE !!! ===

        # Run once so it matches current default settings
        self.refresh_window_list()

    # ------------------------------------------------------------
    # visTweaks Function:
    # - called when the Visual Tweaks button is clicked

    def visTweaks_clicked(self):
        print("Visual Tweaks button clicked!")
        navigation = get_navigation_manager()
        if navigation:
            navigation.navigate(self, "visual")

    # ------------------------------------------------------------
    # audTweaks Function:
    # - called when the Audio Tweaks button is clicked
    def audTweaks_clicked(self):
        print("Audio Tweaks button clicked!")
        navigation = get_navigation_manager()
        if navigation:
            navigation.navigate(self, "audio")

    # ------------------------------------------------------------
    # physTweaks Function:
    # - called when the Physical Tweaks button is clicked
    def physTweaks_clicked(self):
        print("Physical Tweaks button clicked!")
        navigation = get_navigation_manager()
        if navigation:
            navigation.navigate(self, "physical")

    # ------------------------------------------------------------
    # presMenu Function:
    # - called when the Preset Menu button is clicked
    def presMenu_clicked(self):
        print("Preset Menu button clicked!")
        navigation = get_navigation_manager()
        if navigation:
            navigation.navigate(self, "preset")


    #-------------------------------------------------------------
    # Function to Attach Window to Game selected
    def attach_selected_window(self):
        selected_title = self.cmbTargetWindow.currentText().strip()
        if not selected_title:
            print("[AudioMenu] No target window selected.")
            return
        
        print(f"[AudioMenu] Attaching to selected window: {selected_title}")
        self.overlay_manager.attach_to_window_title(selected_title)

    # ------------------------------------------------------------
    # Function to refesh Game list
    def refresh_window_list(self):
        self.cmbTargetWindow.clear()

        titles = list_open_window_titles()

        filtered_titles = []
        ignore_contains = ["Program Manager", "Settings", "Task Switching"]

        for title in titles:
            if any(bad in title for bad in ignore_contains):
                continue
            filtered_titles.append(title)

        self.cmbTargetWindow.addItems(filtered_titles)

    def logout_clicked(self):
        try:
            print("Logging out...")

            self.auth.clear_tokens()
            webbrowser.open(self.auth.build_logout_url())

            app = QtWidgets.QApplication.instance()
            if hasattr(app, "login_window"):
                app.login_window.status_label.setText("Not signed in")
                app.login_window.show()

            self.close()

        except Exception as e:
            print(f"Logout error: {e}")
            import traceback
            traceback.print_exc()
