import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase only once
if not firebase_admin._apps:
    cred = credentials.Certificate("/data/mitsubishi-2/hos-agent-project/melco_care/hospital-agentic-system/backend/serviceAccount.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

def get_db():
    return db
