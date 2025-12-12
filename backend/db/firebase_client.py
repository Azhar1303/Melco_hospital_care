import firebase_admin
from firebase_admin import credentials, firestore
from config import FIREBASE_CREDENTIAL_PATH, FIREBASE_DB_URL



_app = None
_db = None


def get_db():
    global _app, _db
    if _db is not None:
        return _db

    cred = credentials.Certificate(FIREBASE_CREDENTIAL_PATH)
    _app = firebase_admin.initialize_app(cred, {
        # "projectId": FIREBASE_CREDENTIAL_PATH,
        "databaseURL": FIREBASE_DB_URL,
    })
    _db = firestore.client()
    return _db
