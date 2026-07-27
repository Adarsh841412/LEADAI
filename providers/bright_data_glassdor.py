import requests
import json
from datetime import datetime, timezone 
import time
API_KEY = "4b292b93-e065-4ee0-8cdf-31c0f66bb323"

GLASSDOOR_DATASET_ID = "gd_lpfbbndm1xnopbrcr0"


def trigger_brightdata_job_scrape_glassdoor(job_title: str, country: str, location: str = "Remote"):
    """
    Triggers a Bright Data Glassdoor scrape job.

    Required fields for this dataset: location, keyword, country, date_posted.
    country must be a 2-letter ISO country code (e.g. "US", "FR").

    The response can be:
      a) a single JSON object with a snapshot_id -> still processing, need to poll
      b) multiple JSON objects concatenated by newlines (NDJSON) -> data ready immediately
    """
    url = (
        f"https://api.brightdata.com/datasets/v3/scrape"
        f"?dataset_id={GLASSDOOR_DATASET_ID}&notify=false&include_errors=true"
        f"&type=discover_new&discover_by=keyword&limit_per_input=3"
    )
    payload = {
        "input": [
            {
                "location": location,
                "keyword": job_title,
                "country": country,
                "date_posted": "Last day"
            }
        ],
        "limit_per_input": 3,
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


def get_brightdata_snapshot_status_glassdoor(snapshot_id):
    """
    Checks the status of a running Bright Data Glassdoor job.
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


def wait_for_snapshot_ready_glassdoor(res):
    status = res.get('status')

    if status == 'ready':
        return "ready"
    elif status == 'failed':
        return "failed"
    elif status == 'running':
        return "running"
    else:
        return "wait for 30 sec, then try again"


def get_data_glassdoor(snapshot_id: str):
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


def parse_brightdata_response_glassdoor(raw: str):
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

def run_bright_data_glassdoor(job_title: str, country: str, location: str = "Remote"):
    """
    a) Triggers the scrape.
    b) If the response is already multiple records (list) -> data is ready,
       return it directly, no polling needed.
    c) If the response is a single dict with a snapshot_id -> auto-poll until ready,
       then fetch and return the final data.
    d) Returns a Python object (list[dict] preferably) -- NEVER a raw JSON string.
    """
    raw = trigger_brightdata_job_scrape_glassdoor(job_title, country, location)  # raw: str

    data = parse_brightdata_response_glassdoor(raw)
    if data is None:
        return None

    # Case: multiple records already returned (JSON array or NDJSON) -> done
    if isinstance(data, list):
        print(f"Got {len(data)} records directly, no polling needed.")
        return data

    # Case: single dict -> likely has snapshot_id, needs polling
    if isinstance(data, dict):
        snapshot_id = data.get('snapshot_id', '')

        if not snapshot_id:
            # dict but no snapshot_id -> nothing to poll, return as-is (wrapped in list
            # for consistency with downstream code that expects a list of jobs)
            return [data]

        while True:
            status_raw = get_brightdata_snapshot_status_glassdoor(snapshot_id)
            res = parse_brightdata_response_glassdoor(status_raw)

            if res is None or not isinstance(res, dict):
                print("Failed to parse status response, got:", status_raw)
                time.sleep(10)
                continue

            result = wait_for_snapshot_ready_glassdoor(res)

            if result == "ready":
                print(result)
                scraped = get_data_glassdoor(snapshot_id)  # already parsed (list/dict) or None
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

    # Anything else (int, None, etc.) -- unexpected shape
    print("Unexpected data type from trigger response:", type(data))
    return None




# def convert_brightdata_to_apify_glassdoor(brightdata_data):
#     """
#     Convert Bright Data GLASSDOOR job listings to Apify format.
#     Filters out hybrid and on-site jobs - ONLY returns remote jobs.

#     IMPORTANT (confirmed from real Glassdoor sample data):
#     - 'job_location' is the job's ACTUAL city (e.g. "Virginia Beach, VA"),
#       NOT "Remote" -- the "Remote" value only appears in discovery_input.location,
#       which is just the search filter used, not proof the job itself is remote.
#     - Not every result returned for a "Remote" search is actually remote (e.g.
#       some explicitly require an in-person interview) -- keyword-based rejection
#       on job_overview/job_title is still required as a safety net.
#     - Crawl errors show up as inline records like:
#       {'timestamp': ..., 'input': {...}, 'error': 'Crawl aborted on job cancel',
#        'error_code': 'aborted_page'} -- these must be skipped, not treated as jobs.

#     Args:
#         brightdata_data (list): List of job dicts from Bright Data (Glassdoor dataset)

#     Returns:
#         list: List of jobs in Apify format (ONLY remote jobs)
#     """
#     if not brightdata_data:
#         return []

#     remote_keywords = [
#         'remote', 'work from home', 'wfh', 'telecommute', 'telework',
#         'fully remote', '100% remote', 'completely remote', 'entirely remote',
#         'anywhere', 'location independent', 'global', 'worldwide',
#         'distributed', 'home office', 'work at home', 'wah',
#         'remote-first', 'remote friendly', 'remote allowed',
#         'digital nomad', 'virtual office', 'off-site'
#     ]

