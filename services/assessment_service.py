from datetime import datetime, date
from typing import Optional
import re


class AssessmentService:

    DATE_FORMATS = (
        "%A, %d %B %Y",   # Friday, 25 July 2026
        "%d %B %Y",       # 25 July 2026
        "%d/%m/%Y",       # 25/07/2026
        "%Y-%m-%d",       # 2026-07-25
        "%B %d, %Y",      # July 25, 2026
    )

    def validate_assessment(
        self,
        assessment_link: Optional[str],
        assessment_deadline: Optional[str],
    ) -> Optional[dict]:

        # Normalize link
        if assessment_link:
            assessment_link = assessment_link.strip()
        else:
            assessment_link = "assessment link not available"

        # No deadline received
        if not assessment_deadline:
            return {
                "assessment_link": assessment_link,
                "assessment_deadline": None,
            }

        # Normalize dash characters
        assessment_deadline = (
            assessment_deadline.replace("–", "-")
                               .replace("—", "-")
                               .replace("−", "-")
                               .strip()
        )

        # If LLM returns a range like:
        # "25 July 2026 - 26 July 2026"
        if "-" in assessment_deadline:
            assessment_deadline = re.split(r"\s*-\s*", assessment_deadline)[0]

        # Parse date
        for fmt in self.DATE_FORMATS:
            try:
                parsed_date = datetime.strptime(
                    assessment_deadline,
                    fmt
                ).date()

                return {
                    "assessment_link": assessment_link,
                    "assessment_deadline": parsed_date,
                }

            except ValueError:
                continue

        # Invalid date format
        return None