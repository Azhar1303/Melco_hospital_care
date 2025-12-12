from firebase_update import get_db

db = get_db()

doctors = [
    # {"user_id": "d101", "name": "Dr. Rajesh Mehta", "role": "doctor", "location": "Hyderabad", "doctor_specialization": "general medicine"},
    {"user_id": "d116", "name": "Dr. Sunita Rao", "role": "doctor", "location": "Hyderabad", "doctor_specialization": "general medicine"},
    # {"user_id": "d103", "name": "Dr. Akash Verma", "role": "doctor", "location": "Delhi", "doctor_specialization": "general medicine"},
    # {"user_id": "d104", "name": "Dr. Poonam Khanna", "role": "doctor", "location": "Delhi", "doctor_specialization": "neurology"},
    # {"user_id": "d105", "name": "Dr. Rakesh Patel", "role": "doctor", "location": "Ahmedabad", "doctor_specialization": "cardiology"},
    # {"user_id": "d106", "name": "Dr. Nisha Shah", "role": "doctor", "location": "Ahmedabad", "doctor_specialization": "dermatology"},
    # {"user_id": "d107", "name": "Dr. Manoj Kulkarni", "role": "doctor", "location": "Pune", "doctor_specialization": "orthopedics"},
    # {"user_id": "d108", "name": "Dr. Shilpa Deshmukh", "role": "doctor", "location": "Pune", "doctor_specialization": "pediatrics"},
    # {"user_id": "d109", "name": "Dr. Karthik Reddy", "role": "doctor", "location": "Bangalore", "doctor_specialization": "general medicine"},
    # {"user_id": "d110", "name": "Dr. Ananya Iyer", "role": "doctor", "location": "Bangalore", "doctor_specialization": "pediatrics"},
    # {"user_id": "d111", "name": "Dr. Amit Malhotra", "role": "doctor", "location": "Mumbai", "doctor_specialization": "cardiology"},
    # {"user_id": "d112", "name": "Dr. Ritu Malhotra", "role": "doctor", "location": "Mumbai", "doctor_specialization": "neurology"},
    # {"user_id": "d113", "name": "Dr. Sandeep Joshi", "role": "doctor", "location": "Jaipur", "doctor_specialization": "general medicine"},
    # {"user_id": "d114", "name": "Dr. Kavita Joshi", "role": "doctor", "location": "Jaipur", "doctor_specialization": "dermatology"},
    # {"user_id": "d115", "name": "Dr. Prashant Tiwari", "role": "doctor", "location": "Lucknow", "doctor_specialization": "general medicine"},
]

for doctor in doctors:
    db.collection("users").document(doctor["user_id"]).set({
        "name": doctor["name"],
        "role": doctor["role"],
        "location": doctor["location"],
        "doctor_specialization": doctor["doctor_specialization"]   # ✅ REQUIRED FIELD
    })

print("✅ Doctors with specialization added successfully!")
