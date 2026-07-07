from typing import Any

POSITION_SCORE = {
    "technical recruiter": 100,
    "recruiter": 100,
    "talent acquisition": 95,
    "talent partner": 95,
    "staffing": 90,
    "sourcer": 90,
    "human resources": 85,
    "hr": 85,
    "people partner": 80,
    "people operations": 80,
    "hiring manager": 80,
    "engineering manager": 80,
    "head of talent": 80,
    "head of recruiting": 80,
    "head of hr": 80,
    "head of engineering": 75,
    "team lead": 75,
    "manager": 70,
    "director": 65,
    "head": 60,
    "vice president": 55,
    "vp": 55,
    "chief technology officer": 50,
    "cto": 50,
    "founder": 45,
    "co-founder": 45,
    "chief executive officer": 40,
    "ceo": 40,
    "principal engineer": 35,
    "staff engineer": 35,
    "software engineer": 25,
    "developer": 25,
    "engineer": 20,
    "product manager": 20,
    "customer success": 15,
    "sales": 10,
}

DEPARTMENT_SCORE = {
    "human_resources": 100,
    "recruiting": 100,
    "talent": 95,
    "management": 70,
    "engineering": 50,
    "product": 45,
    "operations": 40,
    "it": 40,
    "sales": 30,
    "marketing": 25,
    "support": 20,
    "finance": 20,
    "legal": 15,
    "other": 10,
}

SENIORITY_SCORE = {
    "owner": 100,
    "partner": 95,
    "executive": 90,
    "vp": 85,
    "director": 80,
    "manager": 70,
    "senior": 60,
    "lead": 55,
    "mid": 40,
    "entry": 20,
    "junior": 15,
    "intern": 5,
}

DEFAULT_SCORE = 10

GENERIC_PREFIXES = {
    "info",
    "support",
    "contact",
    "sales",
    "admin",
    "hello",
    "careers",
    "jobs",
    "hr",
}

_POSITION_KEYWORDS = sorted(
    POSITION_SCORE.items(),
    key=lambda x: len(x[0]),
    reverse=True,
)


class EmailRanker:
    """
    Select the best Hunter contact for outreach.
    """

    @staticmethod
    def _score_position(contact: dict[str, Any]) -> int:
        position = (contact.get("position") or "").lower()
        position_raw = (contact.get("position_raw") or "").lower()

        text = f"{position} {position_raw}"

        for keyword, score in _POSITION_KEYWORDS:
            if keyword in text:
                return score

        return DEFAULT_SCORE

    @staticmethod
    def _score_department(contact: dict[str, Any]) -> int:
        department = (contact.get("department") or "").lower()
        return DEPARTMENT_SCORE.get(department, DEFAULT_SCORE)

    @staticmethod
    def _score_seniority(contact: dict[str, Any]) -> int:
        seniority = (contact.get("seniority") or "").lower()
        return SENIORITY_SCORE.get(seniority, DEFAULT_SCORE)

    @staticmethod
    def _score_confidence(contact: dict[str, Any]) -> int:
        return int(contact.get("confidence", 0))

    @classmethod
    def _total_score(cls, contact: dict[str, Any]) -> int:
        return (
            cls._score_position(contact)
            + cls._score_department(contact)
            + cls._score_seniority(contact)
            + cls._score_confidence(contact)
        )

    # @staticmethod
    # def _is_valid(contact: dict[str, Any]) -> bool:

    #     verification = (
    #         contact.get("verification", {})
    #         .get("status", "")
        
    #     )
     
    #     return verification == "valid"


    @staticmethod
    def _is_generic_email(contact: dict[str, Any]) -> bool:

        email = (contact.get("value") or "")
    

        if "@" not in email:
            return True

        prefix = email.split("@")[0]

        return prefix in GENERIC_PREFIXES

    @classmethod
    def select_best_contact(
        cls,
        contacts: list[dict[str, Any]],
    ) -> dict[str, Any] | None:
   
        if not contacts:
            return None

        best_contact = None
        best_score = -1

        for contact in contacts:
            


            if cls._is_generic_email(contact):
                continue

            score = cls._total_score(contact)
       
            if score > best_score:
                best_score = score
                best_contact = contact
        

        if best_contact is None:
            return None
     
        
        return {
            "email": best_contact.get("value"),
            "first_name": best_contact.get("first_name"),
            "last_name": best_contact.get("last_name"),
            "position": best_contact.get("position"),
            "department": best_contact.get("department"),
            "seniority": best_contact.get("seniority"),
            "linkedin": best_contact.get("linkedin"),
            "score": best_score,
        }
        