#     reject_keywords = [
#         'hybrid', 'on-site', 'on site', 'in-office', 'in office',
#         'in person', 'in-person', 'office-based', 'office based',
#         'partially remote', 'some remote',
#         'relocation', 'travel to work', 'must relocate',
#         'only on w2', 'only w2', 'independent visa',
#         'need independent visa', 'only independent',
#         'requires an in-person interview'
#     ]

#     apify_jobs = []

#     for job in brightdata_data:
#         # Skip crawl-error / aborted-page records entirely - only clean, valid jobs wanted
#         if 'error' in job or 'error_code' in job:
#             continue

#         # Skip anything without a real job_title (defensive)
#         if not job.get('job_title'):
#             continue

#         # ------------------------------------------------------------
#         # EXTRACT TEXT FOR CHECKING (real Glassdoor field names)
#         # ------------------------------------------------------------
#         job_location = (job.get('job_location') or '').lower()
#         job_title = (job.get('job_title') or '').lower()
#         job_description = (job.get('job_overview') or '').lower()

#         discovery_input = job.get('discovery_input', {}) or {}
#         discovery_location = (discovery_input.get('location', '') or '').lower()
#         discovery_keyword = (discovery_input.get('keyword', '') or '').lower()

#         full_text = f"{job_location} {job_title} {job_description} {discovery_location} {discovery_keyword}"

#         # STEP 1: REJECT if any reject keyword exists (e.g. in-person interview required)
#         is_rejected = any(keyword in full_text for keyword in reject_keywords)
#         if is_rejected:
#             continue

#         # STEP 2: CHECK if remote -- rely on keyword match in title/description,
#         # since job_location itself is a real city, not "Remote"
#         is_remote = False
#         matched_keyword = None
#         for keyword in remote_keywords:
#             if keyword in full_text:
#                 is_remote = True
#                 matched_keyword = keyword
#                 break

#         if not is_remote:
#             continue

#         # ------------------------------------------------------------
#         # BUILD JOB OBJECT (only for remote jobs)
#         # ------------------------------------------------------------
#         company_website = job.get('company_website', '') or ''
#         company_domain = None
#         if company_website:
#             domain = company_website.split('//')[-1].split('/')[0]
#             company_domain = domain.replace('www.', '') if domain else None

#         apify_job = {
#             "jobId": job.get("job_posting_id", ""),
#             "title": job.get("job_title", ""),
#             "jobUrl": (job.get("url", "") or "").replace("?_l=en", ""),

#             # Standard fields
#             "skills": [],
#             "logoUrl": None,
#             "applyUrl": job.get("job_application_link"),
#             "benefits": job.get("employee_benefit_reviews", []),

#             "isRemote": True,
#             "location": "Remote",                  # Keep consistent with Indeed output
#             "platform": "glassdoor_bright_data",
#             "isExpired": False,

#             "recruiter": {
#                 "name": None,
#                 "title": None,
#                 "linkedinUrl": None,
#                 "emailGuesses": [],
#                 "emailConfidence": "none",
#             },

#             "scrapedAt": job.get("timestamp"),
#             "datePosted": None,                    # Glassdoor doesn't expose posting timestamp

#             "companyName": job.get("company_name"),
#             "description": job.get("job_overview"),

#             "remoteStatus": "Remote",

#             "reviewsCount": None,                  # Not available in dataset

#             "companyDomain": company_domain,
#             "companyRating": job.get("company_rating"),

#             "employmentType": None,                # Not available
#             "experienceLevel": None,               # Not available

#             "discovery_input": discovery_input,

#             "_matched_keyword": matched_keyword,

#             "companyLinkedinUrl": None,

#             # -------------------------------
#             # Extra Glassdoor fields (optional)
#             # -------------------------------
#             "companyCEO": job.get("company_ceo"),
#             "companyIndustry": job.get("company_industry"),
#             "companySector": job.get("company_sector"),
#             "companySize": job.get("company_size"),
#             "companyHeadquarters": job.get("company_headquarters"),

#             "payRangeEstimate": (
#                 job.get("pay_range_glassdoor_est")
#                 or job.get("pay_range_Employer_est")
#             ),

#             "payMedian": (
#                 job.get("pay_median_glassdoor")
#                 or job.get("pay_median_employer")
#             ),

#             "payType": job.get("pay_type"),
#         }

#         apify_jobs.append(apify_job)

#     return apify_jobs

