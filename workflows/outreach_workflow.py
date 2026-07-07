from database.db import get_db
from database.repository import LeadRepository

from services.llm_service import LlmService
from services.resume_selector import ResumeSelector


class OutreachWorkflow:

    def __init__(self) -> None:

        self.db = get_db()

        self.repository = LeadRepository(self.db)

        self.resume_selector = ResumeSelector()

        self.llm_service = LlmService()

    def run(self) -> list[dict]:
        
        """
        Generate personalized outreach emails
        for every enriched lead.

        Returns:
            List of generated email payloads.
        """

        generated_emails = []

        # Get all outreach-ready leads
        leads = self.repository.get_pending_outreach()

        if not leads:
            print("No leads available for outreach.")
            return []

        for lead in leads:

            # ---------------------------------------------------------
            # Step 1 : Select best resume
            # ---------------------------------------------------------

            resume = self.resume_selector.select_best_resume(
                lead.description
            )

            print(
                f"[Resume] {lead.company} -> "
                f"{resume['resume_name']} "
                f"(Score : {resume['score']})"
            )

            # ---------------------------------------------------------
            # Step 2 : Prepare payload for LLM
            # ---------------------------------------------------------

            payload = {
                "company": lead.company,
                "job_title": lead.job_title,
                "description": lead.description,
                "resume_name": resume["resume_name"],
            }

            # ---------------------------------------------------------
            # Step 3 : Generate email
            # ---------------------------------------------------------

            email_content = self.llm_service.email_generator(
                payload
            )

            if email_content is None:
                print(
                    f"Email generation failed for "
                    f"{lead.company}"
                )
                continue

            # ---------------------------------------------------------
            # Step 4 : Prepare Gmail payload
            # ---------------------------------------------------------

            generated_emails.append(
                {
                    "lead_id": lead.id,
                    "recipient": lead.email,
                    "subject": email_content["subject"],
                    "body": email_content["email_body"],
                    "resume": resume,
                }
            )

        return generated_emails




workflow = OutreachWorkflow()

generated_emails = workflow.run()

for email in generated_emails:

        print("=" * 100)

        print("To       :", email["recipient"])

        print("Subject  :", email["subject"])

        print("Resume   :", email["resume"]["resume_name"])

        print("Path     :", email["resume"]["resume_path"])

        print("Score    :", email["resume"]["score"])

        print("-" * 100)

        print(email["body"])

        print("=" * 100)