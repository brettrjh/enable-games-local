from PyQt6.QtWidgets import QApplication
from MainMenu import MainMenu
from overlay import OverlayManager
from login_window import LoginWindow
from theme import APP_STYLESHEET

app = QApplication([])
app.setStyleSheet(APP_STYLESHEET)

app.overlay_manager = OverlayManager(app)

main_menu = MainMenu()
main_menu.hide()

def handle_login_success(tokens):
    login_window.hide()
    main_menu.show()

login_window = LoginWindow(on_login_success=handle_login_success)
login_window.show()

# make both windows reachable from the app
app.login_window = login_window
app.main_menu = main_menu

app.exec()
