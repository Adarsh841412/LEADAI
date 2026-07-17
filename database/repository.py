"""
database/repository.py
======================
Repository layer for Lead database operations.
"""

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session
from database.models import Lead, LeadStatus
from datetime import datetime
from sqlalchemy import or_
from database.models import MeetingStatus


class LeadRepository:
    """
    Repository responsible for all Lead database operations.
    """

    def __init__(self, db: Session) -> None:
        self.db = db

    # ------------------------------------------------------------------
    # Private Mapper
    # ------------------------------------------------------------------

    def _to_lead(
        self,
        job: dict[str, Any],
    ) -> Lead:
        """
        Convert a scraped job dictionary into a Lead ORM object.
        """
        
        email_guesses = job.get("recruiter", {}).get("emailGuesses", [])

        return Lead(
            job_id=job["jobId"],
            company=job["companyName"],
            job_title=job["title"],
            location=job.get("location"),
            job_url=job["jobUrl"],
            platform=job.get('platform','linkedin'),
            description=job.get("description"),
            skills=", ".join(job.get("skills", [])),
            email=email_guesses[0] if email_guesses else None,
            email_verified=False,
            status=LeadStatus.NEW,
            metadata_info=job,
            email_status="FOUND" if email_guesses else "PENDING",
        )

#    create 
    def save_lead(
        self,
        job: dict[str, Any],
    ) -> Lead:
        """
        Save a single lead. 
        """
        
        if self.job_exists(job["jobId"]):
            raise ValueError(
                f"Lead already exists : {job['jobId']}"
            )

        lead = self._to_lead(job)

        self.db.add(lead)
        self.db.commit()
        self.db.refresh(lead)

        return lead

    # bulk create 
    def save_leads(
        self,
        jobs: list[dict[str, Any]],
    ) -> int:
        """
        Save multiple leads.

        Returns:
            Number of newly inserted leads.
        """

        lead_objects: list[Lead] = []

        for job in jobs:

            if self.job_exists(job["jobId"]):
                continue

            lead_objects.append(
                self._to_lead(job)
            )

        if not lead_objects:
            return 0

        self.db.bulk_save_objects(
            lead_objects
        )

        self.db.commit()

        return len(lead_objects)

    # check existence of jobs
    
    def job_exists(
        self,
        job_id: str,
    ) -> bool:
        """
        Check whether a job already exists.
        """

        stmt = (
            select(Lead)
            .where(
                Lead.job_id == job_id
            )
        )

        return self.db.scalar(stmt) is not None

#    get all leads 

    def get_all_leads(
        self,
    ) -> list[Lead]:
        """
        Return all leads.
        """

        stmt = select(Lead)

        return list(
            self.db.scalars(stmt).all()
        )


    def get_lead_by_job_id(
        self,
        job_id: str,
    ) -> Lead | None:
        """
        Return a lead by Job ID.
        """

        stmt = (
            select(Lead)
            .where(
                Lead.job_id == job_id
            )
        )

        return self.db.scalar(stmt)


    def delete_lead(
        self,
        job_id: str,
    ) -> bool:
        """
        Delete a lead by Job ID.
        """

        lead = self.get_lead_by_job_id(
            job_id
        )

        if lead is None:
            return False

        self.db.delete(lead)
        self.db.commit()

        return True
    
    

