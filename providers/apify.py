            
# from typing import Any
# from apify_client import ApifyClient
# import requests
# from providers.bright_data import run_bright_data, convert_brightdata_to_apify
# from providers.bright_data_indded import run_bright_data_indded, convert_brightdata_to_apify_indded
# from providers.bright_data_glassdor import run_bright_data_glassdoor, convert_brightdata_to_apify_glassdoor
# import json
# from config.settings import (
#     APIFY_BASE_URL,
#     APIFY_TIMEOUT,
#     APIFY_TOKEN,
#     DEFAULT_ROWS,
#     DEFAULT_PUBLISHED_AT,
#     EXPERIENCE,
#     ACTOR_ID,
#     DEFAULT_JOB_TYPE
# )
# from api.schemas import Platform


# class Lead_Provider:
#     """
#     Handles communication with the Apify LinkedIn Jobs Scraper.
#     """

#     def __init__(self) -> None:
#         self.api_token = APIFY_TOKEN
#         self.base_url = APIFY_BASE_URL
#         self.timeout = APIFY_TIMEOUT

#     def _build_payload(
#         self,
#         job_title: str,
#         location: str,
#     ) -> dict[str, Any]:
#         """
#         Build payload for Apify.
#         """
#         return {
#             "searchQuery": job_title,
#             "location": location,
#             "experienceLevel": EXPERIENCE,
#             "jobType": DEFAULT_JOB_TYPE,
#             "maxResults": DEFAULT_ROWS,
#             "datePosted": DEFAULT_PUBLISHED_AT,
#             "remoteOnly": True,
#             "includeRecruiterEnrichment": True
#         }

#     def _send_request(
#         self,
#         payload: dict[str, Any]
#     ):
#         """
#         Send request to Apify API.
#         """
#         client = ApifyClient(self.api_token)
#         run_input = payload
#         run = client.actor(ACTOR_ID).call(run_input=run_input)
#         return run

#     def fetch_jobs(
#         self,
#         job_title: str,
#         location: str,
#         platform:str 
#     ) -> list[dict[str, Any]]:
#         """
#         Fetch jobs from Apify.
#         """
    
#         if platform == "apify":
#             payload = self._build_payload(
#                 job_title=job_title,
#                 location=location,
#             )

#             run = self._send_request(
#                 payload=payload
#             )
#             dataset_id = run.default_dataset_id
#             dataset_items = []
#             client = ApifyClient(self.api_token)
#             for item in client.dataset(dataset_id).iterate_items():
#                 dataset_items.append(item)
#             return dataset_items

#         # * handle bright data linkedin

#         elif platform == Platform.LINKEDIN:
#             data = run_bright_data(job_title, location)   # already parsed: list[dict] or dict, NOT a str

#             if data is None:
#                 print("No data returned from Bright Data.")
#                 return []

#             # normalize to a list of job dicts, since convert_brightdata_to_apify expects a list

#             if isinstance(data, dict):
#                 data = [data]          # wrap single dict into a list
#             elif not isinstance(data, list):
#                 print("Unexpected data type:", type(data))
#                 return []

#             dataset_items = convert_brightdata_to_apify(data)
#             return dataset_items

#         # * this is for indeed

#         elif platform == Platform.INDEED:

#             data = run_bright_data_indded(job_title, location)   # already parsed: list[dict] or dict, NOT a str

#             if data is None:
#                 print("No data returned from Bright Data.")
#                 return []

#             # normalize to a list of job dicts, since convert_brightdata_to_apify expects a list

#             if isinstance(data, dict):
#                 data = [data]          # wrap single dict into a list
#             elif not isinstance(data, list):
#                 print("Unexpected data type:", type(data))
#                 return []

#             dataset_items = convert_brightdata_to_apify_indded(data)
#             return dataset_items

#         # * this one for glassdoor

