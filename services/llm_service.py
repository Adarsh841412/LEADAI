import os
from typing import Any

from langchain_groq import ChatGroq

from config.settings import XAI_API_KEY
from prompts.pitch_prompt import prompt, parser


os.environ["GROQ_API_KEY"] = XAI_API_KEY.strip()
print(XAI_API_KEY)

class LlmService:
    """
    Generates outreach emails.
    """

    def __init__(self) -> None:

        self.model = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0.7,
            max_tokens=600,
            api_key=XAI_API_KEY,
        )

        self.chain = prompt | self.model | parser

    def email_generator(
        self,
        lead: dict[str, Any],
    ) -> dict[str, str] | None:
        """
        Generate an outreach email for a lead.

        Returns:
            {
                "subject": "...",
                "email_body": "..."
            }
        """

        company = lead.get("company", "")
        job_title = lead.get("job_title", "")
        description = lead.get("description", "")

        if not description:
            return None

        try:

            response = self.chain.invoke(
                {
                    "company": company,
                    "job_title": job_title,
                    "description": description,
                }
            )

            return {
                "subject": response.subject,
                "email_body": response.email_message,
            }

        except Exception as e:

            print(f"LLM Error: {e}")

            return None


# llm = LlmService()

# lead = {
#         "company": "Stripe",
#         "job_title": "Python Backend Engineer",
#         "description": """
#         Looking for an experienced Python developer with FastAPI,
#         PostgreSQL, Docker and AWS experience.
#         """,
#     }

# email = llm.email_generator(lead)

# print(email)