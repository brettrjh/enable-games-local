import base64
import hashlib
import json
import os
import secrets
import threading
import urllib.parse
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer

import requests


class CognitoAuth:
    def __init__(self):
        
        self.cognito_domain = "https://us-east-1fzhmlldk1.auth.us-east-1.amazoncognito.com"
        self.client_id = "7ng34p49pp3ig0ldul8tapfui7"

        
        self.redirect_uri = "http://localhost:8765/callback"
        self.logout_uri = "http://localhost:8765/logout"
        self.scopes = "openid email profile"

        

        self.auth_result = {
            "code": None,
            "state": None,
            "error": None,
        }

        self.server_started = False

    def make_pkce_pair(self):
        code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).rstrip(b"=").decode()
        challenge = hashlib.sha256(code_verifier.encode()).digest()
        code_challenge = base64.urlsafe_b64encode(challenge).rstrip(b"=").decode()
        return code_verifier, code_challenge

    def build_authorize_url(self, state, code_challenge):
        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": self.scopes,
            "state": state,
            "code_challenge_method": "S256",
            "code_challenge": code_challenge,
        }
        return f"{self.cognito_domain}/oauth2/authorize?{urllib.parse.urlencode(params)}"

    def exchange_code_for_tokens(self, code, code_verifier):
        token_url = f"{self.cognito_domain}/oauth2/token"
        data = {
            "grant_type": "authorization_code",
            "client_id": self.client_id,
            "code": code,
            "redirect_uri": self.redirect_uri,
            "code_verifier": code_verifier,
        }
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }

        response = requests.post(token_url, data=data, headers=headers, timeout=20)
        response.raise_for_status()
        return response.json()

    def save_tokens(self, tokens, filename="auth_tokens.json"):
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(tokens, f, indent=2)

    def load_tokens(self, filename="auth_tokens.json"):
        if not os.path.exists(filename):
            return None
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)

    def clear_tokens(self, filename="auth_tokens.json"):
        if os.path.exists(filename):
            os.remove(filename)

    def build_logout_url(self):
        params = {
            "client_id": self.client_id,
            "logout_uri": self.logout_uri,
        }
        return f"{self.cognito_domain}/logout?{urllib.parse.urlencode(params)}"

    def start_local_callback_server(self):
        auth_result = self.auth_result

        class CallbackHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                parsed = urllib.parse.urlparse(self.path)

                if parsed.path == "/callback":
                    params = urllib.parse.parse_qs(parsed.query)
                    auth_result["code"] = params.get("code", [None])[0]
                    auth_result["state"] = params.get("state", [None])[0]
                    auth_result["error"] = params.get("error", [None])[0]
                    auth_result["error_description"] = params.get("error_description", [None])[0]

                    self.send_response(200)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()

                    if auth_result["error"]:
                        message = f"""
                        <html><body>
                        <h2>Login failed</h2>
                        <p><b>Error:</b> {auth_result["error"]}</p>
                        <p><b>Description:</b> {auth_result["error_description"]}</p>
                        </body></html>
                        """
                    else:
                        message = """
                        <html><body>
                        <h2>Login complete. You can close this tab.</h2>
                        </body></html>
                        """

                    self.wfile.write(message.encode("utf-8"))

                elif parsed.path == "/logout":
                    self.send_response(200)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    self.wfile.write(b"""
                        <html><body>
                        <h2>Logged out</h2>
                        <p>You can close this tab.</p>
                        </body></html>
                    """)

                else:
                    self.send_response(404)
                    self.end_headers()

            def log_message(self, format, *args):
                return

        server = HTTPServer(("localhost", 8765), CallbackHandler)
        server.serve_forever()

    def login(self):
        import secrets
        import threading
        import webbrowser

        state = secrets.token_urlsafe(24)
        code_verifier, code_challenge = self.make_pkce_pair()

        # reset auth result
        self.auth_result["code"] = None
        self.auth_result["state"] = None
        self.auth_result["error"] = None
        self.auth_result["error_description"] = None

        # ✅ only start server ONCE
        if not self.server_started:
            server_thread = threading.Thread(
                target=self.start_local_callback_server,
                daemon=True
            )
            server_thread.start()
            self.server_started = True

        auth_url = self.build_authorize_url(state, code_challenge)
        webbrowser.open(auth_url)

        return state, code_verifier