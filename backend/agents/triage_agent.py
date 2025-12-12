# agents/triage_agent.py
"""
Triage Agent for MELCO-Care
- Handles emergency situations
- Dispatches ambulance from nearest available hospital
- Books emergency bed
- 2-hour ambulance return timer
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional


class TriageAgent:
    """
    Handles emergency requests: ambulance dispatch + bed booking.
    """

    def __init__(self, llm, db):
        self.llm = llm
        self.db = db
        self.AMBULANCE_RETURN_HOURS = 2

    # -----------------------------------------------------------
    # MAIN ENTRY: HANDLE EMERGENCY
    # -----------------------------------------------------------
    def handle_emergency(self, user_id: str, location: str) -> Dict[str, Any]:
        """
        Main entry point for emergency handling.
        1. Find nearest hospital with available bed AND ambulance
        2. Dispatch ambulance
        3. Book bed
        4. Create dispatch record
        """
        if not location:
            return {"success": False, "reason": "Location is required for emergency services."}

        # Expire old ambulance dispatches first
        self._restore_returned_ambulances()

        # Find suitable hospital
        hospital = self._find_best_hospital(location)

        if not hospital:
            return {
                "success": False,
                "reason": f"No hospitals with available beds and ambulances found in {location}. Please call emergency services directly."
            }

        hospital_id = hospital.get("id")
        hospital_name = hospital.get("hospital_name", "Unknown")

        # Dispatch ambulance
        ambulance_result = self._dispatch_ambulance(hospital_id)
        if not ambulance_result.get("success"):
            return ambulance_result

        # Book bed
        bed_result = self._book_bed(hospital_id)
        if not bed_result.get("success"):
            # Rollback ambulance if bed booking fails
            self._restore_ambulance(hospital_id)
            return bed_result

        # Create dispatch record
        now = datetime.utcnow()
        ambulance_return_at = now + timedelta(hours=self.AMBULANCE_RETURN_HOURS)

        dispatch_ref = self.db.collection("emergency_dispatches").document()
        dispatch_data = {
            "patient_id": user_id,
            "hospital_id": hospital_id,
            "hospital_name": hospital_name,
            "ambulance_dispatched": True,
            "bed_booked": True,
            "status": "dispatched",
            "created_at": now.isoformat(),
            "ambulance_return_at": ambulance_return_at.isoformat(),
        }
        dispatch_ref.set(dispatch_data)

        return {
            "success": True,
            "dispatch_id": dispatch_ref.id,
            "hospital_id": hospital_id,
            "hospital_name": hospital_name,
            "ambulance_dispatched": True,
            "bed_booked": True,
            "beds_remaining": hospital.get("beds_available", 0) - 1,
            "ambulances_remaining": hospital.get("ambulance_count", 0) - 1,
            "message": f"Emergency services dispatched from {hospital_name}!",
        }

    # -----------------------------------------------------------
    # FIND BEST HOSPITAL
    # -----------------------------------------------------------
    def _find_best_hospital(self, location: str) -> Optional[Dict[str, Any]]:
        """
        Find hospital in location with:
        - At least 1 available bed
        - At least 1 available ambulance
        Prioritizes by most available ambulances (least busy).
        """
        hospitals = self._get_hospitals_by_location(location)

        suitable = []
        for hosp in hospitals:
            beds = hosp.get("beds_available", 0)
            ambulances = hosp.get("ambulance_count", 0)

            if beds > 0 and ambulances > 0:
                suitable.append(hosp)

        if not suitable:
            return None

        # Pick hospital with most ambulances available (least busy)
        return max(suitable, key=lambda x: x.get("ambulance_count", 0))

    # -----------------------------------------------------------
    # DISPATCH AMBULANCE
    # -----------------------------------------------------------
    def _dispatch_ambulance(self, hospital_id: str) -> Dict[str, Any]:
        """
        Decrease ambulance count by 1.
        """
        hosp_ref = self.db.collection("hospitals").document(hospital_id)
        hosp_doc = hosp_ref.get()

        if not hosp_doc.exists:
            return {"success": False, "reason": "Hospital not found."}

        hospital = hosp_doc.to_dict()
        current_count = hospital.get("ambulance_count", 0)

        if current_count < 1:
            return {"success": False, "reason": "No ambulances available at this hospital."}

        hosp_ref.update({"ambulance_count": current_count - 1})
        return {"success": True}

    # -----------------------------------------------------------
    # BOOK BED
    # -----------------------------------------------------------
    def _book_bed(self, hospital_id: str) -> Dict[str, Any]:
        """
        Decrease beds_available by 1.
        """
        hosp_ref = self.db.collection("hospitals").document(hospital_id)
        hosp_doc = hosp_ref.get()

        if not hosp_doc.exists:
            return {"success": False, "reason": "Hospital not found."}

        hospital = hosp_doc.to_dict()
        current_beds = hospital.get("beds_available", 0)

        if current_beds < 1:
            return {"success": False, "reason": "No beds available at this hospital."}

        hosp_ref.update({"beds_available": current_beds - 1})
        return {"success": True}

    # -----------------------------------------------------------
    # RESTORE AMBULANCE (for rollback or return)
    # -----------------------------------------------------------
    def _restore_ambulance(self, hospital_id: str):
        """
        Add 1 back to ambulance count.
        """
        hosp_ref = self.db.collection("hospitals").document(hospital_id)
        hosp_doc = hosp_ref.get()

        if not hosp_doc.exists:
            return

        hospital = hosp_doc.to_dict()
        current_count = hospital.get("ambulance_count", 0)
        hosp_ref.update({"ambulance_count": current_count + 1})

    # -----------------------------------------------------------
    # RESTORE RETURNED AMBULANCES (2-hour expiry)
    # -----------------------------------------------------------
    def _restore_returned_ambulances(self):
        """
        Check all dispatches and restore ambulances that have returned (2hr passed).
        """
        now = datetime.utcnow()

        docs = (
            self.db.collection("emergency_dispatches")
            .where("status", "==", "dispatched")
            .stream()
        )

        for doc in docs:
            data = doc.to_dict()
            return_at_str = data.get("ambulance_return_at")

            if not return_at_str:
                continue

            try:
                return_at = datetime.fromisoformat(return_at_str)
            except ValueError:
                continue

            if now > return_at:
                # Ambulance has returned - restore count
                hospital_id = data.get("hospital_id")
                if hospital_id:
                    self._restore_ambulance(hospital_id)

                # Update dispatch status
                doc.reference.update({"status": "ambulance_returned"})

    # -----------------------------------------------------------
    # GET PATIENT DISPATCHES
    # -----------------------------------------------------------
    def get_patient_dispatches(self, patient_id: str) -> List[Dict[str, Any]]:
        """
        Get all emergency dispatches for a patient.
        """
        self._restore_returned_ambulances()

        docs = (
            self.db.collection("emergency_dispatches")
            .where("patient_id", "==", patient_id)
            .stream()
        )

        dispatches = []
        for doc in docs:
            data = doc.to_dict()
            data["id"] = doc.id
            dispatches.append(data)

        return dispatches

    # -----------------------------------------------------------
    # HELPER: Get hospitals by location
    # -----------------------------------------------------------
    def _get_hospitals_by_location(self, location: str) -> List[Dict[str, Any]]:
        """
        Fetch all hospitals in a given location.
        """
        docs = (
            self.db.collection("hospitals")
            .where("location", "==", location)
            .stream()
        )

        hospitals = []
        for doc in docs:
            data = doc.to_dict()
            data["id"] = doc.id
            hospitals.append(data)

        return hospitals
