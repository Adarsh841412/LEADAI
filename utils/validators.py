"""
Validate jobs returned by the Apify provider.
"""

from typing import Any


class JobValidator:
    """
    Validates job data before further processing.
    """

    REQUIRED_FIELDS = (
        "jobId",
        "title",
        "companyName",
        "jobUrl",
        "description",
        "datePosted",
    )

    @classmethod
    def is_valid_job(cls, job: dict[str, Any]) -> bool:
        """
        Validate a single job.

        Returns:
            True  -> Valid Job
            False -> Invalid Job
        """

        # Validate required fields
        for field in cls.REQUIRED_FIELDS:

            value = job.get(field)

            if value is None:
                return False

            if isinstance(value, str) and not value.strip():
                return False

        # Validate URL
        job_url = str(job.get("jobUrl", "")).strip()

        if not (
            job_url.startswith("http://")
            or job_url.startswith("https://")
        ):
            return False

        return True

    @classmethod
    def validate_jobs(
        cls,
        jobs: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """
        Validate multiple jobs.

        Returns:
            List of valid jobs.
        """

        return [
            job
            for job in jobs
            if cls.is_valid_job(job)
        ]

        
        