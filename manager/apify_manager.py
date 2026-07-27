import os 
from dotenv import load_dotenv 
load_dotenv() 
import requests 
APIFY_TOKENS = os.getenv('APIFY_TOKENS')
class ApifyManager:
    APIFY_BASE_URL = "https://api.apify.com/v2/users/me/limits"

    def __init__(self):
        self.api_keys = self._load_keys()

    def _load_keys(self):
        """
        Load all Apify API keys from the .env file.

        Example:
        APIFY_TOKENS=token1,token2,token3
        """
        if not APIFY_TOKENS:
            raise ValueError("APIFY_TOKENS not found in .env")

        return [key.strip() for key in APIFY_TOKENS.split(",") if key.strip()]

    def _check_key(self, api_key: str) -> dict:
        """
        Check a single Apify API key and return its usage details.
        """
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {api_key}",
        }

        response = requests.get(self.APIFY_BASE_URL, headers=headers)
        response.raise_for_status()

        data = response.json()["data"]

        monthly_limit = data["limits"]["maxMonthlyUsageUsd"]
        monthly_used = data["current"]["monthlyUsageUsd"]
        remaining_credit = monthly_limit - monthly_used

        return {
            "api_key": api_key,
            "monthly_limit": monthly_limit,
            "used_credit": round(monthly_used, 4),
            "remaining_credit": round(remaining_credit, 4),
            "usage_percentage": round((monthly_used / monthly_limit) * 100, 2),
            "cycle_start": data["monthlyUsageCycle"]["startAt"],
            "cycle_end": data["monthlyUsageCycle"]["endAt"],
        }

    def check_all_keys(self):
        """
        Check all configured API keys.
        """
        results = []

        for key in self.api_keys:
            try:
                results.append(self._check_key(key))
            except requests.HTTPError as e:
                results.append(
                    {
                        "api_key": key,
                        "error": str(e),
                    }
                )

        return results
        
        
    def get_best_key(self, min_remaining_credit: float = 1.0):
        """
        Return the API key with the highest remaining credit.

        Args:
            min_remaining_credit: Minimum remaining credit required.

        Returns:
            API key string if available, otherwise None.
        """
        results = self.check_all_keys()

        valid_keys = []

        for data in results:
            # Skip invalid API keys
            if "error" in data:
                continue

            remaining = data["remaining_credit"]

            if remaining >= min_remaining_credit:
                valid_keys.append(data)

        if not valid_keys:
            return None

        valid_keys.sort(
            key=lambda x: x["remaining_credit"],
            reverse=True
        )

        return valid_keys[0]["api_key"]