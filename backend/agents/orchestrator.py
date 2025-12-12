# agents/orchestrator.py
import uuid
import json
import re
from typing import Dict, Any, Optional

from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage

from config import OLLAMA_MODEL, OLLAMA_BASE_URL
from db.firebase_client import get_db

from agents.appointment_scheduler import AppointmentSchedulerAgent
from agents.scheme_matcher import SchemeMatcherAgent
from agents.pharmacy_agent import PharmacyAgent
from agents.triage_agent import TriageAgent
from agents.tool_registry import ToolRegistry


SESSIONS: Dict[str, Dict[str, Any]] = {}


class OrchestratorAgent:
    def __init__(self):
        self.llm = ChatOllama(
            model=OLLAMA_MODEL,
            base_url=OLLAMA_BASE_URL,
            temperature=0.0,
        )

        self.db = get_db()
        self.tools = ToolRegistry()
        self.tools.register("book_appointment", AppointmentSchedulerAgent(self.llm, self.db))
        self.tools.register("scheme_matcher", SchemeMatcherAgent(self.llm, self.db))
        self.tools.register("pharmacy", PharmacyAgent(self.llm, self.db))
        self.tools.register("triage", TriageAgent(self.llm, self.db))

        # Emergency keywords for quick detection
        self.EMERGENCY_KEYWORDS = [
            "emergency", "urgent", "critical", "ambulance", "accident",
            "heart attack", "stroke", "bleeding", "unconscious", "dying",
            "help", "911", "sos", "breathing", "chest pain", "severe"
        ]

        # store disease history only when needed
        self._current_disease_history: Optional[list] = None

        # regex patterns for explicit disease extraction
        self._scheme_for_regex = re.compile(
            r"(?:schemes?|scheme|search schemes|find schemes)\s*(?:for|about|related to)?\s*(?P<disease>[a-zA-Z0-9 \-\']{2,60})",
            flags=re.IGNORECASE,
        )

        self._simple_for_regex = re.compile(
            r"for\s+(?P<disease>[a-zA-Z0-9 \-\']{2,60})",
            flags=re.IGNORECASE
        )

        # stopwords that should NEVER be interpreted as diseases
        self.STOPWORDS = {
            "me", "my", "history", "disease", "diseases",
            "profile", "myself", "condition", "records"
        }

    # -----------------------------------------------------------
    # MAIN ENTRY
    # -----------------------------------------------------------
    def handle_request(self, user_id: str, role: str, message: str, session_id=None):
        if not session_id or session_id not in SESSIONS:
            session_id = str(uuid.uuid4())
            SESSIONS[session_id] = {"context": {}, "active_tool": None}

        state = SESSIONS[session_id]
        context = state["context"]
        active_tool = state["active_tool"]

        # doctors cannot chat
        if role == "doctor":
            return self._respond(session_id, "Doctors must use the dashboard.", None, None)

        # inject location from user profile
        user_ref = self.db.collection("users").document(user_id).get()
        if user_ref.exists:
            context["location"] = user_ref.to_dict().get("location")

        low = (message or "").lower()

        # -----------------------------------------------------------
        # 0. EMERGENCY DETECTION (highest priority)
        # -----------------------------------------------------------
        if self._is_emergency(low):
            agent = self.tools.get("triage")
            location = context.get("location")

            result = agent.handle_emergency(user_id, location)

            if result.get("success"):
                return self._format_emergency_response(session_id, result)
            else:
                return self._respond(
                    session_id,
                    f"⚠️ {result.get('reason', 'Unable to dispatch emergency services.')}",
                    None,
                    None
                )

        # -----------------------------------------------------------
        # 1. EXPLICIT: "scheme for cancer" → extract disease directly
        # -----------------------------------------------------------
        explicit_disease = self._extract_explicit_disease(message)
        if explicit_disease:
            self._current_disease_history = None
            agent = self.tools.get("scheme_matcher")
            results = agent.find_by_disease(explicit_disease)

            if not results:
                return self._respond(
                    session_id,
                    f"❌ No matching government schemes found for '{explicit_disease}'.",
                    None,
                    None
                )

            return self._format_schemes_response(session_id, results)

        # -----------------------------------------------------------
        # 2. BUTTON FLOW: "use my history" → show history then schemes
        # -----------------------------------------------------------
        if any(k in low for k in [
            "use my history", "use my disease history", "check from history",
            "check history", "use my diseases"
        ]):
            agent = self.tools.get("scheme_matcher")

            # Load and store patient history
            disease_history = user_ref.to_dict().get("disease_history", []) if user_ref.exists else []
            self._current_disease_history = disease_history

            results = agent.find_by_patient(user_id)

            if not results:
                return self._respond(
                    session_id,
                    "❌ No matching government schemes found based on your disease history.",
                    None,
                    None
                )

            return self._format_schemes_response(session_id, results)

        # -----------------------------------------------------------
        # 3. CONTINUE APPOINTMENT FLOW
        # -----------------------------------------------------------
        if active_tool == "book_appointment":
            tool = self.tools.get("book_appointment")

            extracted = self._extract_booking_fields(message)
            context.update({k: v for k, v in extracted.items() if v})

            result = tool.run(user_id, context)

            if result.get("need_more_info"):
                return self._respond(session_id, result["reason"], "book_appointment", None)

            if result.get("success"):
                state["active_tool"] = None
                return self._respond(
                    session_id, self._format_booking(result), None, result
                )

            return self._respond(session_id, "Booking failed.", None, None)

        # -----------------------------------------------------------
        # 4. LLM PLANNER (fallback decision logic)
        # -----------------------------------------------------------
        decision = self._decide_tool(role, message)
        tool_name = decision.get("tool")
        args = decision.get("arguments", {}) or {}

        # fallback prompts
        if tool_name is None:
            if any(x in low for x in ["book", "appointment", "doctor", "visit"]):
                return self._respond(
                    session_id,
                    "Tell me your symptoms and preferred time.",
                    None,
                    None
                )

            if any(x in low for x in ["scheme", "fund", "grant", "benefit", "government"]):
                return self._respond(
                    session_id,
                    "Do you want me to check schemes using your disease history, or do you want to specify a disease?",
                    None,
                    None
                )

            if any(x in low for x in ["medicine", "pharmacy", "drug", "tablet", "pill", "medication"]):
                return self._respond(
                    session_id,
                    "Tell me what illness or symptom you need medicine for.",
                    None,
                    None
                )

            return self._respond(session_id, self._unsupported_capability_message(), None, None)

        # -----------------------------------------------------------
        # 5. SCHEME MATCHER via planner
        # -----------------------------------------------------------
        if tool_name == "scheme_matcher":
            agent = self.tools.get("scheme_matcher")
            disease = args.get("disease")

            if disease:
                # user-specified disease → do NOT show history
                self._current_disease_history = None
                results = agent.find_by_disease(disease)
            else:
                # no explicit disease → use history
                disease_history = user_ref.to_dict().get("disease_history", [])
                self._current_disease_history = disease_history
                results = agent.find_by_patient(user_id)

            if not results:
                return self._respond(
                    session_id,
                    "❌ No matching government schemes found for your condition.",
                    None,
                    None
                )

            return self._format_schemes_response(session_id, results)

        # -----------------------------------------------------------
        # 6. APPOINTMENT TOOL via planner
        # -----------------------------------------------------------
        if tool_name == "book_appointment":
            state["context"] = args
            state["active_tool"] = "book_appointment"

            if "location" not in state["context"]:
                state["context"]["location"] = context.get("location")

            tool = self.tools.get("book_appointment")
            result = tool.run(user_id, state["context"])

            if result.get("need_more_info"):
                return self._respond(
                    session_id, result["reason"], "book_appointment", None
                )

            if result.get("success"):
                state["active_tool"] = None
                return self._respond(
                    session_id, self._format_booking(result), None, result
                )

            return self._respond(session_id, "Booking failed.", None, None)

        # -----------------------------------------------------------
        # 7. PHARMACY TOOL via planner
        # -----------------------------------------------------------
        if tool_name == "pharmacy":
            agent = self.tools.get("pharmacy")
            illness = args.get("illness") or args.get("symptoms")
            medicine_name = args.get("medicine_name")
            location = context.get("location")

            # If user specified a medicine name, auto-reserve it
            if medicine_name:
                result = agent.auto_reserve_medicine(
                    patient_id=user_id,
                    medicine_name=medicine_name,
                    location=location,
                    quantity=1
                )

                if result.get("success"):
                    return self._format_reservation_response(session_id, result)
                else:
                    return self._respond(
                        session_id,
                        result.get("reason", "Could not reserve medicine."),
                        None,
                        None
                    )

            # If user specified illness/symptoms, search for medicines
            if illness:
                # Check if illness looks like a medicine name (e.g., "paracetamol", "dolo")
                if self._looks_like_medicine_name(illness):
                    result = agent.auto_reserve_medicine(
                        patient_id=user_id,
                        medicine_name=illness,
                        location=location,
                        quantity=1
                    )

                    if result.get("success"):
                        return self._format_reservation_response(session_id, result)
                    # If failed, fall through to search

                # Search for medicines matching the illness
                result = agent.search_medicine(illness, location)

                if not result.get("success"):
                    return self._respond(
                        session_id,
                        result.get("reason", "No medicines found."),
                        None,
                        None
                    )

                return self._format_pharmacy_response(session_id, result)

            # No illness or medicine specified
            return self._respond(
                session_id,
                "What illness or symptoms do you need medicine for? Or tell me the medicine name you need.",
                None,
                None
            )

        return self._respond(session_id, "Invalid tool request.", None, None)

    # -----------------------------------------------------------
    # EXPLICIT DISEASE EXTRACTOR — FIXED WITH STOPWORDS
    # -----------------------------------------------------------
    def _extract_explicit_disease(self, message: str) -> Optional[str]:
        if not message:
            return None

        # 1. scheme_for_regex
        m = self._scheme_for_regex.search(message)
        if m and m.group("disease"):
            d = m.group("disease").strip(" .?,;!")
            if d.lower() in self.STOPWORDS:
                return None
            return d.lower()

        # 2. simple "for X" if "scheme" present
        if "scheme" in message.lower() or "schemes" in message.lower():
            m2 = self._simple_for_regex.search(message)
            if m2 and m2.group("disease"):
                d = m2.group("disease").strip(" .?,;!")
                if d.lower() in self.STOPWORDS:
                    return None
                return d.lower()

        # 3. fallback
        tokens = message.lower().split()
        if "scheme" in tokens and "for" in tokens:
            try:
                idx = tokens.index("for")
                d = " ".join(tokens[idx + 1:])
                d = d.strip(" .?,;!")
                if d.lower() in self.STOPWORDS:
                    return None
                return d
            except:
                return None

        return None

    # -----------------------------------------------------------
    # OUTPUT FORMATTING
    # -----------------------------------------------------------
    def _format_schemes_response(self, session_id, schemes):
        text = ""

        if self._current_disease_history:
            text += "🩺 Your Disease History:\n"
            for d in self._current_disease_history:
                text += f"- {d}\n"
            text += "\n"

        text += "✅ Matching Government Schemes:\n\n"

        for s in schemes:
            text += (
                f"🏷 {s.get('scheme_name')}\n"
                f"🦠 For: {s.get('disease')}\n"
                f"💰 Amount: ₹{s.get('amount')}\n"
                f"🔗 Apply: {s.get('apply_url')}\n\n"
            )

        return self._respond(session_id, text, "scheme_matcher", {"schemes": schemes})

    # -----------------------------------------------------------
    # LLM PLANNER
    # -----------------------------------------------------------
    def _decide_tool(self, role: str, message: str) -> Dict[str, Any]:
        sys = SystemMessage(content="""
You are a strict hospital intent classifier.

TOOLS:
- "book_appointment" for doctor visits, seeing a doctor, booking consultation.
- "scheme_matcher" for government health schemes, grants, benefits.
- "pharmacy" for medicine requests, pharmacy needs, buying/getting drugs/tablets.

IMPORTANT FOR PHARMACY:
- If user asks for a SPECIFIC medicine by name (paracetamol, dolo, ibuprofen, etc), extract it as "medicine_name"
- If user describes symptoms/illness, extract as "illness"

Return JSON only:
{
 "tool": "book_appointment" | "scheme_matcher" | "pharmacy" | null,
 "arguments": {
    "symptoms": string | null,
    "preferred_time": string | null,
    "disease": string | null,
    "illness": string | null,
    "medicine_name": string | null
 }
}
""")

        try:
            res = self.llm.invoke([sys, HumanMessage(content=message)])
            raw = res.content.strip()
            start = raw.find("{")
            end = raw.rfind("}") + 1
            payload = json.loads(raw[start:end])
        except:
            return {"tool": None, "arguments": {}}

        tool = payload.get("tool")
        if tool not in ["book_appointment", "scheme_matcher", "pharmacy", None]:
            tool = None

        args = payload.get("arguments", {}) or {}
        return {"tool": tool, "arguments": args}

    # -----------------------------------------------------------
    # Booking field extractor
    # -----------------------------------------------------------
    def _extract_booking_fields(self, message: str) -> Dict[str, Any]:
        prompt = f"""
Extract ONLY JSON fields:
- symptoms
- preferred_time

Message: {message}

Return JSON only.
"""
        try:
            res = self.llm.invoke([HumanMessage(content=prompt)])
            raw = res.content.strip()
            start = raw.find("{")
            end = raw.rfind("}") + 1
            data = json.loads(raw[start:end])
        except:
            return {}

        cleaned = {}
        for k, v in data.items():
            if isinstance(v, str):
                cleaned[k] = v.strip()

        return cleaned

    # -----------------------------------------------------------
    # Response wrapper
    # -----------------------------------------------------------
    def _respond(self, session_id, message, agent, data):
        if session_id is None:
            session_id = str(uuid.uuid4())
        return {
            "session_id": session_id,
            "message": message,
            "next_action": "responded",
            "selected_agent": agent,
            "data": data,
        }

    def _unsupported_capability_message(self):
        return (
            "Right now I can help with:\n"
            "✅ Booking doctor appointments\n"
            "✅ Finding government health schemes\n"
            "✅ Searching for medicines\n\n"
            "I cannot yet:\n"
            "- Analyze lab reports\n"
            "- Give prescriptions\n"
            "- Access detailed medical history\n"
            "- Handle billing"
        )

    def _format_booking(self, r):
        return (
            "✅ Appointment Booked Successfully!\n\n"
            f"🏥 Hospital: {r['hospital_name']}\n"
            f"👨‍⚕️ Doctor: {r['doctor_name']}\n"
            f"🩺 Department: {r['department']}\n"
            f"⏰ Time: {r['time']}\n"
            f"🆔 Booking ID: {r['appointment_id']}"
        )

    def _format_pharmacy_response(self, session_id, result):
        """Format medicine search results for display."""
        medicines = result.get("medicines", [])
        location = result.get("location", "your area")
        illness = result.get("illness", "")

        text = f"💊 Medicines available for '{illness}' in {location}:\n\n"

        # Group by hospital
        by_hospital = {}
        for med in medicines:
            hosp = med.get("hospital_name", "Unknown")
            if hosp not in by_hospital:
                by_hospital[hosp] = []
            by_hospital[hosp].append(med)

        for hosp_name, meds in by_hospital.items():
            text += f"🏥 **{hosp_name}**\n"
            for med in meds:
                text += (
                    f"  💊 {med['medicine_name']}\n"
                    f"     📦 Stock: {med['stock_count']} | 🏭 {med['manufacturer']}\n"
                )
            text += "\n"

        text += "📝 To get a medicine, just say: 'I want [medicine name]'"

        return self._respond(session_id, text, "pharmacy", {"medicines": medicines})

    def _format_reservation_response(self, session_id, result):
        """Format successful medicine reservation for display."""
        text = (
            "✅ Medicine Reserved Successfully!\n\n"
            f"💊 Medicine: {result.get('medicine_name')}\n"
            f"🏥 Hospital: {result.get('hospital_name')}\n"
            f"📦 Quantity: {result.get('quantity')}\n"
            f"⏰ Pick up by: {result.get('expires_at')}\n"
            f"🆔 Reservation ID: {result.get('reservation_id')}\n\n"
            "⚠️ Note: If not picked up within 1 hour, the reservation will be cancelled automatically."
        )
        return self._respond(session_id, text, "pharmacy", result)

    def _looks_like_medicine_name(self, text: str) -> bool:
        """
        Quick check if text looks like a medicine name rather than an illness.
        """
        if not text:
            return False

        text_lower = text.lower().strip()

        # Common medicine names/keywords
        MEDICINE_KEYWORDS = [
            "paracetamol", "dolo", "ibuprofen", "cetirizine",
            "azithromycin", "amoxicillin", "metformin", "omeprazole",
            "pantoprazole", "loperamide", "montelukast", "insulin",
            "morphine", "vitamin", "cough syrup", "benadryl",
            "antacid", "digene", "ors", "tablet", "capsule", "syrup",
            "mg", "500mg", "650", "400mg", "10mg", "20mg", "40mg"
        ]

        for keyword in MEDICINE_KEYWORDS:
            if keyword in text_lower:
                return True

        return False

    def _is_emergency(self, text: str) -> bool:
        """
        Check if message contains emergency keywords.
        """
        if not text:
            return False

        text_lower = text.lower()

        for keyword in self.EMERGENCY_KEYWORDS:
            if keyword in text_lower:
                return True

        return False

    def _format_emergency_response(self, session_id, result):
        """Format emergency dispatch success response."""
        text = (
            "🚨 **EMERGENCY SERVICES DISPATCHED!**\n\n"
            f"🏥 Hospital: {result.get('hospital_name')}\n"
            f"🚑 Ambulance: Dispatched and on the way!\n"
            f"🛏️ Bed: Booked and ready\n"
            f"🆔 Dispatch ID: {result.get('dispatch_id')}\n\n"
            "📍 Please stay calm. Help is on the way.\n"
            "📞 If critical, also call local emergency services."
        )
        return self._respond(session_id, text, "triage", result)
