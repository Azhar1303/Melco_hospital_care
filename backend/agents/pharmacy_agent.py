# agents/pharmacy_agent.py
"""
Pharmacy Agent for MELCO-Care
- Search medicines by illness/symptoms
- Location-based hospital filtering
- Medicine reservation with 1-hour pickup window
- Auto-expiry and inventory restoration
"""

import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from langchain_core.messages import HumanMessage, SystemMessage


class PharmacyAgent:
    """
    Handles medicine search and reservation with expiry logic.
    """

    def __init__(self, llm, db):
        self.llm = llm
        self.db = db
        self.RESERVATION_EXPIRY_HOURS = 1

    # -----------------------------------------------------------
    # MEDICINE SEARCH
    # -----------------------------------------------------------
    def search_medicine(self, illness: str, location: str) -> Dict[str, Any]:
        """
        Search for medicines that treat the given illness in hospitals at the given location.
        Returns list of available medicines with hospital info.
        """
        if not illness:
            return {"success": False, "reason": "Please describe your illness or symptoms."}

        if not location:
            return {"success": False, "reason": "Location is required to find nearby hospitals."}

        # Get all hospitals in the location
        hospitals = self._get_hospitals_by_location(location)

        if not hospitals:
            return {
                "success": False,
                "reason": f"No hospitals found in {location}."
            }

        # Find matching medicines across all hospitals
        results = []
        for hospital in hospitals:
            hospital_id = hospital.get("id")
            hospital_name = hospital.get("hospital_name", "Unknown")
            inventory = hospital.get("medicine_inventory", [])

            for medicine in inventory:
                if self._medicine_matches_illness(medicine, illness):
                    stock = medicine.get("stock_count", 0)
                    if stock > 0:
                        results.append({
                            "hospital_id": hospital_id,
                            "hospital_name": hospital_name,
                            "medicine_id": medicine.get("medicine_id"),
                            "medicine_name": medicine.get("medicine_name"),
                            "salt_composition": medicine.get("salt_composition"),
                            "manufacturer": medicine.get("manufacturer"),
                            "stock_count": stock,
                            "treats": medicine.get("treats", []),
                        })

        if not results:
            return {
                "success": False,
                "reason": f"No medicines found for '{illness}' in {location}."
            }

        return {
            "success": True,
            "location": location,
            "illness": illness,
            "medicines": results,
        }

    # -----------------------------------------------------------
    # AUTO-RESERVE MEDICINE BY NAME
    # -----------------------------------------------------------
    def auto_reserve_medicine(
        self,
        patient_id: str,
        medicine_name: str,
        location: str,
        quantity: int = 1
    ) -> Dict[str, Any]:
        """
        Automatically find and reserve a specific medicine by name.
        Picks the hospital with highest stock in the user's location.
        """
        if not medicine_name:
            return {"success": False, "reason": "Please specify the medicine name."}

        if not location:
            return {"success": False, "reason": "Location is required to find nearby hospitals."}

        # Get all hospitals in the location
        hospitals = self._get_hospitals_by_location(location)

        if not hospitals:
            return {
                "success": False,
                "reason": f"No hospitals found in {location}."
            }

        # Find the medicine across all hospitals
        matches = []
        medicine_name_lower = medicine_name.lower().strip()

        for hospital in hospitals:
            hospital_id = hospital.get("id")
            hospital_name = hospital.get("hospital_name", "Unknown")
            inventory = hospital.get("medicine_inventory", [])

            for medicine in inventory:
                med_name = medicine.get("medicine_name", "").lower()
                # Match by partial name or full name
                if medicine_name_lower in med_name or med_name in medicine_name_lower:
                    stock = medicine.get("stock_count", 0)
                    if stock >= quantity:
                        matches.append({
                            "hospital_id": hospital_id,
                            "hospital_name": hospital_name,
                            "medicine_id": medicine.get("medicine_id"),
                            "medicine_name": medicine.get("medicine_name"),
                            "stock_count": stock,
                        })

        if not matches:
            return {
                "success": False,
                "reason": f"'{medicine_name}' is not available in {location}. Try a different medicine or location."
            }

        # Pick the hospital with highest stock (best availability)
        best_match = max(matches, key=lambda x: x["stock_count"])

        # Reserve the medicine
        result = self.reserve_medicine(
            patient_id=patient_id,
            hospital_id=best_match["hospital_id"],
            medicine_id=best_match["medicine_id"],
            quantity=quantity
        )

        if result.get("success"):
            result["auto_selected"] = True
            result["selected_hospital"] = best_match["hospital_name"]

        return result

    # -----------------------------------------------------------
    # MEDICINE RESERVATION
    # -----------------------------------------------------------
    def reserve_medicine(
        self,
        patient_id: str,
        hospital_id: str,
        medicine_id: str,
        quantity: int = 1
    ) -> Dict[str, Any]:
        """
        Reserve medicine for pickup. Reduces inventory and creates reservation.
        Reservation expires in 1 hour if not picked up.
        """
        if quantity < 1:
            return {"success": False, "reason": "Quantity must be at least 1."}

        # Get hospital
        hosp_ref = self.db.collection("hospitals").document(hospital_id)
        hosp_doc = hosp_ref.get()

        if not hosp_doc.exists:
            return {"success": False, "reason": "Hospital not found."}

        hospital = hosp_doc.to_dict()
        hospital_name = hospital.get("hospital_name", "Unknown")
        inventory = hospital.get("medicine_inventory", [])

        # Find medicine in inventory
        medicine_idx = None
        medicine_data = None
        for idx, med in enumerate(inventory):
            if med.get("medicine_id") == medicine_id:
                medicine_idx = idx
                medicine_data = med
                break

        if medicine_data is None:
            return {"success": False, "reason": "Medicine not found in this hospital."}

        current_stock = medicine_data.get("stock_count", 0)
        if current_stock < quantity:
            return {
                "success": False,
                "reason": f"Insufficient stock. Only {current_stock} available."
            }

        # Reduce inventory
        inventory[medicine_idx]["stock_count"] = current_stock - quantity
        hosp_ref.update({"medicine_inventory": inventory})

        # Create reservation
        now = datetime.utcnow()
        expires_at = now + timedelta(hours=self.RESERVATION_EXPIRY_HOURS)

        reservation_ref = self.db.collection("medicine_reservations").document()
        reservation_data = {
            "patient_id": patient_id,
            "hospital_id": hospital_id,
            "hospital_name": hospital_name,
            "medicine_id": medicine_id,
            "medicine_name": medicine_data.get("medicine_name"),
            "quantity": quantity,
            "status": "reserved",
            "created_at": now.isoformat(),
            "expires_at": expires_at.isoformat(),
            "picked_up_at": None,
        }
        reservation_ref.set(reservation_data)

        return {
            "success": True,
            "reservation_id": reservation_ref.id,
            "hospital_name": hospital_name,
            "medicine_name": medicine_data.get("medicine_name"),
            "quantity": quantity,
            "expires_at": expires_at.strftime("%H:%M on %d %b %Y"),
            "message": f"Reserved! Please pick up within {self.RESERVATION_EXPIRY_HOURS} hour(s).",
        }

    # -----------------------------------------------------------
    # GET PATIENT RESERVATIONS (with expiry check)
    # -----------------------------------------------------------
    def get_patient_reservations(self, patient_id: str) -> List[Dict[str, Any]]:
        """
        Get all active reservations for a patient.
        Also expires any reservations past their expiry time.
        """
        # First, expire old reservations
        self._expire_old_reservations()

        # Get active reservations for patient
        docs = (
            self.db.collection("medicine_reservations")
            .where("patient_id", "==", patient_id)
            .where("status", "==", "reserved")
            .stream()
        )

        reservations = []
        for doc in docs:
            data = doc.to_dict()
            data["id"] = doc.id
            reservations.append(data)

        return reservations

    # -----------------------------------------------------------
    # CANCEL RESERVATION
    # -----------------------------------------------------------
    def cancel_reservation(self, reservation_id: str) -> Dict[str, Any]:
        """
        Cancel a reservation and restore inventory.
        """
        ref = self.db.collection("medicine_reservations").document(reservation_id)
        doc = ref.get()

        if not doc.exists:
            return {"success": False, "reason": "Reservation not found."}

        data = doc.to_dict()
        if data.get("status") != "reserved":
            return {"success": False, "reason": "Reservation is not active."}

        # Restore inventory
        self._restore_inventory(
            data.get("hospital_id"),
            data.get("medicine_id"),
            data.get("quantity", 1)
        )

        # Update status
        ref.update({"status": "cancelled"})

        return {
            "success": True,
            "message": "Reservation cancelled. Medicine added back to inventory."
        }

    # -----------------------------------------------------------
    # MARK AS PICKED UP
    # -----------------------------------------------------------
    def mark_picked_up(self, reservation_id: str) -> Dict[str, Any]:
        """
        Mark reservation as picked up.
        """
        ref = self.db.collection("medicine_reservations").document(reservation_id)
        doc = ref.get()

        if not doc.exists:
            return {"success": False, "reason": "Reservation not found."}

        data = doc.to_dict()
        if data.get("status") != "reserved":
            return {"success": False, "reason": "Reservation is not active."}

        ref.update({
            "status": "picked_up",
            "picked_up_at": datetime.utcnow().isoformat()
        })

        return {"success": True, "message": "Medicine picked up successfully!"}

    # -----------------------------------------------------------
    # INTERNAL: Expire old reservations
    # -----------------------------------------------------------
    def _expire_old_reservations(self):
        """
        Find and expire all reservations past their expiry time.
        Restores inventory for each expired reservation.
        """
        now = datetime.utcnow()

        # Get all "reserved" status reservations
        docs = (
            self.db.collection("medicine_reservations")
            .where("status", "==", "reserved")
            .stream()
        )

        for doc in docs:
            data = doc.to_dict()
            expires_at_str = data.get("expires_at")

            if not expires_at_str:
                continue

            try:
                expires_at = datetime.fromisoformat(expires_at_str)
            except ValueError:
                continue

            if now > expires_at:
                # Expired - restore inventory
                self._restore_inventory(
                    data.get("hospital_id"),
                    data.get("medicine_id"),
                    data.get("quantity", 1)
                )

                # Update status
                doc.reference.update({"status": "expired"})

    # -----------------------------------------------------------
    # INTERNAL: Restore inventory
    # -----------------------------------------------------------
    def _restore_inventory(self, hospital_id: str, medicine_id: str, quantity: int):
        """
        Add quantity back to hospital's medicine inventory.
        """
        if not hospital_id or not medicine_id:
            return

        hosp_ref = self.db.collection("hospitals").document(hospital_id)
        hosp_doc = hosp_ref.get()

        if not hosp_doc.exists:
            return

        hospital = hosp_doc.to_dict()
        inventory = hospital.get("medicine_inventory", [])

        for med in inventory:
            if med.get("medicine_id") == medicine_id:
                med["stock_count"] = med.get("stock_count", 0) + quantity
                break

        hosp_ref.update({"medicine_inventory": inventory})

    # -----------------------------------------------------------
    # INTERNAL: Get hospitals by location
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

    # -----------------------------------------------------------
    # INTERNAL: Match medicine to illness using LLM
    # -----------------------------------------------------------
    def _medicine_matches_illness(self, medicine: Dict[str, Any], illness: str) -> bool:
        """
        Use LLM to semantically match illness to medicine's treats list.
        """
        treats = medicine.get("treats", [])
        if not treats:
            return False

        # First try simple keyword match for efficiency
        illness_lower = illness.lower()
        for treat in treats:
            if treat.lower() in illness_lower or illness_lower in treat.lower():
                return True

        # If no direct match, use LLM for semantic matching
        sys = SystemMessage(content="""
You are a medical matching assistant.
Decide if the patient's illness/symptoms match what the medicine treats.
Be permissive for synonyms (e.g., "headache" matches "head pain", "fever" matches "high temperature").
Return STRICT JSON: { "match": true | false }
ONLY return JSON — no explanation.
""")

        user = HumanMessage(content=f"""
Patient illness: {illness}
Medicine treats: {treats}
""")

        try:
            res = self.llm.invoke([sys, user])
            raw = res.content.strip()

            # Extract JSON
            start = raw.find("{")
            end = raw.rfind("}") + 1
            if start != -1 and end > start:
                data = json.loads(raw[start:end])
                return bool(data.get("match", False))

            # Fallback: check for "true" in response
            return "true" in raw.lower()

        except Exception:
            return False
