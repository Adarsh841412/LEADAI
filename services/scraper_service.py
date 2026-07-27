# """
# Pipeline:
#     Apify
#         ↓
#     Filter
#         ↓
#     Validate
#         ↓
#     Deduplicate
#         ↓
#     Return Clean Jobs
# """


# from typing import Any

# from providers.apify import Lead_Provider
# from utils.filters import JobFilter
# from utils.validators import JobValidator
# from utils.dedup import JobDeduplicator


# class ScraperService:
#     """
#     Service responsible for scraping and cleaning jobs.
#     """

#     @classmethod
#     def scrape_jobs(
#         cls,
#         job_title: str,
#         location: str,
#         platform:str
#     ) -> list[dict[str, Any]]:
#         """
#         Scrape jobs and return cleaned results.

#         Steps:
#             1. Fetch jobs from Apify
#             2. Filter recent tech jobs
#             3. Validate jobs
#             4. Remove duplicates

#         Returns:
#             List of clean jobs.
#         """
#         try:
#             provider = Lead_Provider()

#             jobs = provider.fetch_jobs(
#                 job_title=job_title,
#                 location=location,
#                 platform=platform
#             )
#         except Exception as e:
#             print(e)
#             return []
            
#         print("filter recent tech jobs ")
#         jobs = JobFilter.filter_recent_tech_jobs(jobs)
#         print("validate jobs")
#         jobs = JobValidator.validate_jobs(jobs)
#         print("remove dupliate jobs")
#         jobs = JobDeduplicator.remove_duplicates(jobs)

#         # print(jobs)
#         return jobs




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

import logging
import time
from typing import Any, List, Dict, Optional

from providers.apify import LeadProvider
from utils.filters import JobFilter
from utils.validators import JobValidator
from utils.dedup import JobDeduplicator

# Setup logging
logger = logging.getLogger(__name__)




class ScraperServiceError(Exception):
    """Base exception for ScraperService errors."""
    pass


