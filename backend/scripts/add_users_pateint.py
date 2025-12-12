from firebase_update import get_db
import random

db = get_db()

# ---------- ORIGINAL 10 PATIENTS (UPDATED WITH DISEASES) ----------
patients = [
    {"user_id": "p201", "name": "Anil Kumar",    "role": "patient", "location": "Hyderabad",  "disease_history": ["fever"]},
    {"user_id": "p202", "name": "Sunita Kumari", "role": "patient", "location": "Hyderabad",  "disease_history": ["migraine"]},
    {"user_id": "p203", "name": "Rohit Bansal",  "role": "patient", "location": "Delhi",      "disease_history": ["diabetes"]},
    {"user_id": "p204", "name": "Neha Bansal",   "role": "patient", "location": "Delhi",      "disease_history": ["thyroid"]},
    {"user_id": "p205", "name": "Harsh Patel",   "role": "patient", "location": "Ahmedabad",  "disease_history": ["asthma"]},
    {"user_id": "p206", "name": "Komal Patel",   "role": "patient", "location": "Ahmedabad",  "disease_history": ["cold", "cough"]},
    {"user_id": "p207", "name": "Suresh Naidu",  "role": "patient", "location": "Bangalore",  "disease_history": ["hypertension"]},
    {"user_id": "p208", "name": "Latha Naidu",   "role": "patient", "location": "Bangalore",  "disease_history": ["arthritis"]},
    {"user_id": "p209", "name": "Imran Sheikh",  "role": "patient", "location": "Mumbai",     "disease_history": ["allergy"]},
    {"user_id": "p210", "name": "Fatima Sheikh", "role": "patient", "location": "Mumbai",     "disease_history": ["cancer"]},  # ✅ cancer added
]

# ---------- 10 MORE RANDOM PATIENTS ----------
extra_names = [
    "Rahul Verma", "Pooja Shah", "Amit Joshi", "Nisha Mehta", "Karan Malhotra",
    "Riya Kapoor", "Deepak Yadav", "Sneha Iyer", "Mohit Arora", "Tasneem Khan"
]

cities = ["Hyderabad", "Delhi", "Ahmedabad", "Bangalore", "Mumbai"]

disease_pool = [
    "cancer", "diabetes", "asthma", "arthritis",
    "hypertension", "migraine", "thyroid",
    "fever", "allergy", "covid", "cholesterol"
]

extra_patients = []

for i, name in enumerate(extra_names, start=211):
    extra_patients.append({
        "user_id": f"p{i}",
        "name": name,
        "role": "patient",
        "location": random.choice(cities),
        "disease_history": random.sample(disease_pool, k=random.randint(1, 2))
    })

# ---------- COMBINE ALL 20 PATIENTS ----------
all_patients = patients + extra_patients

# ---------- UPLOAD TO FIREBASE ----------
for p in all_patients:
    db.collection("users").document(p["user_id"]).set({
        "name": p["name"],
        "role": p["role"],
        "location": p["location"],
        "disease_history": p["disease_history"]
    })

print("✅ 20 Patients added successfully with full disease history!")
