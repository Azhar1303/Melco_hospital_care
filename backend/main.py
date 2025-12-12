from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from agents.orchestrator import OrchestratorAgent
from models.schemas import ChatRequest, OrchestratorResponse
from db.firebase_client import get_db

app = FastAPI(title="Hospital Agentic System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db = get_db()
orchestrator = OrchestratorAgent()


# ---------- HEALTH ----------
@app.get("/health")
def health_check():
    return {"status": "ok"}


# ---------- LOGIN ----------
@app.post("/login")
def login(payload: dict):
    user_id = payload.get("user_id")

    if not user_id:
        return {"success": False, "reason": "User ID missing"}

    user_ref = db.collection("users").document(str(user_id)).get()
    if not user_ref.exists:
        return {"success": False, "reason": "User not found"}

    return {"success": True, "user": user_ref.to_dict()}


# ---------- CHAT (AGENTIC ENTRYPOINT) ----------
@app.post("/chat", response_model=OrchestratorResponse)
def chat_endpoint(payload: ChatRequest):
    try:
        user_ref = db.collection("users").document(payload.user_id).get()
        if not user_ref.exists:
            return OrchestratorResponse(
                session_id=payload.session_id,
                message="Invalid user.",
                next_action="blocked",
                selected_agent=None,
                data=None,
            )

        user = user_ref.to_dict()
        role = user.get("role", "patient")

        result = orchestrator.handle_request(
            user_id=payload.user_id,
            role=role,
            message=payload.message,
            session_id=payload.session_id,
        )

        # Normalize response fields (defensive)
        return OrchestratorResponse(
            session_id=result.get("session_id"),
            message=result.get("message", "Unknown response from orchestrator."),
            next_action=result.get("next_action", "unknown"),
            selected_agent=result.get("selected_agent"),
            data=result.get("data"),
        )

    except Exception as e:
        # Don't ever send empty responses
        return OrchestratorResponse(
            session_id=payload.session_id,
            message=f"Internal server error: {str(e)}",
            next_action="error",
            selected_agent=None,
            data=None,
        )


# ---------- PATIENT APPOINTMENTS ----------
@app.get("/patient/appointments/{patient_id}")
def get_patient_appointments(patient_id: str):
    docs = (
        db.collection("appointments")
        .where("patient_id", "==", str(patient_id))
        .stream()
    )

    results = []

    for d in docs:
        appt = d.to_dict() or {}
        if not isinstance(appt, dict):
            continue

        appt["id"] = d.id

        # Resolve Hospital Name (use stored name first, then fallback to ID lookup)
        if appt.get("hospital_name"):
            pass  # Already has name stored
        else:
            hosp_id = appt.get("hospital_id")
            if hosp_id:
                hosp_ref = db.collection("hospitals").document(str(hosp_id)).get()
                appt["hospital_name"] = (
                    hosp_ref.to_dict().get("hospital_name") if hosp_ref.exists else "Unknown Hospital"
                )
            else:
                appt["hospital_name"] = "Unknown Hospital"

        # Resolve Doctor Name (use stored name first, then fallback to ID lookup)
        if appt.get("doctor_name"):
            pass  # Already has name stored
        else:
            doc_id = appt.get("doctor_user_id")
            if doc_id:
                # First try to get from users collection
                doc_ref = db.collection("users").document(str(doc_id).strip()).get()
                if doc_ref.exists:
                    appt["doctor_name"] = doc_ref.to_dict().get("name", "Unknown Doctor")
                else:
                    # Try to find in hospital's specialist_available
                    hosp_id = appt.get("hospital_id")
                    if hosp_id:
                        hosp_ref = db.collection("hospitals").document(str(hosp_id)).get()
                        if hosp_ref.exists:
                            specialists = hosp_ref.to_dict().get("specialist_available", [])
                            doctor_found = False
                            for spec in specialists:
                                if spec.get("doctor_user_id") == doc_id.strip():
                                    appt["doctor_name"] = spec.get("doctor_name", "Unknown Doctor")
                                    doctor_found = True
                                    break
                            if not doctor_found:
                                appt["doctor_name"] = "Unknown Doctor"
                        else:
                            appt["doctor_name"] = "Unknown Doctor"
                    else:
                        appt["doctor_name"] = "Unknown Doctor"
            else:
                appt["doctor_name"] = "Unknown Doctor"

        results.append(appt)

    return results


# ---------- DOCTOR DECISION ----------
@app.post("/doctor/decision")
def doctor_decision(payload: dict):
    appointment_id = payload.get("appointment_id")
    decision = payload.get("decision")

    if not appointment_id or not decision:
        return {"success": False, "reason": "Missing fields"}

    ref = db.collection("appointments").document(str(appointment_id))
    appt_doc = ref.get()

    if not appt_doc.exists:
        return {"success": False, "reason": "Appointment not found"}

    appt = appt_doc.to_dict() or {}
    old_status = appt.get("status", "pending")

    # Strict state machine
    allowed = {
        "pending": ["accepted", "rejected"],
        "accepted": ["completed", "rejected"],
        "rejected": [],
        "completed": [],
    }

    if decision not in allowed.get(old_status, []):
        return {
            "success": False,
            "reason": f"Invalid transition {old_status} → {decision}",
        }

    # Update appointment status
    ref.update({"status": decision})

    # Update congestion info if possible
    doctor_id = appt.get("doctor_user_id")
    hospital_id = appt.get("hospital_id")

    if doctor_id and hospital_id:
        hosp_ref = db.collection("hospitals").document(str(hospital_id))
        hosp_doc = hosp_ref.get()

        if hosp_doc.exists:
            hosp = hosp_doc.to_dict() or {}
            specialists = hosp.get("specialist_available", []) or []

            for d in specialists:
                if d.get("doctor_user_id") == doctor_id:
                    # increment when pending → accepted
                    if old_status == "pending" and decision == "accepted":
                        d["congestion"] = int(d.get("congestion", 0)) + 1
                    # decrement when accepted → completed/rejected
                    elif old_status == "accepted" and decision in ["completed", "rejected"]:
                        d["congestion"] = max(0, int(d.get("congestion", 0)) - 1)

            hosp_ref.update({"specialist_available": specialists})

    return {
        "success": True,
        "old_status": old_status,
        "new_status": decision,
    }


# ---------- DOCTOR APPOINTMENTS ----------
@app.get("/doctor/appointments/{doctor_id}")
def get_doctor_appointments(doctor_id: str):
    clean_doctor_id = str(doctor_id).strip()

    docs = db.collection("appointments").stream()

    results = []
    for d in docs:
        appt = d.to_dict() or {}
        if not isinstance(appt, dict):
            continue

        stored_id_raw = appt.get("doctor_user_id", "")
        stored_id = str(stored_id_raw).strip()

        if stored_id != clean_doctor_id:
            continue

        appt["id"] = d.id

        # Resolve patient name
        pat_id = appt.get("patient_id")
        if pat_id:
            pat_ref = db.collection("users").document(str(pat_id)).get()
            appt["patient_name"] = (
                pat_ref.to_dict().get("name") if pat_ref.exists else "Unknown"
            )
        else:
            appt["patient_name"] = "Unknown"

        # Resolve hospital name
        hosp_id = appt.get("hospital_id")
        if hosp_id:
            hosp_ref = db.collection("hospitals").document(str(hosp_id)).get()
            appt["hospital_name"] = (
                hosp_ref.to_dict().get("hospital_name") if hosp_ref.exists else "Unknown"
            )
        else:
            appt["hospital_name"] = "Unknown"

        results.append(appt)

    return results


# ---------- ASSIGN FINAL DISEASE ----------
@app.post("/doctor/assign-disease")
def assign_final_disease(payload: dict):
    """
    Allows a doctor to assign a final disease/diagnosis to an appointment.
    Also updates the patient's disease_history in their user profile.
    """
    appointment_id = payload.get("appointment_id")
    final_disease = payload.get("final_disease")
    patient_id = payload.get("patient_id")

    if not appointment_id or not final_disease:
        return {"success": False, "reason": "Missing appointment_id or final_disease"}

    # Update the appointment with the final disease
    appt_ref = db.collection("appointments").document(str(appointment_id))
    appt_doc = appt_ref.get()

    if not appt_doc.exists:
        return {"success": False, "reason": "Appointment not found"}

    appt_ref.update({"final_disease": final_disease.strip()})

    # Also update the patient's disease_history if patient_id is provided
    if patient_id:
        user_ref = db.collection("users").document(str(patient_id))
        user_doc = user_ref.get()

        if user_doc.exists:
            user_data = user_doc.to_dict() or {}
            
            # Only update if user is a patient
            if user_data.get("role") == "patient":
                existing_history = user_data.get("disease_history", [])
                if not isinstance(existing_history, list):
                    existing_history = []

                # Add disease (normalized) if not already present
                normalized_disease = final_disease.strip().lower()
                if normalized_disease not in [d.lower() for d in existing_history]:
                    existing_history.append(normalized_disease)
                    user_ref.update({"disease_history": existing_history})

    return {
        "success": True,
        "message": f"Final diagnosis '{final_disease}' saved successfully.",
        "appointment_id": appointment_id,
    }


# ---------- PHARMACY: RESERVE MEDICINE ----------
@app.post("/pharmacy/reserve")
def reserve_medicine(payload: dict):
    """
    Reserve medicine from a hospital.
    Reduces inventory and creates a 1-hour pickup window.
    """
    from agents.pharmacy_agent import PharmacyAgent
    from langchain_ollama import ChatOllama
    from config import OLLAMA_MODEL, OLLAMA_BASE_URL

    patient_id = payload.get("patient_id")
    hospital_id = payload.get("hospital_id")
    medicine_id = payload.get("medicine_id")
    quantity = payload.get("quantity", 1)

    if not all([patient_id, hospital_id, medicine_id]):
        return {"success": False, "reason": "Missing required fields."}

    llm = ChatOllama(model=OLLAMA_MODEL, base_url=OLLAMA_BASE_URL, temperature=0.0)
    agent = PharmacyAgent(llm, db)

    return agent.reserve_medicine(patient_id, hospital_id, medicine_id, quantity)


# ---------- PHARMACY: GET PATIENT RESERVATIONS ----------
@app.get("/pharmacy/reservations/{patient_id}")
def get_patient_reservations(patient_id: str):
    """
    Get all active medicine reservations for a patient.
    Also expires any old reservations.
    """
    from agents.pharmacy_agent import PharmacyAgent
    from langchain_ollama import ChatOllama
    from config import OLLAMA_MODEL, OLLAMA_BASE_URL

    llm = ChatOllama(model=OLLAMA_MODEL, base_url=OLLAMA_BASE_URL, temperature=0.0)
    agent = PharmacyAgent(llm, db)

    reservations = agent.get_patient_reservations(patient_id)
    return {"success": True, "reservations": reservations}


# ---------- PHARMACY: CANCEL RESERVATION ----------
@app.post("/pharmacy/cancel")
def cancel_reservation(payload: dict):
    """
    Cancel a medicine reservation and restore inventory.
    """
    from agents.pharmacy_agent import PharmacyAgent
    from langchain_ollama import ChatOllama
    from config import OLLAMA_MODEL, OLLAMA_BASE_URL

    reservation_id = payload.get("reservation_id")

    if not reservation_id:
        return {"success": False, "reason": "Reservation ID required."}

    llm = ChatOllama(model=OLLAMA_MODEL, base_url=OLLAMA_BASE_URL, temperature=0.0)
    agent = PharmacyAgent(llm, db)

    return agent.cancel_reservation(reservation_id)


# ---------- PHARMACY: MARK AS PICKED UP ----------
@app.post("/pharmacy/pickup")
def mark_pickup(payload: dict):
    """
    Mark a reservation as picked up.
    """
    from agents.pharmacy_agent import PharmacyAgent
    from langchain_ollama import ChatOllama
    from config import OLLAMA_MODEL, OLLAMA_BASE_URL

    reservation_id = payload.get("reservation_id")

    if not reservation_id:
        return {"success": False, "reason": "Reservation ID required."}

    llm = ChatOllama(model=OLLAMA_MODEL, base_url=OLLAMA_BASE_URL, temperature=0.0)
    agent = PharmacyAgent(llm, db)

    return agent.mark_picked_up(reservation_id)


# ---------- EMERGENCY: REQUEST DISPATCH ----------
@app.post("/emergency/request")
def emergency_request(payload: dict):
    """
    Handle emergency request: dispatch ambulance + book bed.
    """
    from agents.triage_agent import TriageAgent
    from langchain_ollama import ChatOllama
    from config import OLLAMA_MODEL, OLLAMA_BASE_URL

    patient_id = payload.get("patient_id")
    location = payload.get("location")

    if not patient_id:
        return {"success": False, "reason": "Patient ID required."}

    # Get patient location if not provided
    if not location:
        user_ref = db.collection("users").document(str(patient_id)).get()
        if user_ref.exists:
            location = user_ref.to_dict().get("location")

    if not location:
        return {"success": False, "reason": "Location is required for emergency services."}

    llm = ChatOllama(model=OLLAMA_MODEL, base_url=OLLAMA_BASE_URL, temperature=0.0)
    agent = TriageAgent(llm, db)

    return agent.handle_emergency(patient_id, location)


# ---------- EMERGENCY: GET PATIENT DISPATCHES ----------
@app.get("/emergency/dispatches/{patient_id}")
def get_emergency_dispatches(patient_id: str):
    """
    Get all emergency dispatches for a patient.
    """
    from agents.triage_agent import TriageAgent
    from langchain_ollama import ChatOllama
    from config import OLLAMA_MODEL, OLLAMA_BASE_URL

    llm = ChatOllama(model=OLLAMA_MODEL, base_url=OLLAMA_BASE_URL, temperature=0.0)
    agent = TriageAgent(llm, db)

    dispatches = agent.get_patient_dispatches(patient_id)
    return {"success": True, "dispatches": dispatches}
