from firebase_update import get_db
import random

db = get_db()

appointments = [
    {
        "appointment_id": "a301",
        "patient_id": "p201",
        "doctor_user_id": "d101",
        "hospital_id": "h101",
        "department": "general medicine",
        "time": "today",
        "status": "pending"
    },
    {
        "appointment_id": "a302",
        "patient_id": "p202",
        "doctor_user_id": "d102",
        "hospital_id": "h102",
        "department": "ent",
        "time": "tomorrow",
        "status": "accepted"
    },
    {
        "appointment_id": "a303",
        "patient_id": "p203",
        "doctor_user_id": "d103",
        "hospital_id": "h103",
        "department": "general medicine",
        "time": "today",
        "status": "pending"
    },
    {
        "appointment_id": "a304",
        "patient_id": "p204",
        "doctor_user_id": "d104",
        "hospital_id": "h104",
        "department": "neurology",
        "time": "tomorrow",
        "status": "rejected"
    },
    {
        "appointment_id": "a305",
        "patient_id": "p205",
        "doctor_user_id": "d105",
        "hospital_id": "h105",
        "department": "cardiology",
        "time": "today",
        "status": "pending"
    },
    {
        "appointment_id": "a306",
        "patient_id": "p206",
        "doctor_user_id": "d106",
        "hospital_id": "h105",
        "department": "dermatology",
        "time": "tomorrow",
        "status": "accepted"
    },
    {
        "appointment_id": "a307",
        "patient_id": "p207",
        "doctor_user_id": "d109",
        "hospital_id": "h105",
        "department": "general medicine",
        "time": "today",
        "status": "pending"
    },
    {
        "appointment_id": "a308",
        "patient_id": "p208",
        "doctor_user_id": "d110",
        "hospital_id": "h105",
        "department": "pediatrics",
        "time": "tomorrow",
        "status": "accepted"
    },
    {
        "appointment_id": "a309",
        "patient_id": "p209",
        "doctor_user_id": "d111",
        "hospital_id": "h109",
        "department": "cardiology",
        "time": "today",
        "status": "pending"
    },
    {
        "appointment_id": "a310",
        "patient_id": "p210",
        "doctor_user_id": "d112",
        "hospital_id": "h109",
        "department": "neurology",
        "time": "tomorrow",
        "status": "pending"
    }
]

for appt in appointments:
    db.collection("appointments").document(appt["appointment_id"]).set({
        "patient_id": appt["patient_id"],
        "doctor_user_id": appt["doctor_user_id"],
        "hospital_id": appt["hospital_id"],
        "department": appt["department"],
        "time": appt["time"],
        "status": appt["status"]
    })

print("✅ 10 Appointments added successfully!")
