from typing import Any

from providers.gmail import Gmail


class GmailService:
    """
    Service layer for Gmail operations.
    """

    def __init__(self) -> None:

        self.gmail = Gmail()

    def send_email(
        self,
        recipient: str,
        subject: str,
        body: str,
        resume_path: str,
    ) -> dict[str, Any] | None:
        """
        Send email using Gmail Provider.

        Returns:
            {
                "message_id": "...",
                "thread_id": "..."
            }

        Returns None if sending fails.
        """
        # print('i am adarsh')
        # print(resume_path)
        try:

            return self.gmail.send_email(
                recipient=recipient,
                subject=subject,
                body=body,
                resume_path=resume_path,
            )

        except Exception as e:

            print(f"Gmail Service Error : {e}")

            return None
        
    # * handling follow up workflow 
    
    # check client reply 
    
    def check_reply(
        self,
        thread_id: str,
    ) -> dict[str, Any] | None:
        """
        Check whether the client has replied
        to an existing Gmail thread.
        """
        
        try:

            return self.gmail.check_reply(thread_id)

        except Exception as e:

            print(f"Gmail reply check failed: {e}")

            return None


    # Send Follow-up Email
    
    def send_followup(
        self,
        recipient: str,
        subject: str,
        body: str,
        thread_id: str,
        rfc_message_id:str
    ) -> dict[str, Any] | None:
        """
        Send a follow-up email in the
        existing Gmail thread.
        """

        try:

            return self.gmail.send_followup(
                recipient,
                subject,
                body,
                thread_id,
                rfc_message_id
            )

        except Exception as e:

            print(f"Follow-up email failed: {e}")

            return None