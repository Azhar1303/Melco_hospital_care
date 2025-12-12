import sys
sys.path.insert(0, '.')
from db.firebase_client import get_db
import json

db = get_db()

# Get hospital h101 to see the schema
h = db.collection('hospitals').document('h101').get()
data = h.to_dict()

# Print keys to understand schema
print("Hospital h101 keys:", list(data.keys()))

# Check if medicine_inventory exists
if 'medicine_inventory' in data:
    print("\nMedicine inventory found!")
    print(json.dumps(data['medicine_inventory'], indent=2, default=str))
else:
    print("\nNo medicine_inventory field found in h101")
    print("Available fields:", list(data.keys()))
