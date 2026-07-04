from dotenv import load_dotenv 
load_dotenv() 

import os

# ==========================================================
# Apify Configuration
# ==========================================================

APIFY_TOKEN = os.getenv("APIFY_TOKEN")
# print(APIFY_TOKEN)
APIFY_BASE_URL = (
    "/v2/acts/"
    "bebity~linkedin-jobs-scraper/"
    "run-sync-get-dataset-items"
)

APIFY_TIMEOUT = 60


# ==========================================================
# Default Search Configuration
# ==========================================================

DEFAULT_ROWS = 2

DEFAULT_PUBLISHED_AT = "past_24h"

DEFAULT_WORK_TYPE = "remote"
DEFAULT_JOB_TYPE = "any"
ACTOR_ID = "3mtoEZQ0ZpQUWepkd"
EXPERIENCE = "any"