#         elif platform == Platform.GLASSDOOR:
#             try:
#                 print(f"Fetching Glassdoor jobs for: {job_title} in {location}")
#                 data = run_bright_data_glassdoor(job_title, location)
                
#                 if data is None:
#                     print("No data returned from Bright Data.")
#                     return []
                
#                 # Normalize to a list of job dicts
#                 if isinstance(data, dict):
#                     data = [data]  # wrap single dict into a list
#                 elif not isinstance(data, list):
#                     print("Unexpected data type:", type(data))
#                     return []
                
#                 print(f"Converting {len(data)} jobs...")
                
#                 # CONVERT the data
#                 dataset_items = convert_brightdata_to_apify_glassdoor(data)
        
#                 # Return the converted jobs, NOT an empty list or None
#                 if dataset_items:
#                     print(dataset_items)
#                     return dataset_items
#                 else:
#                     print("No remote jobs found after filtering.")
#                     return []  # Return empty list, not None
                    
#             except Exception as e:
#                 print(f"Error in Glassdoor fetch: {e}")
#                 import traceback
#                 traceback.print_exc()
#                 return []



# providers/lead_provider.py
import logging
import time
from typing import Any, List, Dict, Optional, Union
from apify_client import ApifyClient
import requests
from requests.exceptions import RequestException, Timeout, ConnectionError

from providers.bright_data import run_bright_data, convert_brightdata_to_apify
from providers.bright_data_indded import run_bright_data_indded, convert_brightdata_to_apify_indded
from providers.bright_data_glassdor import run_bright_data_glassdoor, convert_brightdata_to_apify_glassdoor
import json
from config.settings import (
    APIFY_BASE_URL,
    APIFY_TIMEOUT,
    APIFY_TOKEN,
    DEFAULT_ROWS,
    DEFAULT_PUBLISHED_AT,
    EXPERIENCE,
    ACTOR_ID,
    DEFAULT_JOB_TYPE
)
from api.schemas import Platform

# Setup logging
logger = logging.getLogger(__name__)


class LeadProviderError(Exception):
    """Base exception for LeadProvider errors."""
    pass


class LeadProviderConnectionError(LeadProviderError):
    """Exception for connection/network errors."""
    pass


class LeadProviderTimeoutError(LeadProviderError):
    """Exception for timeout errors."""
    pass


class LeadProviderDataError(LeadProviderError):
    """Exception for data parsing errors."""
    pass


