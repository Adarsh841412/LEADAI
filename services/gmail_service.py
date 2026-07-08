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