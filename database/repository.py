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

        return Lead(
            job_id=job["jobId"],
            company=job["companyName"],
            job_title=job["title"],
            location=job.get("location"),
            job_url=job["jobUrl"],
            platform="LinkedIn",
            description=job.get("description"),
            skills=", ".join(job.get("skills", [])),
            email=None,
            email_verified=False,
            status=LeadStatus.NEW,
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
    
    
