"""
Script to update all hospitals with bed and ambulance data.
Run this once to add the new fields.
"""
import sys
sys.path.insert(0, '.')

from db.firebase_client import get_db
import random

db = get_db()

# Get all hospitals
hospitals = db.collection("hospitals").stream()

# Synthetic data ranges
MIN_BEDS = 200
MAX_BEDS = 250
AMBULANCE_COUNT = [7, 8]
OCCUPANCY_RATE = (0.75, 0.90)  # 75-90% occupied

updated = 0
for hosp_doc in hospitals:
    hospital_id = hosp_doc.id
    
    # Generate synthetic data
    total_beds = random.randint(MIN_BEDS, MAX_BEDS)
    occupancy = random.uniform(*OCCUPANCY_RATE)
    beds_available = int(total_beds * (1 - occupancy))
    ambulance_count = random.choice(AMBULANCE_COUNT)
    
    # Update the hospital
    db.collection("hospitals").document(hospital_id).update({
        "total_beds": total_beds,
        "beds_available": beds_available,
        "ambulance_count": ambulance_count
    })
    
    print(f"Updated {hospital_id}: {total_beds} beds, {beds_available} available, {ambulance_count} ambulances")
    updated += 1

print(f"\n✅ Updated {updated} hospitals with bed and ambulance data.")
