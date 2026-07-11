# import requests
# import json
# import time
# # Failed to parse trigger
# # API_KEY = "e36fbab6-ecee-4530-8db5-58addec70951"  # BUG: your trigger function was using a DIFFERENT key (4b292b93...) than the rest. Must be consistent.

# import json
# from datetime import datetime

# def convert_brightdata_to_apify(brightdata_data):
#     """
#     Convert Bright Data job listings to Apify format.
    
#     Args:
#         brightdata_data (list): List of job objects from Bright Data
        
#     Returns:
#         list: List of jobs in Apify format
#     """
#     apify_jobs = []
    
#     for job in brightdata_data:
#         # Extract recruiter/poster information
#         poster = job.get('job_poster', {})
#         if poster:
#             recruiter_name = poster.get('name')
#             recruiter_title = poster.get('title')
#             recruiter_url = poster.get('url')
#         else:
#             recruiter_name = None
#             recruiter_title = None
#             recruiter_url = None
        
#         # Determine if remote (check description and job location)
#         is_remote = False
#         job_location = job.get('job_location', '')
#         job_summary = job.get('job_summary', '').lower()
        
#         # Check if remote is mentioned in location or description
#         if 'remote' in job_location.lower() or 'remote' in job_summary:
#             is_remote = True
        
#         # Extract company domain from company URL or logo URL
#         company_url = job.get('company_url', '')
#         company_domain = None
#         if company_url:
#             # Extract domain from LinkedIn company URL
#             # Example: https://www.linkedin.com/company/linksoft-technologies/
#             parts = company_url.rstrip('/').split('/')
#             if len(parts) >= 2:
#                 company_domain = parts[-1]  # Gets the company handle
        
#         # Build the Apify format job object
#         apify_job = {
#             "jobId": job.get('job_posting_id', ''),
#             "title": job.get('job_title', ''),
#             "jobUrl": job.get('url', '').replace('?_l=en', ''),  # Clean up URL
#             "skills": [],  # Bright Data doesn't extract skills separately
#             "applyUrl": job.get('apply_link'),
#             "isRemote": is_remote,
#             "location": job.get('job_location', ''),
#             "recruiter": {
#                 "name": recruiter_name,
#                 "title": recruiter_title,
#                 "linkedinUrl": recruiter_url,
#                 "emailGuesses": [],  # Not available from Bright Data
#                 "emailConfidence": "none"  # Default value
#             },
#             "scrapedAt": job.get('timestamp', ''),
#             "datePosted": job.get('job_posted_date', ''),
#             "companyName": job.get('company_name', ''),
#             "description": job.get('job_summary', ''),
#             "companyDomain": company_domain,
#             "employmentType": job.get('job_employment_type', ''),
#             "experienceLevel": job.get('job_seniority_level', ''),
#             "companyLinkedinUrl": job.get('company_url', '')
#         }
        
#         apify_jobs.append(apify_job)
    
#     return apify_jobs







# def get_brightdata_snapshot_status(snapshot_id):
#     """
#     checks the status of a bright data running job
#     """
#     # BUG: url was hardcoded to a fixed snapshot_id instead of using the parameter passed in
#     url = f"https://api.brightdata.com/datasets/v3/progress/{snapshot_id}"

#     headers = {"Authorization": f"Bearer 4b292b93-e065-4ee0-8cdf-31c0f66bb323"}

#     try:
#         response = requests.get(url, headers=headers)
#         response.raise_for_status()
#         return response.text
#     except requests.exceptions.RequestException as e:
#         print(f"Error checking snapshot status: {e}")
#         return json.dumps({"status": "error", "error": str(e)})


# def trigger_brightdata_job_scrape(job_title:str,location:str):
#     """
#     if the response.text dict with snapshot id that means still you didn't get the actual data, meaning it's still fetching, so
#     a) first check get_brightdata_snapshot_status
#     b) if status is ready that means data fetching is done and you get the data, get_data_by_snapshot_id function
#     c) if status is running that means it's still fetching
#     d) if status is failed, go back try for another location
#     """

 
#     url = "https://api.brightdata.com/datasets/v3/scrape?dataset_id=gd_lpfll7v5hcqtkxl6l&type=discover_new&discover_by=keyword&limit_per_input=20"
#     payload = {
#         "input": [
#             {
#                 "keyword": job_title,
#                 "time_range": "Past 24 hours",
#                 "remote": "Remote",
#                 "location": location
#             }
#         ],
#     }

#     headers = {
#         "Authorization": "Bearer 4b292b93-e065-4ee0-8cdf-31c0f66bb323",
#         "Content-Type": "application/json"
#     }

#     try:
#         response = requests.post(url, json=payload, headers=headers)
#         response.raise_for_status()
#         return response.text
#     except requests.exceptions.RequestException as e:
#         print(f"Error triggering scrape: {e}")
#         return json.dumps({"error": str(e)})


# def wait_for_snapshot_ready(res):

#     status = res.get('status')

