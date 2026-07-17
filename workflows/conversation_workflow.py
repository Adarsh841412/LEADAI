from database.db import get_db
from database.repository import LeadRepository

from services.gmail_service import GmailService
from services.llm_service import LlmService
from services.meeting_service import MeetingService
from prompts.conversation_prompt import prompt, parser

class ConversationWorkflow:

    def __init__(self):

        self.db = get_db()

        self.repository = LeadRepository(self.db)

        self.gmail_service = GmailService()

        self.llm_service = LlmService(
             prompt,
              parser,
        )

        self.meeting_service = MeetingService()

    def run(self):

        # ---------------------------------------------------------
        # Step 1 : Fetch Pending Conversations
        # ---------------------------------------------------------

        conversation_leads = self.repository.get_pending_conversation()

        if not conversation_leads:

            print("No pending conversations found.")

            return

        checked = 0

        # ---------------------------------------------------------
        # Step 2 : Process Each Lead
        # ---------------------------------------------------------

        for lead in conversation_leads:

            checked += 1

            print(f"\nChecking {lead.company}")

            # -----------------------------------------------------
            # Get Latest Recruiter Email
            # -----------------------------------------------------

            latest_message = self.gmail_service.get_latest_recruiter_message(
                lead.thread_id
            )
            

            if latest_message is None:

                print("Unable to fetch recruiter message.")

                continue

            payload = {
                "subject": latest_message["subject"],
                "email": latest_message["body"],      # Later replace with body
            }
            # print(latest_message['body'])
            # -----------------------------------------------------
            # Analyze Conversation
            # -----------------------------------------------------
        
            analysis = self.llm_service.conversation_analyzer(
                payload
            )
            print(analysis)
            if analysis is None:

                print("Conversation analysis failed.")

                continue

            intent = analysis.intent.strip()

            print(f"Detected Intent : {intent}")

            # =====================================================
            # CASE 1 : MEETING
            # =====================================================

            if intent == "MEETING":

                meeting = self.meeting_service.validate_meeting(
                    meeting_date=analysis.meeting_date,
                    meeting_time=analysis.meeting_time,
                    timezone=analysis.timezone,
                    meeting_link = analysis.meeting_link,
                    meeting_platform = analysis.meeting_platform,
                )
                
                if meeting is None:

                    print("Invalid meeting information.")

                    continue

                print("Meeting validated.")
                print(meeting)

                save = self.repository.save_meeting(
                    lead.id,
                    meeting
                )
                
                print("Meeting saved successfully.")



            # =====================================================
            # CASE 2 : QUESTION
            # =====================================================
            elif intent == "QUESTION":

                print("Recruiter asked a question.")

                answer = self.llm_service.generate_answer(
                    {
                        "subject": latest_message["subject"],
                        "email": latest_message["body"],   # later body
                    }
                )
                print(answer)
                print() 
                print() 
                
                
                if answer is None:

                    continue
                
                response = self.gmail_service.send_followup(

                    recipient='adarshdubeyv@gmail.com',

                    subject=latest_message["subject"],

                    body=answer.email_message,

                    thread_id=lead.thread_id,

                    rfc_message_id=lead.rfc_message_id,
                )

                if response is None:

                    continue
                print(response)

                updated =  self.repository.update_after_conversation(

                    lead_id=lead.id,

                    thread_id=response["thread_id"],

                    message_id=response["message_id"],

                    rfc_message_id=response["rfc_message_id"],
                )

                if updated:
                   print("Question answered.")
                else:
                  print("Failed to update database.")

#             # =====================================================
#             # CASE 3 : ASSESSMENT
#             # =====================================================

#             elif intent == "ASSESSMENT":

#                 print("Assessment detected.")

#                 # TODO
#                 # self.repository.save_assessment(...)

#                 print("Assessment stored.")

#             # =====================================================
#             # CASE 4 : GENERAL_REPLY
#             # =====================================================

            elif intent == "GENERAL_REPLY":

                print("General recruiter reply.")

                reply = self.llm_service.generate_reply(
                            subject=latest_message["subject"],
                            email=latest_message["body"],
                                          )
                print(reply)
                
                response =   self.gmail_service.send_followup(
                    recipient="adarshdubeyv@gmail.com",
                    subject=f"Re: {latest_message["subject"]}",
                    body=reply,
                    thread_id=lead.thread_id,
                    rfc_message_id=lead.rfc_message_id,
                )
                if response is None:

                    continue
                print(response)
                
                
                # # TODO
                updated =  self.repository.update_after_conversation(

                    lead_id=lead.id,

                    thread_id=response["thread_id"],

                    message_id=response["message_id"],

                    rfc_message_id=response["rfc_message_id"],
                )
                
                if updated:
                    print("Conversation updated.")
                else:
                    print("Failed to update database.")

                print("Reply sent.")

#             # =====================================================
#             # CASE 5 : REJECTION
#             # =====================================================

            elif intent == "REJECTION":

                print("Application rejected.")

                # TODO
                self.repository.mark_rejected(
                    lead.id
                )

                print("Lead updated. to reject")

#             # =====================================================
#             # CASE 6 : UNKNOWN
#             # =====================================================

            elif intent == "UNKNOWN":

                print("Unknown conversation.")

                updated = self.repository.mark_manual_review(
                    lead.id
                )

                if updated:
                    print("Marked for manual review.")
                else:
                    print("Failed to mark lead for manual review.")

#         # ---------------------------------------------------------
#         # Step 3 : Summary
#         # ---------------------------------------------------------

#         print("\n" + "=" * 60)
#         print("Conversation Workflow Completed")
#         print("=" * 60)
#         print(f"Checked Conversations : {checked}")
#         print("=" * 60)


workflow = ConversationWorkflow()

workflow.run()