# ------------------------------------------------------------------
# Connect Workflow
# ------------------------------------------------------------------

    def get_pending_connections(
        self,
    ) -> list[Lead]:
        """
        Return all leads that still need email enrichment.
        """

        stmt = (
            select(Lead)
            .where(Lead.email_status == "PENDING")
        )

        return list(self.db.scalars(stmt).all())


    def update_company_domain(
        self,
        lead_id: int,
        company_domain: str,
    ) -> bool:
        """
        Update company domain.
        """

        lead = self.db.get(Lead, lead_id)

        if lead is None:
            return False

        lead.company_domain = company_domain

        self.db.commit()

        return True


    def update_email(
        self,
        lead_id: int,
        email: str,
        verified: bool = False,
    ) -> bool:
        """
        Update lead email.
        """

        lead = self.db.get(Lead, lead_id)

        if lead is None:
            return False

        lead.email = email
        lead.email_verified = True
        lead.email_status = "FOUND"

        self.db.commit()

        return True


    def update_status(
        self,
        lead_id: int,
        status: LeadStatus,
    ) -> bool:
        """
        Update lead status.
        """

        lead = self.db.get(Lead, lead_id)

        if lead is None:
            return False

        lead.status = status

        self.db.commit()

        return True


    def update_contact(
        self,
        lead_id: int,
        company_domain: str,
        email: str,
        email_verified: bool = False,
    ) -> bool:
        """
        Update all enrichment fields in a single transaction.
        """

        lead = self.db.get(Lead, lead_id)

        if lead is None:
            return False

        lead.company_domain = company_domain
        lead.email = email
        lead.email_verified = email_verified
        lead.email_status = "FOUND"

        self.db.commit()

        return True
    
    
    # outreach workflow 
    
    def get_pending_outreach(
    self,
) -> list[Lead]:
        """
        Return all leads that are ready for outreach.

        Conditions:
        - Email has been enriched.
        - Email exists.
        """

        stmt = (
            select(Lead)
            .where(
                Lead.email_status == "FOUND",
                Lead.email.is_not(None),
                Lead.status != 'OUTREACH_SENT'
            )
        )

        return list(self.db.scalars(stmt).all())

    # update table after sending outreach 
    
    def update_after_send(self,lead_id:str,thread_id:str,message_id:str,rfc_message_id:str):
        
        lead = self.db.get(Lead,lead_id)
        lead.message_id = message_id
        lead.thread_id = thread_id 
        lead.rfc_message_id = rfc_message_id
        lead.status = LeadStatus.OUTREACH_SENT
        lead.last_contact_at = datetime.utcnow() 
        lead.followup_count = 0 
        
        self.db.commit() 
        return True 
    
    
    
    # * fllow up workflow 
    
    def get_pending_followups(self)->list[Lead]:
        """
        it will find all the lead that sent the pitch alreay 
        having follow_up count < 3
        last_contact <=3 days ago 
        
        
        """
        from sqlalchemy import or_

        stmt = (
            select(Lead)
            .where(
                or_(
                    Lead.status == LeadStatus.OUTREACH_SENT,
                    Lead.status == LeadStatus.FOLLOWUP_SENT,
                ),
                Lead.replied.is_(False),
                Lead.followup_count < 3,
            )
        )

        return list(self.db.scalars(stmt).all())
                
        
    def mark_as_replied(self,lead_id:int)->bool:
        
        """
        marks the replies that get the reply from the client
        """
        
        lead = self.db.get(Lead,lead_id)
        if lead is None :
            print('no pending lead exit')
            return None 
        
        lead.status == LeadStatus.REPLIED 
        lead.replied = True 
        self.db.commit()
        return True 
        
        
        
        
    def update_after_followup(
    self,
    lead_id: int,
    thread_id: str,
    message_id: str,
    rfc_message_id:str
) -> bool:
        """
        Update lead after sending a follow-up email.
        """

        lead = self.db.get(Lead, lead_id)

        if lead is None:

            print("Lead not found.")

            return False

        lead.status = LeadStatus.FOLLOWUP_SENT
        lead.followup_count += 1
        lead.last_contact_at = datetime.utcnow()
        lead.thread_id = thread_id
        lead.message_id = message_id
        lead.rfc_message_id = rfc_message_id

        self.db.commit()

        return True
    
    
    
    # reply workflow 
    
    def get_lead_to_check_reply(self)->list[Lead]:
        
        """
        Return all leads whose Gmail thread should be checked
        for a recruiter reply.
        """
        
        stmt = select(Lead).where(Lead.thread_id.is_not(None),Lead.thread_id != '' , Lead.replied == False)
        return list(self.db.scalars(stmt).all())
    
    
    # * meeting workflow 
    
    def get_pending_conversation(self)->list[Lead]:
        """
        Return all leads whose recruiter has replied
        but whose conversation has not yet been processed.
        """
        
        stmt = select(Lead).where(Lead.replied==True,Lead.conversation_processed == False)
        return list(self.db.scalars(stmt).all())
        
        
    # *conversation workflow 
    
    def save_meeting(
    self,
    lead_id: int,
    meeting,
) -> bool:
        """
        Save extracted meeting details.
        """

        lead = self.db.get(Lead, lead_id)

        if lead is None:

            print("Lead not found.")

            return False
    
        lead.meeting_date = meeting.get('meeting_date')
        lead.meeting_time = meeting.get('meeting_time')
        lead.meeting_status = MeetingStatus.SCHEDULED
        lead.timezone = meeting.get('timezone')
        lead.meeting_platform = meeting.get('meeting_platform')
        lead.meeting_link = meeting.get('meeting_link')

        # If you have this column
        lead.conversation_processed = True

        self.db.commit()

        return True
    


    def update_after_conversation(
        self,
        lead_id: int,
        thread_id: str,
        message_id: str,
        rfc_message_id: str,
    ) -> bool:
        """
        Update lead after sending a conversation reply.

        Updates:
            - thread_id
            - message_id
            - rfc_msg_id
            - last_contact_at
            - conversation_processed
        """

        lead = self.db.get(Lead, lead_id)

        if lead is None:

            print("Lead not found.")

            return False

        lead.thread_id = thread_id
        lead.message_id = message_id
        lead.rfc_msg_id = rfc_message_id
        lead.last_contact_at = datetime.utcnow()

        # Prevent processing the same conversation again
        lead.conversation_processed = True

        self.db.commit()

        return True
    
    
    
    def mark_rejected(
    self,
    lead_id: int,
) -> bool:

        lead = (
            self.db.query(Lead)
            .filter(Lead.id == lead_id)
            .first()
        )

        if lead is None:
            return False

        lead.status = LeadStatus.REJECTED
        lead.conversation_processed = True
        lead.last_contact_at = datetime.now()

        self.db.commit()

        return True
    


    def mark_manual_review(
        self,
        lead_id: int,
    ) -> bool:
        """
        Mark a lead for manual review when the conversation
        could not be classified confidently.
        """

        lead = (
            self.db.query(Lead)
            .filter(Lead.id == lead_id)
            .first()
        )

        if lead is None:
            return False

        lead.manual_review = True
        lead.conversation_processed = True
        lead.last_contact_at = datetime.now()

        self.db.commit()

        return True