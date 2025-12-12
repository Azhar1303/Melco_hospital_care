from db.firebase_client import get_db

db = get_db()

# Test insert
doc_ref = db.collection("test_connection").document("sample")
doc_ref.set({"status": "connected"})

print("✅ Firebase connected successfully!")