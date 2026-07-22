from workflows.lead_workflow import LeadWorkflow
from workflows.connect_workflow import ConnectWorkflow
from workflows.outreach_workflow import OutreachWorkflow
from workflows.replyworkflow import ReplyWorkflow
from workflows.followup_workflow import FollowUpWorkflow
from workflows.conversation_workflow import ConversationWorkflow


def register_jobs(scheduler):

    # ------------------------------------------------------------------
    # Lead Workflow
    # Runs once every day at 09:00 AM
    # ------------------------------------------------------------------
    scheduler.add_job(
        LeadWorkflow().run,
        trigger="cron",
        hour=9,
        minute=0,
        id="lead_workflow",
        replace_existing=True,
        args=["Python Developer", "USA"],
    )

    # ------------------------------------------------------------------
    # Connect Workflow
    # Runs once every day at 09:10 AM
    # ------------------------------------------------------------------
    scheduler.add_job(
        ConnectWorkflow().run,
        trigger="cron",
        hour=9,
        minute=10,
        id="connect_workflow",
        replace_existing=True,
    )

    # ------------------------------------------------------------------
    # Outreach Workflow
    # Runs once every day at 09:20 AM
    # ------------------------------------------------------------------
    scheduler.add_job(
        OutreachWorkflow().run,
        trigger="cron",
        hour=9,
        minute=20,
        id="outreach_workflow",
        replace_existing=True,
    )

    # ------------------------------------------------------------------
    # Reply Workflow
    # Runs every 5 minutes
    # ------------------------------------------------------------------
    scheduler.add_job(
        ReplyWorkflow().run,
        trigger="interval",
        minutes=5,
        id="reply_workflow",
        replace_existing=True,
    )

    # ------------------------------------------------------------------
    # Follow-Up Workflow
    # Runs once every 3 days
    # ------------------------------------------------------------------
    scheduler.add_job(
        FollowUpWorkflow().run,
        trigger="interval",
        days=3,
        id="followup_workflow",
        replace_existing=True,
    )

    # ------------------------------------------------------------------
    # Conversation Workflow
    # Runs every 5 minutes
    # ------------------------------------------------------------------
    scheduler.add_job(
        ConversationWorkflow().run,
        trigger="interval",
        minutes=5,
        id="conversation_workflow",
        replace_existing=True,
    )



