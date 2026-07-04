"""
Pipeline:
    Apify
        ↓
    Filter
        ↓
    Validate
        ↓
    Deduplicate
        ↓
    Return Clean Jobs
"""


from typing import Any

from providers.apify import ApifyProvider
from utils.filters import JobFilter
from utils.validators import JobValidator
from utils.dedup import JobDeduplicator


class ScraperService:
    """
    Service responsible for scraping and cleaning jobs.
    """

    @classmethod
    def scrape_jobs(
        cls,
        job_title: str,
        location: str,
    ) -> list[dict[str, Any]]:
        """
        Scrape jobs and return cleaned results.

        Steps:
            1. Fetch jobs from Apify
            2. Filter recent tech jobs
            3. Validate jobs
            4. Remove duplicates

        Returns:
            List of clean jobs.
        """
        try:
            provider = ApifyProvider()

            jobs = provider.fetch_jobs(
                job_title=job_title,
                location=location,
            )
        except Exception as e:
            print(e)
            return 
            
        
        jobs = JobFilter.filter_recent_tech_jobs(jobs)

        jobs = JobValidator.validate_jobs(jobs)

        jobs = JobDeduplicator.remove_duplicates(jobs)
     
        return jobs