class LeadProvider:
    """
    Handles communication with various job providers:
    - Apify LinkedIn Jobs Scraper
    - Bright Data (LinkedIn, Indeed, Glassdoor)
    """

    MAX_RETRIES = 3
    RETRY_DELAY = 2  # seconds
    REQUEST_TIMEOUT = 30  # seconds
    
    def __init__(self) -> None:
        """Initialize the LeadProvider with configuration."""
        self.api_token = APIFY_TOKEN
        self.base_url = APIFY_BASE_URL
        self.timeout = APIFY_TIMEOUT or self.REQUEST_TIMEOUT
        
        # Validate token
        if not self.api_token:
            logger.warning("APIFY_TOKEN is not set or empty")
    
    def _build_payload(self, job_title: str, location: str) -> Dict[str, Any]:
        """
        Build payload for Apify.
        
        Args:
            job_title: Job title to search
            location: Location to search
            
        Returns:
            Dictionary with search parameters
        """
        return {
            "searchQuery": job_title.strip(),
            "location": location.strip(),
            "experienceLevel": EXPERIENCE,
            "jobType": DEFAULT_JOB_TYPE,
            "maxResults": DEFAULT_ROWS,
            "datePosted": DEFAULT_PUBLISHED_AT,
            "remoteOnly": True,
            "includeRecruiterEnrichment": True
        }
    
    def _send_request_with_retry(
        self,
        client: ApifyClient,
        actor_id: str,
        payload: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Send request to Apify with retry logic.
        
        Args:
            client: ApifyClient instance
            actor_id: Actor ID to call
            payload: Request payload
            
        Returns:
            Run response dictionary
            
        Raises:
            LeadProviderConnectionError: If connection fails
            LeadProviderTimeoutError: If request times out
            LeadProviderError: For other errors
        """
        last_error = None
        
        for attempt in range(self.MAX_RETRIES):
            try:
                logger.info(f"Calling Apify actor (attempt {attempt + 1}/{self.MAX_RETRIES})")
                
                # Call the actor
                run = client.actor(actor_id).call(run_input=payload)
                
                if run:
                    logger.info(f"Apify actor call successful on attempt {attempt + 1}")
                    return run
                else:
                    raise LeadProviderError("Actor returned empty response")
                
            except Timeout as e:
                last_error = e
                logger.warning(f"Request timeout on attempt {attempt + 1}: {e}")
                
            except ConnectionError as e:
                last_error = e
                logger.warning(f"Connection error on attempt {attempt + 1}: {e}")
                
            except RequestException as e:
                last_error = e
                logger.warning(f"Request error on attempt {attempt + 1}: {e}")
                
            except Exception as e:
                last_error = e
                logger.error(f"Unexpected error on attempt {attempt + 1}: {e}")
            
            # Retry with exponential backoff
            if attempt < self.MAX_RETRIES - 1:
                wait_time = self.RETRY_DELAY * (2 ** attempt)
                logger.info(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
        
        # All retries failed
        if isinstance(last_error, Timeout):
            raise LeadProviderTimeoutError(
                f"Request timed out after {self.MAX_RETRIES} attempts"
            ) from last_error
        elif isinstance(last_error, ConnectionError):
            raise LeadProviderConnectionError(
                f"Connection failed after {self.MAX_RETRIES} attempts: {str(last_error)}"
            ) from last_error
        else:
            raise LeadProviderError(
                f"Failed to call actor after {self.MAX_RETRIES} attempts: {str(last_error)}"
            ) from last_error
    
    def _fetch_apify_jobs(self, job_title: str, location: str) -> List[Dict[str, Any]]:
        """
        Fetch jobs from Apify.
        
        Args:
            job_title: Job title to search
            location: Location to search
            
        Returns:
            List of job dictionaries
            
        Raises:
            LeadProviderError: If fetching fails
        """
        try:
            # Build payload
            payload = self._build_payload(job_title, location)
            logger.info(f"Fetching Apify jobs: {job_title} in {location}")
            
            # Create client
            client = ApifyClient(self.api_token)
            
            # Send request with retry
            run = self._send_request_with_retry(client, ACTOR_ID, payload)
            
            if not run:
                logger.warning("No run response from Apify")
                return []
            
            # Get dataset
            dataset_id = run.get('defaultDatasetId')
            if not dataset_id:
                logger.warning("No dataset ID in run response")
                return []
            
            # Fetch items from dataset
            dataset_items = []
            try:
                for item in client.dataset(dataset_id).iterate_items():
                    dataset_items.append(item)
                
                logger.info(f"Fetched {len(dataset_items)} jobs from Apify")
                return dataset_items
                
            except Exception as e:
                logger.error(f"Error iterating dataset: {e}", exc_info=True)
                raise LeadProviderDataError(f"Failed to fetch dataset items: {str(e)}") from e
                
        except LeadProviderError:
            # Re-raise provider-specific errors
            raise
            
        except Exception as e:
            logger.error(f"Unexpected error fetching Apify jobs: {e}", exc_info=True)
            raise LeadProviderError(f"Apify fetch failed: {str(e)}") from e
    
    def _normalize_brightdata_response(
        self,
        data: Any,
        platform: str
    ) -> List[Dict[str, Any]]:
        """
        Normalize Bright Data response to a list of dictionaries.
        
        Args:
            data: Raw data from Bright Data
            platform: Platform name for logging
            
        Returns:
            List of job dictionaries
            
        Raises:
            LeadProviderDataError: If data cannot be normalized
        """
        if data is None:
            logger.warning(f"No data returned from Bright Data ({platform})")
            return []
        
        # Normalize to list
        if isinstance(data, dict):
            logger.debug(f"Converting single dict to list for {platform}")
            return [data]
        elif isinstance(data, list):
            if not data:
                logger.warning(f"Empty list returned from Bright Data ({platform})")
                return []
            logger.info(f"Received {len(data)} items from Bright Data ({platform})")
            return data
        else:
            error_msg = f"Unexpected data type from Bright Data ({platform}): {type(data)}"
            logger.error(error_msg)
            raise LeadProviderDataError(error_msg)
    
    def _fetch_brightdata_linkedin(self, job_title: str, location: str) -> List[Dict[str, Any]]:
        """
        Fetch jobs from Bright Data LinkedIn.
        
        Args:
            job_title: Job title to search
            location: Location to search
            
        Returns:
            List of job dictionaries
        """
        try:
            logger.info(f"Fetching Bright Data LinkedIn jobs: {job_title} in {location}")
            
            # Fetch data
            data = run_bright_data(job_title, location)
            
            # Normalize response
            normalized_data = self._normalize_brightdata_response(data, "LinkedIn")
            
            if not normalized_data:
                return []
            
            # Convert to Apify format
            try:
                converted = convert_brightdata_to_apify(normalized_data)
                logger.info(f"Converted {len(converted)} Bright Data LinkedIn jobs")
                return converted
            except Exception as e:
                logger.error(f"Error converting Bright Data LinkedIn data: {e}", exc_info=True)
                raise LeadProviderDataError(f"Conversion failed: {str(e)}") from e
                
        except LeadProviderError:
            raise
            
        except Exception as e:
            logger.error(f"Unexpected error fetching Bright Data LinkedIn jobs: {e}", exc_info=True)
            raise LeadProviderError(f"Bright Data LinkedIn fetch failed: {str(e)}") from e
    
    def _fetch_brightdata_indeed(self, job_title: str, location: str) -> List[Dict[str, Any]]:
        """
        Fetch jobs from Bright Data Indeed.
        
        Args:
            job_title: Job title to search
            location: Location to search
            
        Returns:
            List of job dictionaries
        """
        try:
            logger.info(f"Fetching Bright Data Indeed jobs: {job_title} in {location}")
            
            # Fetch data
            data = run_bright_data_indded(job_title, location)
            
            # Normalize response
            normalized_data = self._normalize_brightdata_response(data, "Indeed")
            
            if not normalized_data:
                return []
            
            # Convert to Apify format
            try:
                converted = convert_brightdata_to_apify_indded(normalized_data)
                logger.info(f"Converted {len(converted)} Bright Data Indeed jobs")
                return converted
            except Exception as e:
                logger.error(f"Error converting Bright Data Indeed data: {e}", exc_info=True)
                raise LeadProviderDataError(f"Conversion failed: {str(e)}") from e
                
        except LeadProviderError:
            raise
            
        except Exception as e:
            logger.error(f"Unexpected error fetching Bright Data Indeed jobs: {e}", exc_info=True)
            raise LeadProviderError(f"Bright Data Indeed fetch failed: {str(e)}") from e
    
    def _fetch_brightdata_glassdoor(self, job_title: str, location: str) -> List[Dict[str, Any]]:
        """
        Fetch jobs from Bright Data Glassdoor.
        
        Args:
            job_title: Job title to search
            location: Location to search
            
        Returns:
            List of job dictionaries
        """
        try:
            logger.info(f"Fetching Bright Data Glassdoor jobs: {job_title} in {location}")
            
            # Fetch data
            data = run_bright_data_glassdoor(job_title, location)
            
            # Normalize response
            normalized_data = self._normalize_brightdata_response(data, "Glassdoor")
            
            if not normalized_data:
                logger.warning("No Glassdoor jobs found")
                return []
            
            # Convert to Apify format
            try:
                converted = convert_brightdata_to_apify_glassdoor(normalized_data)
                if converted:
                    logger.info(f"Converted {len(converted)} Bright Data Glassdoor jobs")
                    return converted
                else:
                    logger.warning("No remote Glassdoor jobs found after filtering")
                    return []
            except Exception as e:
                logger.error(f"Error converting Bright Data Glassdoor data: {e}", exc_info=True)
                raise LeadProviderDataError(f"Glassdoor conversion failed: {str(e)}") from e
                
        except LeadProviderError:
            raise
            
        except Exception as e:
            logger.error(f"Unexpected error fetching Bright Data Glassdoor jobs: {e}", exc_info=True)
            raise LeadProviderError(f"Bright Data Glassdoor fetch failed: {str(e)}") from e
    
    def fetch_jobs(
        self,
        job_title: str,
        location: str,
        platform: str
    ) -> List[Dict[str, Any]]:
        """
        Fetch jobs from the specified platform.
        
        Args:
            job_title: Job title to search for
            location: Location to search in
            platform: Platform to use (apify, linkedin, indeed, glassdoor)
            
        Returns:
            List of job dictionaries
            
        Raises:
            ValueError: If platform is invalid
            LeadProviderError: If fetching fails
        """
        # Validate inputs
        if not job_title or not job_title.strip():
            raise ValueError("Job title is required")
        
        if not location or not location.strip():
            raise ValueError("Location is required")
        
        if not platform or not platform.strip():
            raise ValueError("Platform is required")
        
        # Clean and normalize inputs
        job_title = job_title.strip()
        location = location.strip()
        platform = platform.strip().lower()
        
        logger.info(f"Fetching jobs: {job_title} in {location} from {platform}")
        
        try:
            # Route to appropriate provider
            if platform == "apify":
                return self._fetch_apify_jobs(job_title, location)
            
            elif platform == Platform.LINKEDIN.value or platform == "linkedin":
                return self._fetch_brightdata_linkedin(job_title, location)
            
            elif platform == Platform.INDEED.value or platform == "indeed":
                return self._fetch_brightdata_indeed(job_title, location)
            
            elif platform == Platform.GLASSDOOR.value or platform == "glassdoor":
                return self._fetch_brightdata_glassdoor(job_title, location)
            
            else:
                error_msg = f"Unsupported platform: {platform}. Must be one of: apify, linkedin, indeed, glassdoor"
                logger.error(error_msg)
                raise ValueError(error_msg)
                
        except (ValueError, LeadProviderError):
            # Re-raise known errors
            raise
            
        except Exception as e:
            logger.error(f"Unexpected error in fetch_jobs: {e}", exc_info=True)
            raise LeadProviderError(f"Failed to fetch jobs from {platform}: {str(e)}") from e
    
    def fetch_jobs_safe(
        self,
        job_title: str,
        location: str,
        platform: str
    ) -> List[Dict[str, Any]]:
        """
        Safe version that never raises exceptions, returns empty list on error.
        
        Args:
            job_title: Job title to search for
            location: Location to search in
            platform: Platform to use
            
        Returns:
            List of job dictionaries (empty on error)
        """
        try:
            return self.fetch_jobs(job_title, location, platform)
        except Exception as e:
            logger.error(f"fetch_jobs_safe caught error: {e}", exc_info=True)
            return []
    
    def get_platforms(self) -> List[str]:
        """
        Get list of supported platforms.
        
        Returns:
            List of platform names
        """
        return ['apify', 'linkedin', 'indeed', 'glassdoor']
    
    def validate_platform(self, platform: str) -> bool:
        """
        Check if platform is supported.
        
        Args:
            platform: Platform name
            
        Returns:
            True if supported, False otherwise
        """
        return platform and platform.strip().lower() in self.get_platforms()