def convert_brightdata_to_apify_glassdoor(brightdata_data):
    """
    Convert Bright Data Glassdoor dataset into the common Apify job format.
    Returns ONLY remote jobs.
    """
    if not brightdata_data:
        return []

    # Keywords that indicate a REMOTE job
    remote_keywords = [
        "remote",
        "fully remote",
        "100% remote",
        "completely remote",
        "entirely remote",
        "remote-first",
        "remote first",
        "remote friendly",
        "remote-friendly",
        "remote allowed",
        "location type remote",
        "location: remote",
        "virtual",
        "work from home",
        "work at home",
        "home office",
        "distributed",
        "anywhere",
        "worldwide",
        "global",
        "wfh",
        "wah",
        "telework",
        "telecommute",
        "remote work",
        "remote position",
        "remote opportunity",
        "remote role",
        "remote job",
        "remote us",
        "remote united states",
        "remote only",
        "fully remote position",
        "this is a remote role",
        "this position is remote",
        "remote work opportunities",
    ]

    # Keywords that indicate NOT REMOTE
    reject_keywords = [
        "hybrid schedule",
        "hybrid role",
        "hybrid work",
        "hybrid remote",
        "on-site required",
        "on-site position",
        "in-office required",
        "in-office position",
        "must work in office",
    ]

    apify_jobs = []

    for job in brightdata_data:
        # Skip crawl error records
        if job.get("error") or job.get("error_code"):
            continue

        if not job.get("job_title"):
            continue

        # Get all text fields
        job_location = (job.get("job_location") or "").lower()
        job_title = (job.get("job_title") or "").lower()
        job_description = (job.get("job_overview") or "").lower()
        
        # Check if location itself says remote
        is_location_remote = (
            "remote" in job_location or 
            job_location == "united states" or
            job_location == "usa" or
            job_location == "us" or
            "anywhere" in job_location
        )

        # Combine text for checking
        combined_text = f"{job_title} {job_description} {job_location}"

        # Check for REJECT keywords
        is_clearly_not_remote = False
        
        # Check for strong hybrid indicators
        if "hybrid" in combined_text:
            if "hybrid remote" in combined_text or "remote hybrid" in combined_text:
                is_clearly_not_remote = False
            elif "hybrid schedule" in combined_text or "hybrid role" in combined_text:
                is_clearly_not_remote = True
        
        # Check for strong on-site indicators
        if "on-site" in combined_text or "on site" in combined_text:
            if "remote" in combined_text:
                remote_count = combined_text.count("remote")
                onsite_count = combined_text.count("on-site") + combined_text.count("on site")
                if onsite_count >= remote_count:
                    is_clearly_not_remote = True
            else:
                is_clearly_not_remote = True
        
        if "in-office" in combined_text or "in office" in combined_text:
            if "remote" not in combined_text or combined_text.count("in-office") > combined_text.count("remote"):
                is_clearly_not_remote = True

        if is_clearly_not_remote:
            continue

        # Check if it's a remote job
        is_remote_job = False
        matched_keyword = None
        
        # Check remote keywords
        for keyword in remote_keywords:
            if keyword in combined_text:
                is_remote_job = True
                matched_keyword = keyword
                break
        
        # If location says remote, it's remote
        if not is_remote_job and is_location_remote:
            is_remote_job = True
            matched_keyword = "location_remote"
        
        if not is_remote_job:
            continue

        # Company domain
        company_domain = None
        website = job.get("company_website")
        if website:
            company_domain = (
                website.replace("https://", "")
                .replace("http://", "")
                .replace("www.", "")
                .split("/")[0]
            )

        # Get pay range
        pay_range = (
            job.get("pay_range_glassdoor_est") or 
            job.get("pay_range_Employer_est") or 
            job.get("pay_range_glassdoor") or
            job.get("pay_range")
        )
        
        pay_median = (
            job.get("pay_median_glassdoor") or 
            job.get("pay_median_employer") or
            job.get("pay_median")
        )

        # 🔥 FIX: Set datePosted to today's date for Glassdoor jobs
        # Glassdoor jobs don't have a real datePosted, but they were fetched today
        today = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")
        
        # Or if you want "last day" format
        # today = "last day"

        # Convert to Apify format
        apify_job = {
            "jobId": job.get("job_posting_id", ""),
            "title": job.get("job_title", ""),
            "jobUrl": job.get("url", ""),
            "skills": [],
            "logoUrl": None,
            "applyUrl": job.get("job_application_link"),
            "benefits": job.get("employee_benefit_reviews", []),
            "isRemote": True,
            "remoteStatus": "Remote",
            "location": "Remote",
            "platform": "glassdoor_bright_data",
            "isExpired": False,
            "recruiter": {
                "name": None,
                "title": None,
                "linkedinUrl": None,
                "emailGuesses": [],
                "emailConfidence": "none",
            },
            "scrapedAt": job.get("timestamp"),
            "datePosted": today,  # 🔥 Set to today's date
            "companyName": job.get("company_name"),
            "description": job.get("job_overview"),
            "reviewsCount": None,
            "companyDomain": company_domain,
            "companyRating": job.get("company_rating"),
            "companyCEO": job.get("company_ceo"),
            "companyIndustry": job.get("company_industry"),
            "companySector": job.get("company_sector"),
            "companySize": job.get("company_size"),
            "companyHeadquarters": job.get("company_headquarters"),
            "employmentType": None,
            "experienceLevel": None,
            "companyLinkedinUrl": None,
            "payRangeEstimate": pay_range,
            "payMedian": pay_median,
            "payType": job.get("pay_type"),
            "discovery_input": job.get("discovery_input", {}),
            "_matched_keyword": matched_keyword,
        }

        apify_jobs.append(apify_job)

    return apify_jobs