class ScraperService:
    """
    Service responsible for scraping and cleaning jobs.
    
    Pipeline:
        1. Fetch jobs from Apify
        2. Filter recent tech jobs
        3. Validate jobs
        4. Remove duplicates
        5. Return clean jobs
    """
    
    # Configuration
    MAX_RETRIES = 3
    RETRY_DELAY = 2  # seconds
    REQUEST_TIMEOUT = 30  # seconds
    
    @classmethod
    def _fetch_with_retry(
        cls,
        provider: LeadProvider,
        job_title: str,
        location: str,
        platform: str
    ) -> List[Dict[str, Any]]:
        """
        Fetch jobs with retry logic.
        
        Args:
            provider: Lead provider instance
            job_title: Job title to search
            location: Location to search
            platform: Platform to use
            
        Returns:
            List of job dictionaries
            
        Raises:
            Exception: If fetching fails after all retries
        """
        last_error = None
        
        for attempt in range(cls.MAX_RETRIES):
            try:
                logger.info(
                    f"Fetching jobs (attempt {attempt + 1}/{cls.MAX_RETRIES}): "
                    f"{job_title} in {location} on {platform}"
                )
                
                jobs = provider.fetch_jobs(
                    job_title=job_title,
                    location=location,
                    platform=platform
                )
                
                logger.info(f"Successfully fetched {len(jobs)} jobs")
                return jobs
                
            except Exception as e:
                last_error = e
                logger.warning(f"Fetch attempt {attempt + 1} failed: {e}")
                
                if attempt < cls.MAX_RETRIES - 1:
                    wait_time = cls.RETRY_DELAY * (2 ** attempt)
                    logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
        
        # All retries failed
        logger.error(f"All {cls.MAX_RETRIES} fetch attempts failed")
        raise last_error or Exception("Failed to fetch jobs after multiple retries")
    
    @classmethod
    def _safe_apply_filter(cls, jobs: List[Dict[str, Any]], filter_name: str, filter_func) -> List[Dict[str, Any]]:
        """
        Safely apply a filter with error handling.
        
        Args:
            jobs: List of jobs
            filter_name: Name of the filter for logging
            filter_func: Filter function to apply
            
        Returns:
            Filtered list of jobs (original list if filter fails)
        """
        if not jobs:
            logger.info(f"Skipping {filter_name}: No jobs to process")
            return jobs
        
        try:
            logger.info(f"Applying {filter_name}...")
            filtered = filter_func(jobs)
            logger.info(f"{filter_name} completed: {len(filtered)} jobs remaining")
            return filtered
            
        except Exception as e:
            logger.error(f"{filter_name} failed: {e}", exc_info=True)
            logger.warning(f"Continuing without {filter_name} filter")
            return jobs  # Return original jobs if filter fails
    
    @classmethod
    def scrape_jobs(
        cls,
        job_title: str,
        location: str,
        platform: str,
        max_retries: Optional[int] = None,
        retry_delay: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Scrape jobs and return cleaned results.

        Steps:
            1. Fetch jobs from Apify (with retry)
            2. Filter recent tech jobs
            3. Validate jobs
            4. Remove duplicates

        Args:
            job_title: Job title to search for
            location: Location to search in
            platform: Platform to use (linkedin, indeed, glassdoor)
            max_retries: Maximum number of retry attempts (optional)
            retry_delay: Delay between retries in seconds (optional)

        Returns:
            List of clean jobs (empty list if no jobs found or all filters fail)
        """
        # Override class constants if provided
        if max_retries is not None and max_retries > 0:
            cls.MAX_RETRIES = max_retries
        if retry_delay is not None and retry_delay > 0:
            cls.RETRY_DELAY = retry_delay
        
        logger.info(
            f"Starting scrape_jobs: job_title='{job_title}', "
            f"location='{location}', platform='{platform}'"
        )
        
        # Step 1: Fetch jobs from Apify
        try:
            provider = LeadProvider()
            jobs = cls._fetch_with_retry(
                provider,
                job_title=job_title,
                location=location,
                platform=platform
            )
            
        except Exception as e:
            logger.error(f"Failed to fetch jobs: {e}", exc_info=True)
            return []
        
        # Check if any jobs were fetched
        if not jobs:
            logger.warning("No jobs fetched from provider")
            return []
        
        logger.info(f"Fetched {len(jobs)} raw jobs")
        
        # Step 2: Filter recent tech jobs
        jobs = cls._safe_apply_filter(
            jobs,
            "filter_recent_tech_jobs",
            JobFilter.filter_recent_tech_jobs
        )
        
        if not jobs:
            logger.warning("All jobs filtered out after tech filter")
            return []
        
        # Step 3: Validate jobs
        jobs = cls._safe_apply_filter(
            jobs,
            "validate_jobs",
            JobValidator.validate_jobs
        )
        
        if not jobs:
            logger.warning("All jobs filtered out after validation")
            return []
        
        # Step 4: Remove duplicates
        jobs = cls._safe_apply_filter(
            jobs,
            "remove_duplicates",
            JobDeduplicator.remove_duplicates
        )
        
        if not jobs:
            logger.warning("All jobs filtered out after deduplication")
            return []
        
        # Final result
        logger.info(f"Scrape completed successfully: {len(jobs)} clean jobs returned")
        return jobs
    
    @classmethod
    def scrape_jobs_safe(
        cls,
        job_title: str,
        location: str,
        platform: str,
        max_retries: Optional[int] = None,
        retry_delay: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """

        Args:
            job_title: Job title to search for
            location: Location to search in
            platform: Platform to use
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds
            
        Returns:
            List of clean jobs (empty list on any error)
        """
        try:
            return cls.scrape_jobs(
                job_title=job_title,
                location=location,
                platform=platform,
                max_retries=max_retries,
                retry_delay=retry_delay
            )
        except Exception as e:
            logger.error(f"scrape_jobs_safe caught unexpected error: {e}", exc_info=True)
            return []