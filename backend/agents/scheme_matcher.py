# agents/scheme_matcher.py
import json
from langchain_core.messages import HumanMessage, SystemMessage


class SchemeMatcherAgent:
    def __init__(self, llm, db):
        self.llm = llm
        self.db = db

    def find_by_patient(self, user_id: str):
        user_ref = self.db.collection("users").document(user_id).get()
        if not user_ref.exists:
            return []

        user = user_ref.to_dict()
        diseases = user.get("disease_history", [])

        if not diseases:
            return []

        scheme_docs = self.db.collection("schemes").stream()
        schemes = [d.to_dict() for d in scheme_docs]

        matched = []
        for scheme in schemes:
            scheme_disease = scheme.get("disease", "").strip()
            if not scheme_disease:
                continue

            if self._llm_judge_match(diseases, scheme_disease):
                matched.append(scheme)

        return matched

    def find_by_disease(self, disease: str):
        # basic sanitize
        if not disease:
            return []

        scheme_docs = self.db.collection("schemes").stream()
        schemes = [d.to_dict() for d in scheme_docs]

        matched = []
        for scheme in schemes:
            scheme_disease = scheme.get("disease")
            if not scheme_disease:
                continue

            if self._llm_judge_match([disease], scheme_disease):
                matched.append(scheme)

        return matched

    def _llm_judge_match(self, patient_diseases, scheme_disease):
        sys = SystemMessage(content="""
You are a medical semantic matcher.

Decide if the given patient disease(s) and the scheme disease/category are the SAME or STRONGLY RELATED.
Be permissive for common synonyms and subtypes (e.g., 'blood cancer' -> 'cancer', 'renal failure' -> 'kidney disease', 'pregnancy' -> 'maternal health').
Return STRICT JSON: { "match": true | false }
ONLY return JSON — no explanation.
""")

        user = HumanMessage(content=f"""
Patient disease list: {patient_diseases}
Scheme disease: {scheme_disease}
""")

        try:
            res = self.llm.invoke([sys, user])
            raw = res.content.strip()
            # try to extract JSON from code fences or stray text
            if "```" in raw:
                raw = raw.split("```")[-2] if raw.count("```") >= 2 else raw.replace("```", "")
            # fallback: pick the first JSON-looking substring
            start = raw.find("{")
            end = raw.rfind("}") + 1
            if start != -1 and end != -1:
                raw_json = raw[start:end]
                data = json.loads(raw_json)
                return bool(data.get("match", False))
            # last resort: check keywords
            lowered = raw.lower()
            if "true" in lowered:
                return True
            return False
        except Exception:
            return False
