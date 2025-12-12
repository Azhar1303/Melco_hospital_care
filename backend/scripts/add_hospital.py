from firebase_update import get_db

db = get_db()

hospitals = [
    {
        "hospital_id": "h101",
        "hospital_name": "Apollo Hospital",
        "location": "Hyderabad",
        "departments": "General Medicine, Cardiology, Orthopedics",
        "specialist_available": [
            {"doctor_user_id": "d101", "doctor_name": "Dr. Rajesh Mehta", "specialization": "Cardiologist", "congestion": 12},
            {"doctor_user_id": "d102", "doctor_name": "Dr. Sunita Rao", "specialization": "Physician", "congestion": 5},
        ]
    },
    {
        "hospital_id": "h102",
        "hospital_name": "Care Hospital",
        "location": "Hyderabad",
        "departments": "Dermatology, ENT, Pediatrics",
        "specialist_available": [
            {"doctor_user_id": "d102", "doctor_name": "Dr. Sunita Rao", "specialization": "ENT Specialist", "congestion": 7},
        ]
    },
    {
        "hospital_id": "h103",
        "hospital_name": "AIIMS Delhi",
        "location": "Delhi",
        "departments": "Emergency, Medicine, Neurology",
        "specialist_available": [
            {"doctor_user_id": "d103", "doctor_name": "Dr. Akash Verma", "specialization": "Emergency Physician", "congestion": 18},
            {"doctor_user_id": "d104", "doctor_name": "Dr. Poonam Khanna", "specialization": "Neurologist", "congestion": 9},
        ]
    },
    {
        "hospital_id": "h104",
        "hospital_name": "Fortis Hospital",
        "location": "Delhi",
        "departments": "Cardiology, Orthopedics, Urology",
        "specialist_available": [
            {"doctor_user_id": "d104", "doctor_name": "Dr. Poonam Khanna", "specialization": "Urologist", "congestion": 6},
        ]
    },
    {
        "hospital_id": "h105",
        "hospital_name": "Manipal Hospital",
        "location": "Bangalore",
        "departments": "Medicine, Pediatrics, Dermatology",
        "specialist_available": [
            {"doctor_user_id": "d109", "doctor_name": "Dr. Karthik Reddy", "specialization": "Physician", "congestion": 10},
            {"doctor_user_id": "d110", "doctor_name": "Dr. Ananya Iyer", "specialization": "Pediatrician", "congestion": 4},
        ]
    },
    {
        "hospital_id": "h106",
        "hospital_name": "Narayana Health",
        "location": "Bangalore",
        "departments": "Cardiology, Emergency, Orthopedics",
        "specialist_available": [
            {"doctor_user_id": "d109", "doctor_name": "Dr. Karthik Reddy", "specialization": "Cardiologist", "congestion": 15},
        ]
    },
    {
        "hospital_id": "h107",
        "hospital_name": "MIOT Hospital",
        "location": "Chennai",
        "departments": "Orthopedics, Neurology, Medicine",
        "specialist_available": [
            {"doctor_user_id": "d110", "doctor_name": "Dr. Ananya Iyer", "specialization": "Neurologist", "congestion": 8},
        ]
    },
    {
        "hospital_id": "h108",
        "hospital_name": "SRM Hospital",
        "location": "Chennai",
        "departments": "ENT, Pediatrics, Pulmonology",
        "specialist_available": [
            {"doctor_user_id": "d110", "doctor_name": "Dr. Ananya Iyer", "specialization": "Pulmonologist", "congestion": 11},
        ]
    },
    {
        "hospital_id": "h109",
        "hospital_name": "Kokilaben Hospital",
        "location": "Mumbai",
        "departments": "Oncology, Neurology, Medicine",
        "specialist_available": [
            {"doctor_user_id": "d111", "doctor_name": "Dr. Amit Malhotra", "specialization": "Oncologist", "congestion": 14},
            {"doctor_user_id": "d112", "doctor_name": "Dr. Ritu Malhotra", "specialization": "Neurologist", "congestion": 6},
        ]
    },
    {
        "hospital_id": "h110",
        "hospital_name": "Lilavati Hospital",
        "location": "Mumbai",
        "departments": "Cardiology, Emergency, Medicine",
        "specialist_available": [
            {"doctor_user_id": "d111", "doctor_name": "Dr. Amit Malhotra", "specialization": "Cardiologist", "congestion": 20},
        ]
    },
]

for hospital in hospitals:
    db.collection("hospitals").document(hospital["hospital_id"]).set({
        "hospital_name": hospital["hospital_name"],
        "location": hospital["location"],
        "departments": hospital["departments"],
        "specialist_available": hospital["specialist_available"]
    })

print("✅ 10 Hospitals with doctor congestion added successfully!")
