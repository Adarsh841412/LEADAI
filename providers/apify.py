from typing import Any
from apify_client import ApifyClient
import requests
from providers.bright_data import run_bright_data,convert_brightdata_to_apify
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


class ApifyProvider:
    """
    Handles communication with the Apify LinkedIn Jobs Scraper.
    """

    def __init__(self) -> None:
        self.api_token=APIFY_TOKEN
        self.base_url=APIFY_BASE_URL
        self.timeout=APIFY_TIMEOUT


    def _build_payload(
        self,
        job_title: str,
        location: str,
    ) -> dict[str, Any]:
        """
        Build payload for Apify.
        """

        return {
            "searchQuery": job_title,
            "location": location,
            "experienceLevel": EXPERIENCE,
            "jobType": DEFAULT_JOB_TYPE,
            "maxResults": DEFAULT_ROWS,
            "datePosted":DEFAULT_PUBLISHED_AT,
            "remoteOnly": True,
            "includeRecruiterEnrichment": True
        }

    def _send_request(
        self,
        payload: dict[str, Any]
    ):
        """
        Send request to Apify API.
        """
        client = ApifyClient(self.api_token)   
        run_input = payload
        run = client.actor(ACTOR_ID).call(run_input=run_input)
        return run 
        
     
    
    

    def fetch_jobs(
        self,
        job_title: str,
        location: str,
    ) -> list[dict[str, Any]]:
        """
        Fetch jobs from Apify.
        
        """
        while True :
            inp = input("press 1 to get data from apify\npress 2 to get data from bright data\n")
            if inp.strip() in ("1", "2"):
                break
            else :
                print("it is invalid selection try again ")
        
        if inp.strip() == "1":
            payload = self._build_payload(
                job_title=job_title,
                location=location,
            )

            run =  self._send_request(
                payload=payload
            )
            dataset_id = run.default_dataset_id
            dataset_items = []
            client = ApifyClient(self.api_token)   
            for item in client.dataset(dataset_id).iterate_items():
                dataset_items.append(item)
            return dataset_items 
        
        
        # *hanlde bright data 
        elif inp.strip() == "2":
            data = run_bright_data(job_title, location)   # already parsed: list[dict] or dict, NOT a str
    
            if data is None:
                print("No data returned from Bright Data.")
                return []
    
        # normalize to a list of job dicts, since convert_brightdata_to_apify expects a list
        
            if isinstance(data, dict):
                data = [data]          # wrap single dict into a list
            elif not isinstance(data, list):
                print("Unexpected data type:", type(data))
                return []
        
            dataset_items = convert_brightdata_to_apify(data)
            print("scraped by adarsh")
            print(dataset_items)
            return dataset_items
                



            
