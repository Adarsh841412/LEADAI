# from database.repository import LeadRepository
# from services.gmail_service import GmailService
# from services.llm_service import LlmService
# from database.db import get_db
# from prompts.followup_prompt import prompt,parser 

# class FollowUpWorkflow:
    
#     def __init__(self):
#         self.db = get_db() 
#         self.repository = LeadRepository(self.db)
#         self.gmail_service = GmailService()
#         self.llm_service = LlmService(prompt,parser)    
        
#     def run(self):
#         """
#         Check whether clients have replied to outreach emails.

#         If a reply is received:
#             - Mark lead as replied.

#         Otherwise:
#             - Lead is eligible for follow-up.
#         """

#         # ---------------------------------------------------------
#         # Step 1 : Fetch eligible leads
#         # ---------------------------------------------------------

#         followup_leads = self.repository.get_pending_followups()

#         if not followup_leads:
#             print("No leads available for follow-up.")
#             return

#         checked_leads = 0
#         replied_leads = 0
#         pending_followups = 0

#         # ---------------------------------------------------------
#         # Step 2 : Process each lead
#         # ---------------------------------------------------------

#         for lead in followup_leads:

#             checked_leads += 1

#             print(f"\nChecking {lead.company}")

#             reply = self.gmail_service.check_reply(
#                 lead.thread_id
#             )

#             if reply is None:

#                 print("Unable to check Gmail thread.")
#                 continue

#             if reply["replied"]:

#                 replied_leads += 1

#                 self.repository.mark_as_replied(
#                     lead.id
#                 )

#                 print("✓ Reply received")

#                 continue
            
#             else :
#                 pending_followups += 1
#                 print("→ Generating follow-up")
                
           
#                 # 1. Generate follow-up email
                
#                 first_message = reply["messages"][0]

#                 previous_email = first_message["snippet"]

#                 previous_subject = ""

#                 for header in first_message["payload"]["headers"]:

#                     if header["name"] == "Subject":

#                         previous_subject = header["value"]

#                         break


#                 payload = {
#                     "company": lead.company,
#                     "job_title": lead.job_title,
#                     "description": lead.description,
#                     "previous_subject": previous_subject,
#                     "previous_email": previous_email,
#                 }

#                 output = self.llm_service.email_generator(payload)
#                 if output is None:
#                     print(f"Failed to generate follow-up for {lead.company}")
#                     continue
                
            
#                 # 2. Send follow-up email
                  
#                 response = self.gmail_service.send_followup(
#                         recipient=lead.email,
#                         subject=output["subject"],
#                         body=output["email_body"],
#                         thread_id=lead.thread_id,)
                                                     
                
#                 if response in None :
#                     print(f'failed to send follow up email to {lead.company}')
#                     continue 
                
#                 print(f"✓ Follow-up sent to {lead.company}")

                    
                
#                 # 3. Update follow-up count
                
#                 self.repository.update_after_followup(
#                         lead_id=lead.id,
#                         thread_id=response["thread_id"],
#                         message_id=response["message_id"],
#                     )

#                 print(f"✓ Database updated for {lead.company}")
                            
                                
                
                
                

#         # ---------------------------------------------------------
#         # Step 3 : Summary
#         # ---------------------------------------------------------

#         # print("\n" + "=" * 60)
#         # print("        Follow-up Check Complete")
#         # print("=" * 60)

#         # print(f"Checked Leads : {checked_leads}")
#         # print(f"Client Replied: {replied_leads}")
#         # print(f"Need Follow-up: {pending_followups}")

#         # print("=" * 60)
    
    
    
# c1 = FollowUpWorkflow() 
# c1.run() 
        
         
         
         
from database.db import get_db
from database.repository import LeadRepository

from services.gmail_service import GmailService
from services.llm_service import LlmService

from prompts.followup_prompt import prompt, parser


class FollowUpWorkflow:

    def __init__(self) -> None:

        self.db = get_db()

        self.repository = LeadRepository(self.db)

        self.gmail_service = GmailService()

        self.llm_service = LlmService(prompt, parser)

    def run(self) -> None:
        """
        Check whether clients have replied to outreach emails.

        If replied:
            - Mark as replied.

        Otherwise:
            - Generate follow-up.
            - Send follow-up.
            - Update database.
        """

        # ---------------------------------------------------------
        # Step 1 : Fetch eligible leads
        # ---------------------------------------------------------

        followup_leads = self.repository.get_pending_followups()

        if not followup_leads:
            print("No leads available for follow-up.")
            return

        checked_leads = 0
        replied_leads = 0
        followups_sent = 0

        # ---------------------------------------------------------
        # Step 2 : Process each lead
        # ---------------------------------------------------------

        for lead in followup_leads:

            checked_leads += 1

            print(f"\nChecking {lead.company}")

            reply = self.gmail_service.check_reply(
                lead.thread_id
            )

            if reply is None:

                print("Unable to check Gmail thread.")

                continue

            # -----------------------------------------------------
            # Client Replied
            # -----------------------------------------------------

            if reply["replied"]:

                replied_leads += 1

<<<<<<< HEAD
                self.repository.mark_as_replied(
                    lead.id
                )
=======
                # self.repository.mark_as_replied(
                #     lead.id
                # )
>>>>>>> master

                print("✓ Reply received")

                continue

            # -----------------------------------------------------
            # Generate Follow-up
            # -----------------------------------------------------

            print("→ Generating follow-up")

            first_message = reply["messages"][0]

            previous_email = first_message["snippet"]

            previous_subject = ""

            for header in first_message["payload"]["headers"]:

                if header["name"] == "Subject":

                    previous_subject = header["value"]

<<<<<<< HEAD
                    break
=======
                    # break
>>>>>>> master

            payload = {
                "company": lead.company,
                "job_title": lead.job_title,
                "description": lead.description,
                "previous_subject": previous_subject,
                "previous_email": previous_email,
            }
       
            followup_email = self.llm_service.email_generator(
                payload
            )

            if followup_email is None:

                print(
                    f"Failed to generate follow-up for {lead.company}"
                )

                continue

            # -----------------------------------------------------
            # Send Follow-up
            # -----------------------------------------------------

            response = self.gmail_service.send_followup(
                recipient='adarshdubeyv@gmail.com',
                subject=previous_subject,
                body=followup_email["email_body"],
                thread_id=lead.thread_id,
                rfc_message_id = lead.rfc_message_id
            )

            if response is None:

                print(
                    f"Failed to send follow-up email to {lead.company}"
                )

                continue

            print(f"✓ Follow-up sent to {lead.company}")

            # -----------------------------------------------------
            # Update Database
            # -----------------------------------------------------

            updated = self.repository.update_after_followup(
                lead_id=lead.id,
                thread_id=response["thread_id"],
                message_id=response["message_id"],
                rfc_message_id=response['rfc_message_id']
            )

            if updated:

                followups_sent += 1

                print(
                    f"✓ Database updated for {lead.company}"
                )

            else:

                print(
                    f"Failed to update database for {lead.company}"
                )
            break 
        # ---------------------------------------------------------
        # Step 3 : Summary
        # ---------------------------------------------------------

        print("\n" + "=" * 60)
        print("        Follow-up Workflow Complete")
        print("=" * 60)

        print(f"Checked Leads   : {checked_leads}")
        print(f"Client Replied  : {replied_leads}")
        print(f"Follow-ups Sent : {followups_sent}")

        print("=" * 60)

<<<<<<< HEAD


=======
>>>>>>> master