#     if status == 'ready':
#         return "ready"
#     elif status == 'failed':
#         return "failed"
#     elif status == 'running':
#         return "running"
#     else:
#         return "wait for 30 sec, then try again"


# def get_data(snapshot_id: str):
#     """
#     return all the lead data
#     """
#     url = f"https://api.brightdata.com/datasets/v3/snapshot/{snapshot_id}?format=json"

#     headers = {"Authorization": f"Bearer 4b292b93-e065-4ee0-8cdf-31c0f66bb323"}

#     try:
#         response = requests.get(url, headers=headers, timeout=30)
#         print(response.status_code)
#         response.raise_for_status()
#         jobs = response.json()
#         data = json.dumps(jobs, indent=2)
#         return data
#     except requests.exceptions.RequestException as e:
#         print(f"Error fetching data: {e}")
#         return None
#     except json.JSONDecodeError as e:
#         print(f"Error parsing response JSON: {e}")
#         return None


# def run_bright_data(job_title:str,location:str):
#     """
#     a) first it scrapes data
#     b) then check status of data
#     c) after checking status if ready then it will get the data
#     d) return that data that it gets
#     e) else return data directly
#     """

#     raw = trigger_brightdata_job_scrape(job_title,location)
  

#     try:
#         data = json.loads(raw)
#         print('adarsh')
#         print(type(data))
#     except json.JSONDecodeError:
#         print("Failed to parse trigger response, got:", raw)
#         return None

#     if data.get('snapshot_id'):
#         snapshot_id = data.get('snapshot_id')
  
#         while True:
#             snapshot_id=snapshot_id
#             check = input('Enter 1 to check status, enter 2 to break: ')

#             if check.strip() == "1":
#                 # see an updated status. Now it re-fetches status on every check.
#                 status_raw = get_brightdata_snapshot_status(snapshot_id)
#                 try:
#                     res = json.loads(status_raw)
#                 except json.JSONDecodeError:
#                     print("Failed to parse status response, got:", status_raw)
#                     continue

#                 result = wait_for_snapshot_ready(res)

#                 if result == "ready":
#                     print(result)
#                     scraped = get_data(snapshot_id)
#                     if scraped:
#                         print("screaped by adarsh")
#                         # print(scraped)
#                         return scraped 
#                     break  # stop looping once data is retrieved
#                 elif result == "failed":
#                     print("Snapshot failed. Try another location/keyword.")
#                     break
#                 else:
#                     print(result)  # "running" or "wait for 30 sec, then try again"

#             else:
#                 break
#     else:
#         return data
    




import requests
import json
import time
from datetime import datetime

# NOTE: move this to an environment variable in production, e.g.:
#   API_KEY = os.environ["BRIGHTDATA_API_KEY"]
API_KEY = "4b292b93-e065-4ee0-8cdf-31c0f66bb323"


def convert_brightdata_to_apify(brightdata_data):
    """
    Convert Bright Data job listings to Apify format.

    Args:
        brightdata_data (list): List of job dicts from Bright Data

    Returns:
        list: List of jobs in Apify format
    """
    apify_jobs = []

    for job in brightdata_data:
        # Extract recruiter/poster information
        poster = job.get('job_poster') or {}
        recruiter_name = poster.get('name')
        recruiter_title = poster.get('title')
        recruiter_url = poster.get('url')

        # Determine if remote (check description and job location)
        job_location = job.get('job_location', '') or ''
        job_summary = (job.get('job_summary', '') or '').lower()
        is_remote = 'remote' in job_location.lower() or 'remote' in job_summary

        # Extract company domain from company URL
        company_url = job.get('company_url', '') or ''
        company_domain = None
        if company_url:
            parts = company_url.rstrip('/').split('/')
            if len(parts) >= 2:
                company_domain = parts[-1]  # company handle from LinkedIn URL

        apify_job = {
            "jobId": job.get('job_posting_id', ''),
            "title": job.get('job_title', ''),
            "jobUrl": (job.get('url', '') or '').replace('?_l=en', ''),
            "skills": [],  # Bright Data doesn't extract skills separately
            "applyUrl": job.get('apply_link'),
            "isRemote": is_remote,
            "location": job.get('job_location', ''),
            "recruiter": {
                "name": recruiter_name,
                "title": recruiter_title,
                "linkedinUrl": recruiter_url,
                "emailGuesses": [],
                "emailConfidence": "none"
            },
            "scrapedAt": job.get('timestamp', ''),
            "datePosted": job.get('job_posted_date', ''),
            "companyName": job.get('company_name', ''),
            "description": job.get('job_summary', ''),
            "companyDomain": company_domain,
            "employmentType": job.get('job_employment_type', ''),
            "experienceLevel": job.get('job_seniority_level', ''),
            "companyLinkedinUrl": job.get('company_url', ''),
            "platform":'bright_data'
        }

        apify_jobs.append(apify_job)

    return apify_jobs


