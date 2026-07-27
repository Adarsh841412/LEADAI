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
#     print("=" * 60)

#     flow_number = input("Select Workflow: ").strip()

#     if flow_number == "1":

#         workflow = LeadWorkflow(
#             job_title="Python Developer",
#             location="US",
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



import logging
import sys
logging.basicConfig(
    level=logging.INFO,  # Show INFO, WARNING, ERROR, CRITICAL
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.StreamHandler(sys.stdout),  # Print to console
    ]
)

# Now all your logger.info() calls will work!

from fastapi import FastAPI

from api.routes import router as lead_generation_router
from api.exception import register_exception_handlers

app = FastAPI(
    title="Lead AI API",
    version="1.0.0",
    description="Lead Generation & Outreach Automation API",
)

# Register global exception handlers
register_exception_handlers(app)

# Register all routes
app.include_router(
    lead_generation_router,
    prefix="/api/v1",
    tags=["Lead Generation"],
)




