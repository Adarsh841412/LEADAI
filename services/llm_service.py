import os
from typing import Any
from langchain_groq import ChatGroq
from config.settings import XAI_API_KEY
os.environ["GROQ_API_KEY"] = XAI_API_KEY.strip()
from prompts.question_reply_prompt import (
    prompt as question_prompt,
    parser as question_parser,
)
from prompts.question_reply_prompt import prompt
from langchain_core.output_parsers import StrOutputParser
from prompts.general_reply_prompt import prompt as general_reply_prompt
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

# this one is for conversation workflow 


    def conversation_analyzer(
    self,
    lead: dict[str, Any],
):
        """
        Analyze the latest recruiter message.

        Expected Payload:
        {
            "subject": "...",
            "email": "..."
        }

        Returns:
            Parsed ConversationResponse object.

        Returns None if analysis fails.
        """

        subject = lead.get("subject")
        email = lead.get("email")
       

        if not subject or not email:

            print("Conversation payload is incomplete.")

            return None

        payload = {
            "subject": subject,
            "email": email,
        }

        try:

            response = self.chain.invoke(payload)

            return response

        except Exception as e:

            print(f"Conversation Analyzer Error: {e}")

            return None
        
     
            # * it is for if intent = Question 
    def generate_answer(
        self,
        payload: dict[str, Any],
    ):
        """
        Generate a professional reply to recruiter questions.
        """

        subject = payload.get("subject")
        email = payload.get("email")

        if not subject or not email:

            print("Question payload is incomplete.")

            return None

        chain = (
            question_prompt
            | self.model
            | question_parser
        )

        try:

            response = chain.invoke(
                {
                    "subject": subject,
                    "email": email,
                }
            )

            return response

        except Exception as e:

            print(f"Generate Answer Error: {e}")

            return None    
        
        
    # * this one for intent == Genral_reply
    
    def generate_reply(
        self,
        subject: str,
        email: str,
    ) -> str:
        """
        Generate a professional reply to a recruiter email.
        """

        chain = (
            general_reply_prompt
            | self.model
            | StrOutputParser()
        ) 

        return chain.invoke(
            {
                "subject": subject,
                "email": email,
            }
        )    