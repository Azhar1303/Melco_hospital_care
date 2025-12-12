from firebase_update import get_db

db = get_db()

# Refined list of 30 Government Schemes
# - "disease": Single specific name (e.g., "Cancer", "Maternal Health")
# - "amount": Valid non-zero value (imputed conservative estimates where service is free)
all_schemes = [
    {
        "scheme_id": "sch_001",
        "scheme_name": "Ayushman Bharat (PM-JAY)",
        "disease": "Critical Care",
        "amount": 500000,
        "apply_url": "https://pmjay.gov.in"
    },
    {
        "scheme_id": "sch_002",
        "scheme_name": "Aarogyasri (Telangana)",
        "disease": "Surgery",
        "amount": 1000000,
        "apply_url": "https://aarogyasri.telangana.gov.in"
    },
    {
        "scheme_id": "sch_003",
        "scheme_name": "Rashtriya Arogya Nidhi (RAN)",
        "disease": "Cancer",
        "amount": 1500000,
        "apply_url": "https://main.mohfw.gov.in/major-programmes/poor-patients-financial-support"
    },
    {
        "scheme_id": "sch_004",
        "scheme_name": "Health Ministers Discretionary Grant",
        "disease": "General Health",
        "amount": 125000,
        "apply_url": "https://dghs.gov.in/content/1356_3_HealthMinisterDiscretionaryGrant.aspx"
    },
    {
        "scheme_id": "sch_005",
        "scheme_name": "PM National Relief Fund",
        "disease": "Cancer",
        "amount": 300000,
        "apply_url": "https://pmnrf.gov.in/"
    },
    {
        "scheme_id": "sch_006",
        "scheme_name": "Dr. Ambedkar Medical Aid Scheme",
        "disease": "Kidney Disease",
        "amount": 350000,
        "apply_url": "https://socialjustice.gov.in"
    },
    {
        "scheme_id": "sch_007",
        "scheme_name": "Ni-kshay Poshan Yojana",
        "disease": "Tuberculosis",
        "amount": 500,
        "apply_url": "https://www.nikshay.in/"
    },
    {
        "scheme_id": "sch_008",
        "scheme_name": "Janani Suraksha Yojana",
        "disease": "Maternal Health",
        "amount": 1400,
        "apply_url": "https://nhm.gov.in"
    },
    {
        "scheme_id": "sch_009",
        "scheme_name": "Aam Aadmi Bima Yojana",
        "disease": "Disability",
        "amount": 75000,
        "apply_url": "https://licindia.in"
    },
    {
        "scheme_id": "sch_010",
        "scheme_name": "PM Suraksha Bima Yojana",
        "disease": "Accident",
        "amount": 200000,
        "apply_url": "https://www.jansuraksha.gov.in"
    },
    {
        "scheme_id": "sch_011",
        "scheme_name": "Pradhan Mantri Matru Vandana Yojana",
        "disease": "Maternal Health",
        "amount": 5000,
        "apply_url": "https://wcd.nic.in/schemes/pradhan-mantri-matru-vandana-yojana"
    },
    {
        "scheme_id": "sch_012",
        "scheme_name": "Mukhyamantri Amrutum (MA)",
        "disease": "Critical Illness",
        "amount": 500000,
        "apply_url": "https://magujarat.com"
    },
    {
        "scheme_id": "sch_013",
        "scheme_name": "Mahatma Jyotiba Phule Jan Arogya",
        "disease": "Surgery",
        "amount": 250000,
        "apply_url": "https://www.jeevandayee.gov.in"
    },
    {
        "scheme_id": "sch_014",
        "scheme_name": "CMCHIS (Tamil Nadu)",
        "disease": "General Health",
        "amount": 500000,
        "apply_url": "https://www.cmchistn.com"
    },
    {
        "scheme_id": "sch_015",
        "scheme_name": "Karunya Health Scheme",
        "disease": "Cancer",
        "amount": 500000,
        "apply_url": "https://sha.kerala.gov.in"
    },
    {
        "scheme_id": "sch_016",
        "scheme_name": "Bhamashah Swasthya Bima Yojana",
        "disease": "General Health",
        "amount": 300000,
        "apply_url": "https://health.rajasthan.gov.in"
    },
    {
        "scheme_id": "sch_017",
        "scheme_name": "Swasthya Sathi",
        "disease": "General Health",
        "amount": 500000,
        "apply_url": "https://swasthyasathi.gov.in"
    },
    {
        "scheme_id": "sch_018",
        "scheme_name": "Himcare",
        "disease": "General Health",
        "amount": 500000,
        "apply_url": "https://www.hpsbys.in"
    },
    {
        "scheme_id": "sch_019",
        "scheme_name": "Deen Dayal Swasthya Seva Yojana",
        "disease": "General Health",
        "amount": 400000,
        "apply_url": "https://www.ddssygoa.com"
    },
    {
        "scheme_id": "sch_020",
        "scheme_name": "Dr. Muthulakshmi Reddy Maternity Scheme",
        "disease": "Maternal Health",
        "amount": 18000,
        "apply_url": "https://picme.tn.gov.in"
    },
    {
        "scheme_id": "sch_021",
        "scheme_name": "National Leprosy Eradication Programme",
        "disease": "Leprosy",
        "amount": 8000,
        "apply_url": "https://nlep.mohfw.gov.in"
    },
    {
        "scheme_id": "sch_022",
        "scheme_name": "Awaz Health Insurance",
        "disease": "Accident",
        "amount": 200000,
        "apply_url": "https://lc.kerala.gov.in"
    },
    {
        "scheme_id": "sch_023",
        "scheme_name": "West Bengal Health Scheme",
        "disease": "General Health",
        "amount": 100000,
        "apply_url": "https://wbhealthscheme.gov.in"
    },
    {
        "scheme_id": "sch_024",
        "scheme_name": "Atal Amrit Abhiyan",
        "disease": "Cancer",
        "amount": 200000,
        "apply_url": "https://atalamritabhiyan.assam.gov.in"
    },
    {
        "scheme_id": "sch_025",
        "scheme_name": "Chief Ministers Relief Fund",
        "disease": "General Health",
        "amount": 200000,
        "apply_url": "https://cmrf.telangana.gov.in"
    },
    {
        "scheme_id": "sch_026",
        "scheme_name": "Family Planning Indemnity Scheme",
        "disease": "Reproductive Health",
        "amount": 200000,
        "apply_url": "https://nhm.gov.in"
    },
    {
        "scheme_id": "sch_027",
        "scheme_name": "Universal Health Insurance",
        "disease": "General Health",
        "amount": 30000,
        "apply_url": "https://dfs.nic.in"
    },
    {
        "scheme_id": "sch_028",
        "scheme_name": "Ayushman CAPF",
        "disease": "General Health",
        "amount": 500000,
        "apply_url": "https://jha.pmjay.gov.in"
    },
    {
        "scheme_id": "sch_029",
        "scheme_name": "Janani Shishu Suraksha Karyakram",
        "disease": "Maternal Health",
        "amount": 5000,
        "apply_url": "https://nhm.gov.in"
    },
    {
        "scheme_id": "sch_030",
        "scheme_name": "National Dialysis Programme",
        "disease": "Kidney Disease",
        "amount": 100000,
        "apply_url": "https://nhm.gov.in"
    }
]

# 1. DELETE EXISTING SCHEMES (Cleanup)
print("🗑️ Removing previously added schemes...")
try:
    docs = db.collection("schemes").stream()
    deleted_count = 0
    for doc in docs:
        doc.reference.delete()
        deleted_count += 1
    print(f"   Removed {deleted_count} old documents.")
except Exception as e:
    print(f"   Error while clearing collection: {e}")

# 2. ADD NEW SCHEMES
print("🚀 Adding 30 Real Government Schemes...")
for s in all_schemes:
    db.collection("schemes").document(s["scheme_id"]).set(s)

print("✅ 30 Real Government Schemes added successfully!")