def get_brightdata_snapshot_status(snapshot_id):
    """
    Checks the status of a running Bright Data job.
    """
    url = f"https://api.brightdata.com/datasets/v3/progress/{snapshot_id}"
    headers = {"Authorization": f"Bearer {API_KEY}"}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error checking snapshot status: {e}")
        return json.dumps({"status": "error", "error": str(e)})


def trigger_brightdata_job_scrape(job_title: str, location: str):
    """
    Triggers a Bright Data scrape job.

    The response can be:
      a) a single JSON object with a snapshot_id -> still processing, need to poll
      b) multiple JSON objects concatenated by newlines (NDJSON) -> data ready immediately
    """
    url = "https://api.brightdata.com/datasets/v3/scrape?dataset_id=gd_lpfll7v5hcqtkxl6l&type=discover_new&discover_by=keyword&limit_per_input=20"
    payload = {
        "input": [
            {
                "keyword": job_title,
                "time_range": "Past 24 hours",
                "remote": "Remote",
                "location": location
            }
        ],
    }
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error triggering scrape: {e}")
        return json.dumps({"error": str(e)})


def wait_for_snapshot_ready(res):
    status = res.get('status')

    if status == 'ready':
        return "ready"
    elif status == 'failed':
        return "failed"
    elif status == 'running':
        return "running"
    else:
        return "wait for 30 sec, then try again"


def get_data(snapshot_id: str):
    """
    Returns all lead data for a completed snapshot, already parsed
    (list[dict] or dict) -- NOT a JSON string.
    """
    url = f"https://api.brightdata.com/datasets/v3/snapshot/{snapshot_id}?format=json"
    headers = {"Authorization": f"Bearer {API_KEY}"}

    try:
        response = requests.get(url, headers=headers, timeout=30)
        print(response.status_code)
        response.raise_for_status()
        jobs = response.json()  # already a Python object (list/dict)
        return jobs
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error parsing response JSON: {e}")
        return None


def parse_brightdata_response(raw: str):
    """
    raw is always a str. It can be:
      a) a single JSON object   -> {"snapshot_id": "..."}
      b) a JSON array           -> [{...}, {...}, ...]
      c) NDJSON (line-delimited)-> {...}\\n{...}\\n{...}   <- multiple dicts as one string

    Returns a Python dict or list[dict], or None on total failure.
    Never returns a string.
    """
    if raw is None:
        return None

    raw = raw.strip()
    if not raw:
        print("Empty response.")
        return None

    # 1) Try standard JSON first (covers single dict AND a proper JSON array)
    try:
        data = json.loads(raw)
        # handle double-encoded JSON (string containing JSON, not yet dict/list)
        if isinstance(data, str):
            data = json.loads(data)
        return data
    except json.JSONDecodeError:
        pass  # fall through to NDJSON handling

    # 2) Fall back: NDJSON / line-delimited multiple dicts
    records = []
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            print("Skipping unparseable line:", line[:200])

    if records:
        print(f"Parsed {len(records)} records from NDJSON.")
        return records

    print("Failed to parse trigger response, got:", raw[:500])
    return None


def run_bright_data(job_title: str, location: str):
    """
    a) Triggers the scrape.
    b) If the response is already multiple records (list) -> data is ready,
       return it directly, no polling needed.
    c) If the response is a single dict with a snapshot_id -> poll until ready,
       then fetch and return the final data.
    d) Returns a Python object (list[dict] preferably) -- NEVER a raw JSON string.
    """
    raw = trigger_brightdata_job_scrape(job_title, location)  # raw: str
    # print("Adarsh kumar dubey")
    # print(raw)

    data = parse_brightdata_response(raw)
    if data is None:
        return None

    # Case: multiple records already returned (JSON array or NDJSON) -> done
    if isinstance(data, list):
        print(f"Got {len(data)} records directly, no polling needed.")
        return data

    # Case: single dict -> likely has snapshot_id, needs polling
    if isinstance(data, dict):
        snapshot_id = data.get('snapshot_id')

        if not snapshot_id:
            # dict but no snapshot_id -> nothing to poll, return as-is (wrapped in list
            # for consistency with downstream code that expects a list of jobs)
            return [data]

        while True:
            check = input('Enter 1 to check status, enter 2 to break: ')

            if check.strip() == "1":
                status_raw = get_brightdata_snapshot_status(snapshot_id)
                res = parse_brightdata_response(status_raw)
                if res is None or not isinstance(res, dict):
                    print("Failed to parse status response, got:", status_raw)
                    continue

                result = wait_for_snapshot_ready(res)

                if result == "ready":
                    print(result)
                    scraped = get_data(snapshot_id)  # already parsed (list/dict) or None
                    if scraped is not None:
                        print("scraped by adarsh")
                        if isinstance(scraped, dict):
                            scraped = [scraped]
                        return scraped
                    break  # fetch failed, stop looping
                elif result == "failed":
                    print("Snapshot failed. Try another location/keyword.")
                    break
                else:
                    print(result)  # "running" or "wait for 30 sec, then try again"
            else:
                break

        return None

    # Anything else (int, None, etc.) -- unexpected shape
    print("Unexpected data type from trigger response:", type(data))
    return None


