from database.repository import LeadRepository
from database.db import get_db
from services.gmail_service import GmailService


class ReplyWorkflow:

    def __init__(self):

        self.db = get_db()
        self.repository = LeadRepository(self.db)
        self.gmail_service = GmailService()

    def run(self):

        pending_leads = self.repository.get_lead_to_check_reply()

        if not pending_leads:

            print("No pending replies to check.")
            return

        checked_leads = 0
        replied_leads = 0

        for lead in pending_leads:

            checked_leads += 1

            print(f"\nChecking {lead.company}")

            reply = self.gmail_service.check_reply(
                lead.thread_id
            )

            if reply is None:

                print("Unable to check Gmail thread.")
                continue

            if reply["replied"]:

                replied_leads += 1

                self.repository.mark_as_replied(
                    lead.id
                )

                print("✓ Reply received")

            else:

                print("No reply yet.")

        print("\n" + "=" * 50)
        print("Reply Workflow Complete")
        print("=" * 50)
        print(f"Checked Leads : {checked_leads}")
        print(f"Replies Found : {replied_leads}")
        print("=" * 50)

