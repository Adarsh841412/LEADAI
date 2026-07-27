"""
database/repository.py
======================
Repository layer for Lead database operations.
"""

from typing import Any
import logging
from sqlalchemy import select
from sqlalchemy.orm import Session
from database.models import Lead, LeadStatus
from datetime import datetime
from sqlalchemy import or_
from database.models import MeetingStatus
from sqlalchemy import select, or_, and_, text
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, OperationalError

logger = logging.getLogger(__name__)
class LeadRepository:
    """
    Repository responsible for all Lead database operations.
    """

    def __init__(self, db: Session) -> None:
        self.db = db
    
    def save_leads(
    self,
    jobs: list[dict[str, Any]],
) -> int:
        """
        Save multiple leads.

        Returns:
            Number of newly inserted leads.
            
        Raises:
            ValueError: If jobs is None or invalid
            Exception: For database errors (handled by caller)
        """
        #  Input validation
        if jobs is None:
            logger.warning("jobs is None, returning 0")
            return 0
        
        if not jobs:
            logger.info("Empty job list provided to save_leads")
            return 0

        logger.info(f"Processing {len(jobs)} jobs for saving")
        
        lead_objects: list[Lead] = []
        duplicate_count = 0
        error_count = 0
        for idx, job in enumerate(jobs):
            try:
                #  Validate job exists
                if not job:
                    logger.warning(f"Job at index {idx} is None, skipping")
                    error_count += 1
                    continue
                
                #  Validate jobId exists
                job_id = job.get("jobId")
                if not job_id:
                    logger.warning(f"Job at index {idx} missing jobId, skipping")
                    error_count += 1
                    continue
                
                #  Check for duplicates (with error handling)
                try:
                    if self.job_exists(str(job_id)):
                        duplicate_count += 1
                        continue
                except Exception as e:
                    logger.error(f"Error checking job existence for {job_id}: {e}")
                    error_count += 1
                    continue
                
                #  Convert to lead (may raise ValueError)
                try:
                    lead = self._to_lead(job)
                    lead_objects.append(lead)
                except ValueError as e:
                    logger.warning(f"Validation error for job {job_id}: {e}")
                    error_count += 1
                    continue
                except Exception as e:
                    logger.error(f"Error converting job {job_id} to lead: {e}")
                    error_count += 1
                    continue
                    
            except Exception as e:
                logger.error(f"Unexpected error processing job at index {idx}: {e}")
                error_count += 1
                continue

        if not lead_objects:
            logger.info(
                f"No new leads to save. "
                f"Duplicates: {duplicate_count}, Errors: {error_count}"
            )
            return 0

        try:
            #  Bulk save with transaction
            self.db.bulk_save_objects(lead_objects)
            self.db.commit()
            
            saved_count = len(lead_objects)
            logger.info(
                f"Successfully saved {saved_count} leads. "
                f"Duplicates skipped: {duplicate_count}, "
                f"Errors: {error_count}"
            )
            return saved_count
            
        except Exception as e:
            #  Rollback on error
            self.db.rollback()
            logger.error(f"Database error saving leads: {e}", exc_info=True)
            raise  # Re-raise for caller to handle


    def job_exists(
        self,
        job_id: str,
    ) -> bool:
        """
        Check whether a job already exists.
        
        Args:
            job_id: Job ID to check
            
        Returns:
            True if exists, False otherwise
        """
        #  Validate input
        if not job_id:
            logger.warning("job_id is None or empty, returning False")
            return False
        
        try:
            stmt = (
                select(Lead)
                .where(Lead.job_id == str(job_id))
            )
            result = self.db.scalar(stmt)
            exists = result is not None
            
            if exists:
                logger.debug(f"Job {job_id} already exists")
            
            return exists
            
        except Exception as e:
            #  Log error but don't crash
            logger.error(f"Error checking if job {job_id} exists: {e}")
            #  Return False as fallback (better to try saving than skip)
            return False


    def _to_lead(
        self,
        job: dict[str, Any],
    ) -> Lead:
        """
        Convert a scraped job dictionary into a Lead ORM object.
        
        Args:
            job: Job dictionary
            
        Returns:
            Lead ORM object
            
        Raises:
            ValueError: If required fields are missing or invalid
        """
        #  Validate job is not None
        if not job:
            raise ValueError("Job data is required")
        
        #  Validate required fields
        required_fields = ['jobId', 'companyName', 'title', 'jobUrl']
        missing_fields = []
        
        for field in required_fields:
            value = job.get(field)
            if value is None or str(value).strip() == '':
                missing_fields.append(field)
        
        if missing_fields:
            raise ValueError(
                f"Missing required fields: {', '.join(missing_fields)}"
            )
        
        #  Extract and validate email
        email_guesses = job.get("recruiter", {}).get("emailGuesses", [])
        email = email_guesses[0] if email_guesses else None
        
        #  Basic email validation (if present)
        if email:
            import re
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, str(email)):
                logger.warning(f"Invalid email format, skipping: {email}")
                email = None
        
        #  Sanitize fields to prevent database errors
        def sanitize(value, max_length=255, default=""):
            if value is None:
                return default
            sanitized = ' '.join(str(value).strip().split())
            if len(sanitized) > max_length:
                logger.warning(f"Truncating field from {len(sanitized)} to {max_length}")
                sanitized = sanitized[:max_length]
            return sanitized
        
        #  Build lead object
        try:
            lead = Lead(
                job_id=str(job["jobId"]).strip(),
                company=sanitize(job["companyName"], 255, "Unknown Company"),
                job_title=sanitize(job["title"], 255, "Unknown Title"),
                location=sanitize(job.get("location", ""), 255, "Unknown"),
                job_url=str(job["jobUrl"]).strip(),
                platform=sanitize(job.get('platform', 'linkedin'), 50, 'linkedin').lower(),
                description=sanitize(job.get("description", ""), 10000, ""),
                skills=", ".join(job.get("skills", [])[:20])[:1000],  # Limit to 20 skills, 1000 chars
                email=email,
                email_verified=False,
                status=LeadStatus.NEW,
                metadata_info=job,
                email_status="FOUND" if email else "PENDING",
            )
            
            logger.debug(f"Successfully converted job {job['jobId']} to Lead")
            return lead
            
        except Exception as e:
            logger.error(f"Error creating Lead object for job {job.get('jobId', 'unknown')}: {e}")
            raise ValueError(f"Failed to convert job to Lead: {str(e)}") from e

    # def _to_lead(
    #     self,
    #     job: dict[str, Any],
    # ) -> Lead:
    #     """
    #     Convert a scraped job dictionary into a Lead ORM object.
    #     """
        
    #     email_guesses = job.get("recruiter", {}).get("emailGuesses", [])

    #     return Lead(
    #         job_id=job["jobId"],
    #         company=job["companyName"],
    #         job_title=job["title"],
    #         location=job.get("location"),
    #         job_url=job["jobUrl"],
    #         platform=job.get('platform','linkedin'),
    #         description=job.get("description"),
    #         skills=", ".join(job.get("skills", [])),
    #         email=email_guesses[0] if email_guesses else None,
    #         email_verified=False,
    #         status=LeadStatus.NEW,
    #         metadata_info=job,
    #         email_status="FOUND" if email_guesses else "PENDING",
    #     )

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

    # # bulk create 
    # def save_leads(
    #     self,
    #     jobs: list[dict[str, Any]],
    # ) -> int:
    #     """
    #     Save multiple leads.

    #     Returns:
    #         Number of newly inserted leads.
    #     """
        

    #     lead_objects: list[Lead] = []

    #     for job in jobs:

    #         if self.job_exists(job["jobId"]):
    #             continue

    #         lead_objects.append(
    #             self._to_lead(job)
    #         )

    #     if not lead_objects:
    #         return 0

    #     try :
    #         self.db.bulk_save_objects(
    #         lead_objects
    #     )

    #         self.db.commit()

    #         return len(lead_objects)
    #     except Exception :
    #         self.db.rollback() 
    #         raise 

    # # check existence of jobs
    
    # def job_exists(
    #     self,
    #     job_id: str,
    # ) -> bool:
    #     """
    #     Check whether a job already exists.
    #     """

    #     stmt = (
    #         select(Lead)
    #         .where(
    #             Lead.job_id == job_id
    #         )
    #     )

    #     return self.db.scalar(stmt) is not None

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

    # def get_pending_connections(
    #     self,
    # ) -> list[Lead]:
    #     """
    #     Return all leads that still need email enrichment.
    #     """
    #     try:

    #         stmt = (
    #             select(Lead)
    #             .where(Lead.email_status == "PENDING")
    #         )

    #         return list(self.db.scalars(stmt).all())
    #     except Exception as e:
    #         print("error in get pending connection repository",e)
    #         return []

    # database/repository.py

    def get_pending_connections(self) -> list[Lead]:
        """
        Return all leads that still need email enrichment.
        
        Returns:
            List of Lead objects with email_status = "PENDING"
            Returns empty list on error or if no pending leads found
            
        Raises:
            No exceptions raised (handled internally)
        """
        try:
            stmt = (
                select(Lead)
                .where(Lead.email_status == "PENDING")
            )
            
            results = list(self.db.scalars(stmt).all())
            logger.info(f"Found {len(results)} pending connections")
            return results
            
        except SQLAlchemyError as e:
            logger.error(f"Database error in get_pending_connections: {e}", exc_info=True)
            return []
            
        except Exception as e:
            logger.error(f"Unexpected error in get_pending_connections: {e}", exc_info=True)
            return []

    # def update_company_domain(
    #     self,
    #     lead_id: int,
    #     company_domain: str,
    # ) -> bool:
    #     """
    #     Update company domain.
    #     """
        
    #     try : 
    #         lead = self.db.get(Lead, lead_id)

    #         if lead is None:
    #             return False

    #         lead.company_domain = company_domain

    #         self.db.commit()

    #         return True

    #     except Exception as e:
    #         self.db.rollback() 
    #         raise 
       
       
    def update_company_domain(
    self,
    lead_id: int,
    company_domain: str,
) -> bool:
        """
        Update company domain for a lead.
        
        Args:
            lead_id: ID of the lead to update
            company_domain: Company domain to set
        
        Returns:
            True if updated successfully, False if lead not found
            
        Raises:
            ValueError: If lead_id is invalid
            SQLAlchemyError: For database errors
        """
        #  Validate input
        if not isinstance(lead_id, int) or lead_id <= 0:
            logger.warning(f"Invalid lead_id: {lead_id}")
            return False
        
        if not company_domain or not str(company_domain).strip():
            logger.warning(f"Empty company_domain for lead {lead_id}")
            return False
        
        try:
            #  Get lead
            lead = self.db.get(Lead, lead_id)
            
            if lead is None:
                logger.warning(f"Lead not found with id: {lead_id}")
                return False
            
            #  Update domain
            lead.company_domain = str(company_domain).strip()
            
            #  Commit transaction
            self.db.commit()
            
            logger.info(f"Updated company domain for lead {lead_id}: {company_domain}")
            return True
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error updating company domain for lead {lead_id}: {e}", exc_info=True)
            raise
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Unexpected error updating company domain for lead {lead_id}: {e}", exc_info=True)
            raise   
        
        
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


    # def update_contact(
    #     self,
    #     lead_id: int,
    #     company_domain: str,
    #     email: str,
    #     email_verified: bool = False,
    # ) -> bool:
    #     """
    #     Update all enrichment fields in a single transaction.
    #     """
    #     try :

    #         lead = self.db.get(Lead, lead_id)

    #         if lead is None:
    #             return False

    #         lead.company_domain = company_domain
    #         lead.email = email
    #         lead.email_verified = email_verified
    #         lead.email_status = "FOUND"

    #         self.db.commit()

    #         return True
    #     except Exception as e:
    #         self.db.rollback() 
    #         raise 
    
    def update_contact(
    self,
    lead_id: int,
    company_domain: str,
    email: str,
    email_verified: bool = False,
) -> bool:
        """
        Update all enrichment fields in a single transaction.
        
        Args:
            lead_id: ID of the lead to update
            company_domain: Company domain to set
            email: Email address to set
            email_verified: Whether email is verified (default: False)
        
        Returns:
            True if updated successfully, False if lead not found
            
        Raises:
            ValueError: If lead_id is invalid or email format is invalid
            SQLAlchemyError: For database errors
        """
        #  Validate lead_id
        if not isinstance(lead_id, int) or lead_id <= 0:
            logger.warning(f"Invalid lead_id: {lead_id}")
            return False
        
        #  Validate company_domain
        if not company_domain or not str(company_domain).strip():
            logger.warning(f"Empty company_domain for lead {lead_id}")
            return False
        
        #  Validate email
        if not email or not str(email).strip():
            logger.warning(f"Empty email for lead {lead_id}")
            return False
        
        #  Validate email format (basic)
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, str(email).strip()):
            logger.warning(f"Invalid email format for lead {lead_id}: {email}")
            return False
        
        try:
            #  Get lead
            lead = self.db.get(Lead, lead_id)
            
            if lead is None:
                logger.warning(f"Lead not found with id: {lead_id}")
                return False
            
            #  Update fields
            lead.company_domain = str(company_domain).strip()
            lead.email = str(email).strip()
            lead.email_verified = email_verified
            lead.email_status = "FOUND"
            
            #  Commit transaction
            self.db.commit()
            
            logger.info(f"Updated contact for lead {lead_id}: {email} (verified: {email_verified})")
            return True
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error updating contact for lead {lead_id}: {e}", exc_info=True)
            raise
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Unexpected error updating contact for lead {lead_id}: {e}", exc_info=True)
            raise
        
    
    
    
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
        try :
            stmt = (
                select(Lead)
                .where(
                    Lead.email_status == "FOUND",
                    Lead.email.is_not(None),
                    Lead.status != 'OUTREACH_SENT'
                )
            )

            return list(self.db.scalars(stmt).all())
        except Exception as e :
            print("Error getting pending outreach:", e)
            return []

    # update table after sending outreach 
    
    def update_after_send(self,lead_id:str,thread_id:str,message_id:str,rfc_message_id:str):
        try :
            lead = self.db.get(Lead,lead_id)
            if lead is None:
                return False 
            lead.message_id = message_id
            lead.thread_id = thread_id 
            lead.rfc_message_id = rfc_message_id
            lead.status = LeadStatus.OUTREACH_SENT
            lead.last_contact_at = datetime.utcnow() 
            lead.followup_count = 0 
            
            self.db.commit() 
            return True 
        except Exception as e:
            self.db.rollback() 
            print("Error occured in update after send",e)
            return False 
        
        
        
    
    
    # * fllow up workflow 
    
    def get_pending_followups(self)->list[Lead]:
        """
        it will find all the lead that sent the pitch alreay 
        having follow_up count < 3
        last_contact <=3 days ago 
        
        
        """
        from sqlalchemy import or_
        try : 
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
        except Exception as e:
            print('error in peding followups',e)
            return []         
        
    def mark_as_replied(self,lead_id:int)->bool:
        
        """
        marks the replies that get the reply from the client
        """
        
        try :
        
            lead = self.db.get(Lead,lead_id)
            if lead is None :
                print('no pending lead exit')
                return False
            
            lead.status = LeadStatus.REPLIED 
            lead.replied = True 
            self.db.commit()
            return True 
            
        except Exception as e:
            print("error occured while marks as replied",e) 
            self.db.rollback() 
            return False     
        
        
        
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
        try :
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
        except Exception :
            self.db.rollback() 
            raise 
        
        
    
    # reply workflow 
    
    def get_lead_to_check_reply(self)->list[Lead]:
        
        """
        Return all leads whose Gmail thread should be checked
        for a recruiter reply.
        """
        try :
            stmt = select(Lead).where(Lead.thread_id.is_not(None),Lead.thread_id != '' , Lead.replied == False)
            return list(self.db.scalars(stmt).all())
        except Exception as e:
            print("error occured in get_lead_to_check_reply",e)
            return []
        
    
    # * meeting workflow 
    
    def get_pending_conversation(self)->list[Lead]:
        """
        Return all leads whose recruiter has replied
        but whose conversation has not yet been processed.
        """
        try :
        
            stmt = select(Lead).where(Lead.replied==True,Lead.conversation_processed == False)
            return list(self.db.scalars(stmt).all())
        except Exception as e:
            print('error occured in get pending conversation',e)
            return []
        
        
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
        try :

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
        except Exception as e:
            self.db.rollback() 
            print("error occured in update after conversation")
            return False 
      
    
    
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
    
    
    
    # * for assesment 
    def save_assessment(self, lead_id: str, assessment: dict):

        try :
            lead = self.db.get(Lead, lead_id)

            if lead is None:
                print("Lead not found.")
                return False

            lead.assessment_link = assessment["assessment_link"]
            lead.assessment_deadline = assessment["assessment_deadline"]
            lead.status = LeadStatus.ASSESSMENT_PENDING

            self.db.commit()

            return True
        except Exception as e:
            print("errorin db ",e)
            self.db.rollback() 
            return False 
            
           
    