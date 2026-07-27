# from services.scraper_service import ScraperService
# from database.repository import LeadRepository
# from database.db import get_db
# class LeadWorkflow:
#     def __init__(self,job_title,location,platform)->None:
#         self.job_title=job_title
#         self.location= location 
#         self.platfrom=platform.strip().lower() 
        
#     def run(self)->dict:
        
#         # step1 scrapt the job 
        
#         jobs = ScraperService.scrape_jobs(self.job_title,self.location,self.platfrom)
        
#         if not jobs :

#             return {
#                     "status": "failed",
#                     "message": "No jobs found."
#                 }
                    
#         db = get_db() 
        
#         # step3 * save all this data into repository 
        
#         try :
#             repository = LeadRepository(db)
#             saved_jobs = repository.save_leads(jobs)
            
#             return {
#                 "status":'success',
#                 "scraped_jobs":len(jobs),
#                 "saved_jobs":saved_jobs
#             }
        
#         except Exception as e:
#             print(e)
#             return {
#                 'status':'failed',
#                 'message':'database error'
#             }    
            
#         finally:
#             db.close() 
                
            
     
        
        
          
# lead_workflow.py
from sqlalchemy import text
import logging
import time
from typing import Optional, Dict, Any

from services.scraper_service import ScraperService
from database.repository import LeadRepository
from database.db import get_db

# Setup logging
logger = logging.getLogger(__name__)



class LeadWorkflow:
    """
    LeadWorkflow orchestrates the lead generation process:
    1. Scrape jobs from platform
    2. Save jobs to database
    """
    
    # Configuration constants
    MAX_RETRIES = 3
    RETRY_DELAY = 1  # seconds
    
    def __init__(self, job_title: str, location: str, platform: str) -> None:
        """
        Initialize the workflow with input validation.
        
        Args:
            job_title: Job title to search for
            location: Location to search in
            platform: Platform to use (linkedin, indeed, glassdoor)
            
        Raises:
            ValueError: If any input is invalid
        """
        # Validate inputs
        if not job_title or not str(job_title).strip():
            raise ValueError("Job title is required and cannot be empty")
        
        if not location or not str(location).strip():
            raise ValueError("Location is required and cannot be empty")
        
        if not platform or not str(platform).strip():
            raise ValueError("Platform is required and cannot be empty")
        
        # Store validated inputs
        self.job_title = str(job_title).strip()
        self.location = str(location).strip()
        self.platform = str(platform).strip().lower()  # Fixed: platform (not platfrom)
        print(self.platform)
        # Validate platform
        valid_platforms = ['linkedin', 'indeed', 'glassdoor']
        if self.platform not in valid_platforms:
            raise ValueError(
                f"Invalid platform: '{platform}'. "
                f"Must be one of: {', '.join(valid_platforms)}"
            )
        
        logger.info(
            f"LeadWorkflow initialized: job_title='{self.job_title}', "
            f"location='{self.location}', platform='{self.platform}'"
        )
    
    def _get_db_connection_with_retry(self) -> Any:
        """
        Establish database connection with retry logic.
        
        Returns:
            Database connection object
            
        Raises:
            Exception: If connection fails after all retries
        """
        last_error = None
        
        for attempt in range(self.MAX_RETRIES):
            try:
                db = get_db()
                # Test connection
                db.execute(text("SELECT 1"))
                logger.info(f"Database connected on attempt {attempt + 1}")
                return db
                
            except Exception as e:
                last_error = e
                logger.warning(
                    f"Database connection attempt {attempt + 1}/{self.MAX_RETRIES} failed: {e}"
                )
                
                if attempt < self.MAX_RETRIES - 1:
                    wait_time = self.RETRY_DELAY * (2 ** attempt)  # Exponential backoff
                    logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
        
        # All retries failed
        logger.error(f"Failed to connect to database after {self.MAX_RETRIES} attempts")
        raise last_error or Exception("Database connection failed")
    
    def run(self) -> dict:
        """
        Execute the complete workflow.
        
        Returns:
            Dictionary with status and results:
            {
                "status": "success" or "failed",
                "scraped_jobs": int,
                "saved_jobs": int,
                "message": str (optional)
            }
        """
        logger.info("Starting LeadWorkflow execution")
        
        # Step 1: Scrape jobs
        try:
            jobs = ScraperService.scrape_jobs(
                self.job_title,
                self.location,
                self.platform 
            )
            
            logger.info(f"Scraped {len(jobs)} jobs")
            
        except Exception as e:
            logger.error(f"Scraping failed: {e}", exc_info=True)
            return {
                "status": "failed",
                "message": f"Scraping failed: {str(e)}"
            }
        
        # Check if any jobs found
        if not jobs:
            logger.warning(f"No jobs found for {self.job_title} in {self.location}")
            return {
                "status": "failed",
                "message": "No jobs found."
            }
        
        # Step 2: Save jobs to database
        db = None
        try:
            # Get database connection with retry
            db = self._get_db_connection_with_retry()
            
            # Save jobs
            repository = LeadRepository(db)
            saved_jobs = repository.save_leads(jobs)
            
            logger.info(f"Successfully saved {saved_jobs} jobs out of {len(jobs)}")
            
            return {
                "status": "success",
                "scraped_jobs": len(jobs),
                "saved_jobs": saved_jobs
            }
            
        except Exception as e:
            logger.error(f"Database operation failed: {e}", exc_info=True)
            return {
                "status": "failed",
                "message": f"Database error: {str(e)}"
            }
            
        finally:
            # Always close database connection
            if db:
                try:
                    db.close()
                    logger.debug("Database connection closed")
                except Exception as e:
                    logger.warning(f"Error closing database connection: {e}")    






    