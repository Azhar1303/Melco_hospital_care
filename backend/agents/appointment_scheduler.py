from typing import Dict, Any
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage


class AppointmentSchedulerAgent:
    """
    TRUE TOOL AGENT
    """

    def __init__(self, llm: ChatOllama, db):
        self.llm = llm
        self.db = db

    def run(self, user_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        symptoms = context.get("symptoms")
        location = context.get("location")
        preferred_time = context.get("preferred_time")

        if not symptoms:
            return {"success": False, "need_more_info": True, "reason": "Tell me your symptoms."}

        if not location:
            return {"success": False, "need_more_info": True, "reason": "Tell me your city."}

        if not preferred_time:
            return {"success": False, "need_more_info": True, "reason": "When would you like to visit?"}

        department = self._map_symptoms_to_department(symptoms)
        hospitals = self._find_hospitals(location, department)

        if not hospitals:
            return {"success": False, "reason": "No hospital found for this department in your city."}

        doctor, hospital = self._pick_doctor(hospitals, department)

        if not doctor:
            return {"success": False, "reason": "No available doctor right now."}

        # -------- Create appointment --------
        ref = self.db.collection("appointments").document()

        ref.set({
            "patient_id": user_id,
            "doctor_user_id": doctor["doctor_user_id"],
            "doctor_name": doctor["doctor_name"],  # Store name directly
            "hospital_id": hospital["id"],
            "hospital_name": hospital["hospital_name"],  # Store name directly
            "department": department,
            "time": preferred_time,
            "status": "pending",
            "symptoms": symptoms,
        })

        # -------- UPDATE DISEASE HISTORY --------
        self._update_disease_history(user_id, symptoms)

        return {
            "success": True,
            "hospital_name": hospital["hospital_name"],
            "doctor_name": doctor["doctor_name"],
            "department": department,
            "time": preferred_time,
            "appointment_id": ref.id,
        }

    # ---------------- INTERNALS ---------------- #

    def _map_symptoms_to_department(self, symptoms: str) -> str:
        prompt = f"""
Map symptoms to ONE department from:
general medicine, cardiology, orthopedics, dermatology, pediatrics, ent, neurology

Symptoms: {symptoms}
"""
        res = self.llm.invoke([HumanMessage(content=prompt)])
        value = res.content.strip().lower()

        allowed = {
            "general medicine", "cardiology", "orthopedics",
            "dermatology", "pediatrics", "ent", "neurology"
        }

        return value if value in allowed else "general medicine"

    def _find_hospitals(self, location, department):
        docs = self.db.collection("hospitals").where("location", "==", location).stream()
        valid = []

        for d in docs:
            h = d.to_dict()
            dept_list = [x.strip().lower() for x in h.get("departments", "").split(",")]

            if department in dept_list:
                valid.append({"id": d.id, **h})

        return valid

    def _pick_doctor(self, hospitals, department):
        for h in hospitals:
            doctors = [
                d for d in h.get("specialist_available", [])
                if d.get("specialization", "").lower() == department
            ]

            if doctors:
                best = min(doctors, key=lambda x: int(x.get("congestion", 0)))
                return best, h

        return None, None

    def _update_disease_history(self, patient_id: str, symptoms: str):
        """
        Update users/{patient_id}.disease_history:
        - Adds new symptom keywords
        - Does NOT add duplicates
        """

        if not symptoms:
            return

        # Normalize comma-separated keywords
        new_diseases = [
            s.strip().lower()
            for s in symptoms.split(",")
            if s.strip()
        ]

        user_ref = self.db.collection("users").document(patient_id)
        user_doc = user_ref.get()

        if not user_doc.exists:
            return

        user_data = user_doc.to_dict()

        # Only patients should have disease history
        if user_data.get("role") != "patient":
            return

        existing = user_data.get("disease_history", [])
        if not isinstance(existing, list):
            existing = []

        # merge without duplicates
        updated = list(set(existing + new_diseases))

        user_ref.update({"disease_history": updated})
