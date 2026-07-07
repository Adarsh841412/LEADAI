"""
database/repository.py
======================
Repository layer for Lead database operations.
"""

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from database.models import Lead, LeadStatus


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
            platform="LinkedIn",
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
        lead.email_verified = verified
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




