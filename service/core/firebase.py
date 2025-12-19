import firebase_admin
from firebase_admin import credentials, auth

_app = None

def init_firebase():
    global _app
    if _app is None:
        _app = firebase_admin.initialize_app()
    return _app


def verify_token(token: str) -> dict:
    init_firebase()
    return auth.verify_id_token(token)
