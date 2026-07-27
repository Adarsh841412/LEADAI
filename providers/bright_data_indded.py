import requests
import json
import time
from datetime import datetime


API_KEY = "4b292b93-e065-4ee0-8cdf-31c0f66bb323"

def convert_brightdata_to_apify_indded(brightdata_data):
    """
    Convert Bright Data INDEED job listings to Apify format.
    Filters out hybrid and on-site jobs - ONLY returns remote jobs.

    Args:
        brightdata_data (list): List of job dicts from Bright Data (Indeed dataset)

    Returns:
        list: List of jobs in Apify format (ONLY remote jobs)
    """
    if not brightdata_data:
        return []

    # Remote keywords - ACCEPT these (used as a safety-net check on description text)
    remote_keywords = [
        'remote', 'work from home', 'wfh', 'telecommute', 'telework',
        'fully remote', '100% remote', 'completely remote', 'entirely remote',
        'anywhere', 'location independent', 'global', 'worldwide',
        'distributed', 'home office', 'work at home', 'wah',
        'remote-first', 'remote friendly', 'remote allowed',
        'digital nomad', 'virtual office', 'off-site'
    ]

    # Rejection keywords - if ANY match, SKIP the job
    reject_keywords = [
        'hybrid', 'on-site', 'on site', 'in-office', 'in office',
        'in person', 'in-person', 'office-based', 'office based',
        'partially remote', 'some remote',
        'relocation', 'travel to work', 'must relocate',
        'only on w2', 'only w2', 'independent visa',
        'need independent visa', 'only independent'
    ]

    apify_jobs = []

    for job in brightdata_data:
        # Skip error/status objects that sometimes show up (e.g. {'status': 'failed', ...})
        if 'jobid' not in job and 'job_title' not in job:
            continue

        # ------------------------------------------------------------
        # EXTRACT TEXT FOR CHECKING (Indeed field names)
        # ------------------------------------------------------------
        job_location = (job.get('location') or job.get('job_location') or '').lower()
        job_title = (job.get('job_title', '') or '').lower()
        job_description = (job.get('description_text', '') or job.get('description', '') or '').lower()

        discovery_input = job.get('discovery_input', {}) or {}
        discovery_location = (discovery_input.get('location', '') or '').lower()
        discovery_keyword = (discovery_input.get('keyword_search', '') or '').lower()

        full_text = f"{job_location} {job_title} {job_description} {discovery_location} {discovery_keyword}"

        # ------------------------------------------------------------
        # STEP 1: REJECT if any reject keyword exists
        # ------------------------------------------------------------
        is_rejected = False
        for keyword in reject_keywords:
            if keyword in full_text:
                is_rejected = True
                break
        if is_rejected:
            continue

        # ------------------------------------------------------------
        # STEP 2: CHECK if remote (location field OR keyword match)
        # ------------------------------------------------------------
        is_remote = job_location.strip() == 'remote'
        matched_keyword = 'location=remote' if is_remote else None

        if not is_remote:
            for keyword in remote_keywords:
                if keyword in full_text:
                    is_remote = True
                    matched_keyword = keyword
                    break

        if not is_remote:
            continue

        # ------------------------------------------------------------
        # BUILD JOB OBJECT (only for remote jobs)
        # ------------------------------------------------------------
        company_link = job.get('company_link', '') or ''
        company_domain = None
        if company_link:
            # e.g. https://www.indeed.com/cmp/Cure-Business-Solutions-2?... -> Cure-Business-Solutions-2
            path = company_link.split('?')[0]
            parts = path.rstrip('/').split('/')
            if len(parts) >= 1:
                company_domain = parts[-1]

        apify_job = {
            "jobId": job.get('jobid', ''),
            "title": job.get('job_title', ''),
            "jobUrl": (job.get('url', '') or '').replace('?_l=en', ''),
            "skills": [],
            "applyUrl": None,  # Indeed dataset doesn't provide a direct apply link
            "isRemote": True,
            "remoteStatus": "Remote",
            "location": job.get('location', '') or job.get('job_location', ''),
            "recruiter": {
                "name": None,
                "title": None,
                "linkedinUrl": None,
                "emailGuesses": [],
                "emailConfidence": "none"
            },
            "scrapedAt": job.get('timestamp', ''),
            "datePosted": job.get('date_posted_parsed', '') or job.get('date_posted', ''),
            "companyName": job.get('company_name', ''),
            "description": job.get('description_text', '') or job.get('description', ''),
            "companyDomain": company_domain,
            "employmentType": job.get('job_type', ''),
            "experienceLevel": None,  # Indeed dataset doesn't provide seniority level
            "companyLinkedinUrl": None,
            "platform": 'indeed_bright_data',
            "companyRating": job.get('company_rating'),
            "reviewsCount": job.get('company_reviews_count'),
            "benefits": job.get('benefits', []),
            "isExpired": job.get('is_expired', False),
            "logoUrl": job.get('logo_url'),
            "discovery_input": discovery_input,
            # Extra info for debugging
            "_matched_keyword": matched_keyword
        }

        apify_jobs.append(apify_job)

    return apify_jobs



