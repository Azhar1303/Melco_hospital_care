import firebase_admin
from firebase_admin import credentials, firestore

# Path to your service account JSON
cred = credentials.Certificate("serviceAccount.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

schema = {}

def walk_collection(collection_ref, container):
    docs = collection_ref.stream()
    for doc in docs:
        doc_entry = {"fields": doc.to_dict(), "subcollections": {}}
        container[doc.id] = doc_entry
        
        # Recursively walk subcollections
        subcollections = doc.reference.collections()
        for sub in subcollections:
            doc_entry["subcollections"][sub.id] = {}
            walk_collection(sub, doc_entry["subcollections"][sub.id])

# Start from root collections
root_collections = db.collections()
for col in root_collections:
    schema[col.id] = {}
    walk_collection(col, schema[col.id])

# Print or save schema
import json
print(json.dumps(schema, indent=4))
