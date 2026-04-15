import logging

from PyQt6.QtWidgets import QApplication

from MainMenu import MainMenu
from PresetMenu import PresetMenu
from TweakMenus import AudioMenu, KeybindMenu, PhysMenu, VisualMenu
from login_window import LoginWindow
from navigation import NavigationManager
from overlay import OverlayManager


logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(name)s: %(message)s")

app = QApplication([])

app.overlay_manager = OverlayManager(app)
app.navigation_manager = NavigationManager()

navigation = app.navigation_manager
navigation.register_route("main", lambda: MainMenu())
navigation.register_route("visual", lambda: VisualMenu())
navigation.register_route("audio", lambda: AudioMenu())
navigation.register_route("physical", lambda: PhysMenu())
navigation.register_route("preset", lambda: PresetMenu())
navigation.register_route("keybind", lambda: KeybindMenu())


def handle_login_success(tokens):
    navigation.navigate(login_window, "main")


login_window = LoginWindow(on_login_success=handle_login_success)
navigation.set_route_instance("login", login_window)
navigation.current_route = "login"
login_window.show()

# make both windows reachable from the app
app.login_window = login_window

app.exec()