def get_brightdata_snapshot_status_indded(snapshot_id):
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


def trigger_brightdata_job_scrape_indded(job_title: str, country:str):
    """
    Triggers a Bright Data scrape job.

    The response can be:
      a) a single JSON object with a snapshot_id -> still processing, need to poll
      b) multiple JSON objects concatenated by newlines (NDJSON) -> data ready immediately
    """
    url = "https://api.brightdata.com/datasets/v3/scrape?dataset_id=gd_l4dx9j9sscpvs7no2&type=discover_new&discover_by=keyword&limit_per_input=10"
    payload = {
        "input": [
            {
                "keyword_search": job_title,
                "date_posted": "Last 24 hours",
                "location": 'Remote',
                "country":country,
                "domain":'indeed.com'
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
    
    
def wait_for_snapshot_ready_indded(res):
    status = res.get('status')

    if status == 'ready':
        return "ready"
    elif status == 'failed':
        return "failed"
    elif status == 'running':
        return "running"
    else:
        return "wait for 30 sec, then try again"


def get_data_indded(snapshot_id: str):
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


def parse_brightdata_response_indded(raw: str):
    
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






def run_bright_data_indded(job_title: str, country: str):
    """
    a) Triggers the scrape.
    b) If the response is already multiple records (list) -> data is ready,
       return it directly, no polling needed.
    c) If the response is a single dict with a snapshot_id -> auto-poll until ready,
       then fetch and return the final data.
    d) Returns a Python object (list[dict] preferably) -- NEVER a raw JSON string.
    """
    raw = trigger_brightdata_job_scrape_indded(job_title, country)  # raw: str

    data = parse_brightdata_response_indded(raw)
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
            return [data]

        while True:
            status_raw = get_brightdata_snapshot_status_indded(snapshot_id)
            res = parse_brightdata_response_indded(status_raw)

            if res is None or not isinstance(res, dict):
                print("Failed to parse status response, got:", status_raw)
                time.sleep(10)
                continue

            result = wait_for_snapshot_ready_indded(res)

            if result == "ready":
                print(result)
                scraped = get_data_indded(snapshot_id)  # already parsed (list/dict) or None
                if scraped is not None:
                    print("Number of jobs:", len(scraped))
                    if isinstance(scraped, dict):
                        scraped = [scraped]
                    return scraped
                print("Fetch failed after snapshot was ready.")
                return None

            elif result == "failed":
                print("Snapshot failed. Try another location/keyword.")
                break

            else:
                print(result)
                time.sleep(10)

        return None

    print("Unexpected data type from trigger response:", type(data))
    return None

# def run_bright_data_indded(job_title: str,country:str):
    
    
#     """
#     a) Triggers the scrape.
#     b) If the response is already multiple records (list) -> data is ready,
#        return it directly, no polling needed.
#     c) If the response is a single dict with a snapshot_id -> poll until ready,
#        then fetch and return the final data.
#     d) Returns a Python object (list[dict] preferably) -- NEVER a raw JSON string.
#     """
    
#     raw = trigger_brightdata_job_scrape_indded(job_title,country)  # raw: str

#     data = parse_brightdata_response_indded(raw)
#     if data is None:
#         return None 
    
    
#     # Case: multiple records already returned (JSON array or NDJSON) -> done
#     if isinstance(data, list):
#         print(f"Got {len(data)} records directly, no polling needed.")
#         return data

#     # Case: single dict -> likely has snapshot_id, needs polling
#     if isinstance(data, dict):
#         snapshot_id = data.get('snapshot_id')

#         if not snapshot_id:
#             # dict but no snapshot_id -> nothing to poll, return as-is (wrapped in list
#             # for consistency with downstream code that expects a list of jobs)
#             return [data]

#         while True:
#             check = input('Enter 1 to check status, enter 2 to break: ')

#             if check.strip() == "1":
#                 status_raw = get_brightdata_snapshot_status_indded(snapshot_id)
#                 res = parse_brightdata_response_indded(status_raw)
#                 if res is None or not isinstance(res, dict):
#                     print("Failed to parse status response, got:", status_raw)
#                     continue

#                 result = wait_for_snapshot_ready_indded(res)

#                 if result == "ready":
#                     print(result)
#                     scraped = get_data_indded(snapshot_id)  # already parsed (list/dict) or None
#                     print("Number of jobs:", len(scraped))  
#                     if scraped is not None:
#                         print("scraped by adarsh")
#                         if isinstance(scraped, dict):
#                             scraped = [scraped]
#                         return scraped
#                     break  # fetch failed, stop looping
#                 elif result == "failed":
#                     print("Snapshot failed. Try another location/keyword.")
#                     break
#                 else:
#                     print(result)  
#             else:
#                 break

#         return None

#     # Anything else (int, None, etc.) -- unexpected shape
#     print("Unexpected data type from trigger response:", type(data))
#     return None



















# def convert_brightdata_to_apify_indded(brightdata_data):
#     """
#     Convert Bright Data Indeed job listings to Apify format.
#     """
#     if not brightdata_data:
#         return []
    
#     remote_keywords = ['remote', 'work from home', 'wfh', 'telecommute', 'fully remote', '100% remote']
#     reject_keywords = ['hybrid', 'on-site', 'on site', 'in-office', 'in office']
    
#     apify_jobs = []
    
#     for job in brightdata_data:
#         # Indeed uses different field names
#         job_location = (job.get('job_location', '') or job.get('location', '') or '').lower()
#         job_title = (job.get('job_title', '') or '').lower()
#         job_description = (job.get('description_text', '') or job.get('description', '') or job.get('job_description_formatted', '') or '').lower()
        
#         full_text = f"{job_location} {job_title} {job_description}"
        
#         # Check for rejection keywords
#         is_rejected = False
#         for keyword in reject_keywords:
#             if keyword in full_text:
#                 is_rejected = True
#                 break
        
#         if is_rejected:
#             continue
        
#         # Check for remote keywords
#         is_remote = False
#         for keyword in remote_keywords:
#             if keyword in full_text:
#                 is_remote = True
#                 break
        
#         if not is_remote:
#             continue
        
#         # Build job object with Indeed fields
#         apify_job = {
#             "jobId": job.get('jobid', ''),  # ✅ Indeed uses 'jobid'
#             "title": job.get('job_title', ''),
#             "jobUrl": job.get('url', ''),
#             "skills": [],
#             "applyUrl": job.get('apply_link', ''),
#             "isRemote": True,
#             "remoteStatus": "Remote",
#             "location": job.get('job_location', '') or job.get('location', ''),
#             "recruiter": {  # ✅ Indeed doesn't have recruiter info
#                 "name": None,
#                 "title": None,
#                 "linkedinUrl": None,
#                 "emailGuesses": [],
#                 "emailConfidence": "none"
#             },
#             "scrapedAt": datetime.now().isoformat(),
#             "datePosted": job.get('date_posted_parsed', ''),  # ✅ Indeed uses 'date_posted_parsed'
#             "companyName": job.get('company_name', ''),
#             "description": job.get('description_text', '') or job.get('job_description_formatted', ''),
#             "companyDomain": extract_domain_indeed(job.get('company_link', '')),
#             "employmentType": job.get('job_type', ''),  # ✅ Indeed uses 'job_type'
#             "experienceLevel": None,  # ✅ Indeed doesn't have this
#             "companyLinkedinUrl": None,
#             "platform": 'indeed_bright_data',
#             "companyRating": job.get('company_rating'),  # ✅ Indeed has rating
#             "reviewsCount": job.get('company_reviews_count'),  # ✅ Indeed has reviews
#             "benefits": job.get('benefits', []),  # ✅ Indeed has benefits
#             "region": job.get('region', ''),  # ✅ Indeed has region
#             "isExpired": job.get('is_expired', False),  # ✅ Indeed has expiry flag
#             "logoUrl": job.get('logo_url', ''),  # ✅ Indeed has logo
#             "source": "indeed"
#         }
        
#         apify_jobs.append(apify_job)
    
#     return apify_jobs

# def extract_domain_indeed(company_link):
#     """Extract domain from Indeed company link."""
#     if not company_link:
#         return None
#     # Example: https://fr.indeed.com/cmp/Arianegroup -> Arianegroup
#     parts = company_link.rstrip('/').split('/')
#     return parts[-1] if parts else None