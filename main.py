
from scheduler.scheduler import LeadScheduler


def main():

    scheduler = LeadScheduler()

    scheduler.start()


if __name__ == "__main__":
    main()






# from workflows.lead_workflow import LeadWorkflow
# from workflows.connect_workflow import ConnectWorkflow
# from workflows.outreach_workflow import OutreachWorkflow
# from workflows.replyworkflow import ReplyWorkflow
# from workflows.followup_workflow import FollowUpWorkflow
# from workflows.conversation_workflow import ConversationWorkflow


# def main():

#     print("\n" + "=" * 60)
#     print("                 LEAD AI AUTOMATION")
#     print("=" * 60)
#     print("1. Lead Workflow")
#     print("2. Connect Workflow")
#     print("3. Outreach Workflow")
#     print("4. Reply Workflow")
#     print("5. Follow-up Workflow")
#     print("6. Conversation Workflow")
#     print("=" * 60)

#     flow_number = input("Select Workflow: ").strip()

#     if flow_number == "1":

#         workflow = LeadWorkflow(
#             job_title="Python Developer",
#             location="USA",
#         )

#         print(workflow.run())

#     elif flow_number == "2":

#         workflow = ConnectWorkflow()

#         print(workflow.run())

#     elif flow_number == "3":

#         workflow = OutreachWorkflow()

#         workflow.run()

#     elif flow_number == "4":

#         workflow = ReplyWorkflow()

#         workflow.run()

#     elif flow_number == "5":

#         workflow = FollowUpWorkflow()

#         workflow.run()

#     elif flow_number == "6":

#         workflow = ConversationWorkflow()

#         workflow.run()

#     else:

#         print("\n❌ Invalid workflow selected.")


# if __name__ == "__main__":
#     main()  




