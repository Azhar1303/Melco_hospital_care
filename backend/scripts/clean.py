from firebase_update import get_db
import random

db = get_db()

# ---------------------------------------------------------
# ✅ STEP 1: DELETE ALL EXISTING APPOINTMENTS
# ---------------------------------------------------------

print("🧹 Clearing old appointments...")

docs = db.collection("appointments").stream()
count = 0

for doc in docs:
    db.collection("appointments").document(doc.id).delete()
    count += 1

print(f"✅ Deleted {count} old appointments.")

# ---------------------------------------------------------
# ✅ STEP 2: DEMO USERS & HOSPITALS (MATCH YOUR DB)
# ---------------------------------------------------------

patients = ["p201", "p202", "p203", "p204", "p205"]
doctors = ["d101", "d102", "d103", "d104", "d105"]
hospitals = ["h101", "h102", "h103"]
departments = ["general medicine", "ent", "cardiology", "neurology"]

times = ["today", "tomorrow"]
statuses = ["pending", "accepted", "completed"]

symptom_pool = ["headache","fever", "cough","chest pain","dizziness"]

# ---------------------------------------------------------
# ✅ STEP 3: INSERT CLEAN DEMO APPOINTMENTS
# ---------------------------------------------------------

print("📥 Inserting new demo appointments...")

for i in range(12):
    appointment = {
        "patient_id": random.choice(patients),
        "doctor_user_id": random.choice(doctors),
        "hospital_id": random.choice(hospitals),
        "department": random.choice(departments),
        "time": random.choice(times),
        "status": random.choice(statuses),
        "symptoms": random.choice(symptom_pool),  # ✅ CLEAN LIST
    }

    db.collection("appointments").add(appointment)

print("✅ Demo appointments inserted successfully!")
