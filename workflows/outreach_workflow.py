from database.db import get_db
from database.repository import LeadRepository
from services.llm_service import LlmService
from services.resume_selector import ResumeSelector
from services.gmail_service import GmailService
from  prompts.pitch_prompt import parser,prompt 
class OutreachWorkflow:

    def __init__(self) -> None:

        self.db = get_db()

        self.repository = LeadRepository(self.db)

        self.resume_selector = ResumeSelector()

        self.llm_service = LlmService(prompt,parser)

        self.gmail_service = GmailService()

    def run(self) -> list[dict]:
        """
        Generate and send outreach emails.

        Returns:
            List of successfully sent emails.
        """

        sent_emails = []
        
        try : 

            leads = self.repository.get_pending_outreach()
            if not leads:
                print("No leads available for outreach.")
                return []

            for lead in leads:

                # select resume 

                resume = self.resume_selector.select_best_resume(
                    lead.description
                )
                if resume is None:
                    print(f"No resume found for {lead.company}")
                    continue

                print(
                    f"[Resume] {lead.company} -> "
                    f"{resume['resume_name']} "
                    f"(Score : {resume['score']})"
                )

                # geneate email  
                
                payload = {
                    "company": lead.company,
                    "job_title": lead.job_title,
                    "description": lead.description,
                    "resume_name": resume["resume_name"],
                }

                email_content = self.llm_service.email_generator(
                    payload
                )
                if email_content is None:
                    print(
                        f"Failed to generate email for {lead.company}"
                    )
                    continue

                # send email 
                gmail_response = self.gmail_service.send_email(
                    recipient='adarshdubeyv@gmail.com',
                    subject=email_content["subject"],
                    body=email_content["email_body"],
                    resume_path=resume["resume_path"],
                )

                if gmail_response is None:
                    print(
                        f"Failed to send email to {lead.email}"
                    )
                    continue

            
                # Update Database
                
                updated = self.repository.update_after_send(
                    lead_id=lead.id,
                    thread_id=gmail_response["thread_id"],
                    message_id=gmail_response["message_id"],
                    rfc_message_id=gmail_response["rfc_message_id"],
                )

                if not updated:
                    print(f"Failed to update database for lead {lead.id}")
                    continue
                
                
                sent_emails.append(
                    {
                        "lead_id": lead.id,
                        "recipient": lead.email,
                        "company": lead.company,
                        "subject": email_content["subject"],
                        "resume": resume["resume_name"],
                        "thread_id": gmail_response["thread_id"],
                        "message_id": gmail_response["message_id"],
                    }
                )

                print(f"Email sent to {lead.email}")

            return sent_emails
        except Exception as e:
            print("Error happened in OutreachWorkflow:", e)
            return []
        finally :
            self.db.close() 
    
    


