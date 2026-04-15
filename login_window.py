import threading
import time
import webbrowser

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QMessageBox

from cognito_auth import CognitoAuth
from theme import BUTTON_HEIGHT, SPACING_MD, WINDOW_SIZE, set_button_variant


class LoginWindow(QWidget):
    login_success = pyqtSignal(dict)
    login_error = pyqtSignal(str)
    status_update = pyqtSignal(str)

    def __init__(self, on_login_success=None):
        super().__init__()

        self.auth = CognitoAuth()
        self.on_login_success = on_login_success
        self.pending_state = None
        self.pending_code_verifier = None

        self.setWindowTitle("Enable Games Login")
        self.resize(min(420, WINDOW_SIZE.width()), 180)

        self.status_label = QLabel("Not signed in")
        self.login_button = QPushButton("Sign in with Cognito")
        self.login_button.setMinimumHeight(BUTTON_HEIGHT)
        self.login_button.clicked.connect(self.start_login)
        set_button_variant(self.login_button, "primary")

        

       

        layout = QVBoxLayout()
        layout.setSpacing(SPACING_MD)
        layout.addWidget(self.status_label)
        layout.addWidget(self.login_button)
        self.setLayout(layout)

        self.status_update.connect(self.status_label.setText)
        self.login_error.connect(self.handle_login_error)
        self.login_success.connect(self.handle_login_success)

    def start_login(self):
        try:
            self.pending_state, self.pending_code_verifier = self.auth.login()
            self.status_update.emit("Browser opened. Finish sign-in there...")
            threading.Thread(target=self.wait_for_callback, daemon=True).start()
        except Exception as e:
            QMessageBox.critical(self, "Login error", str(e))

    def wait_for_callback(self):
        for _ in range(300):
            error = self.auth.auth_result["error"]
            code = self.auth.auth_result["code"]
            returned_state = self.auth.auth_result["state"]

            if error:
                self.login_error.emit(f"Login failed: {error}")
                return

            if code:
                if returned_state != self.pending_state:
                    self.login_error.emit("State mismatch. Login rejected.")
                    return

                try:
                    tokens = self.auth.exchange_code_for_tokens(code, self.pending_code_verifier)
                    self.auth.save_tokens(tokens)
                    self.login_success.emit(tokens)
                except Exception as e:
                    self.login_error.emit(f"Token exchange failed: {e}")
                return

            time.sleep(0.5)

        self.login_error.emit("Login timed out")

    def handle_login_success(self, tokens):
        self.status_label.setText("Signed in successfully")
        if self.on_login_success:
            self.on_login_success(tokens)

    def handle_login_error(self, message):
        self.status_label.setText(message)

    def logout(self):
        self.auth.clear_tokens()
        self.status_label.setText("Logging out...")
        webbrowser.open(self.auth.build_logout_url())
