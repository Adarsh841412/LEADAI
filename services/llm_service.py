import os
from typing import Any
from langchain_groq import ChatGroq
from config.settings import XAI_API_KEY
os.environ["GROQ_API_KEY"] = XAI_API_KEY.strip()


class LlmService:
    """
    Generates outreach emails.
    """

    def __init__(self,prompt,parser) -> None:

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
        Generate an follow up email for a lead 

        Returns:
            {
                "subject": "...",
                "email_body": "..."
            }
        """

        company = lead.get("company", "")
        job_title = lead.get("job_title", "")
        description = lead.get("description", "")
        previous_email = lead.get("previous_email")
        previous_subject = lead.get("previous_subject")
        
    
        if not description:
            return None
        
        
        payload = {
            "company": company,
            "job_title": job_title,
            "description": description,
}

        if previous_email:
            payload["previous_email"] = previous_email

        if previous_subject:
            payload["previous_subject"] = previous_subject



        try:
            
            

            response = self.chain.invoke(payload)

    
            return {
                "subject": response.subject,
                "email_body": response.email_message
            }

        except Exception as e:

            print(f"LLM Error: {e}")

            return None

