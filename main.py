from workflows.lead_workflow import LeadWorkflow
from workflows.connect_workflow import ConnectWorkflow
from workflows.outreach_workflow import OutreachWorkflow
from workflows.replyworkflow import ReplyWorkflow
from workflows.followup_workflow import FollowUpWorkflow


def main():

    print("\n" + "=" * 55)
    print("           LEAD AI AUTOMATION")
    print("=" * 55)
    print("1. Lead Workflow")
    print("2. Connect Workflow")
    print("3. Outreach Workflow")
    print("=" * 55)

    flow_number = input("Select Workflow: ").strip()

    if flow_number == "1":

        workflow = LeadWorkflow(
            job_title="Python Developer",
            location="USA",
        )

        workflow.run()

    elif flow_number == "2":

        workflow = ConnectWorkflow()

        workflow.run()

    elif flow_number == "3":

        workflow = OutreachWorkflow()

        workflow.run()

    elif flow_number == "4":

        workflow = ReplyWorkflow()

        workflow.run()

    elif flow_number == "5":

        workflow = FollowUpWorkflow()

        workflow.run()

    else:

        print("❌ Invalid workflow selected.")


if __name__ == "__main__":
    main()










# # from google_auth_oauthlib.flow import InstalledAppFlow

# # SCOPES = [
# #     "https://www.googleapis.com/auth/gmail.send",
# #     "https://www.googleapis.com/auth/gmail.readonly",
# #     "https://www.googleapis.com/auth/gmail.modify",
# # ]

# # flow = InstalledAppFlow.from_client_secrets_file(
# #     "credentials.json",
# #     SCOPES,
# # )

# # creds = flow.run_local_server(port=0)

# # with open("token.json", "w") as token:
# #     token.write(creds.to_json())

# # print("Token generated successfully!")
