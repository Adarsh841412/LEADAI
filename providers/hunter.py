
from typing import Any

import requests

from config.settings import (
    HUNTER_API_KEY,
    HUNTER_BASE_URL,
    HUNTER_VERIFY_URL,
)

print(HUNTER_API_KEY)

class HunterProvider:
    """
    Handles Hunter.io API operations.
    """

    def __init__(self) -> None:
        pass 

    def domain_search(
        self,
        domain: str,
        limit: int = 10,
        api_key:str=''
     
    ) -> dict[str, Any] | None:
        """
        Search for company emails using a company domain.

        Args:
            domain: Company domain.
            limit: Maximum number of emails to return.

        Returns:
            Hunter API response or None.
        """

        params = {
            "domain": domain,
            "limit": limit,
            "api_key": api_key,
        }

        try:
            response = requests.get(
                HUNTER_BASE_URL,
                params=params,
            )

            response.raise_for_status()

            return response.json()

        except requests.RequestException:
            print('error occured in domain search')
            return None 


    def verify_email(
        self,
        email: str,
    ) -> dict[str, Any] | None:
        """
        Verify an email address.

        Args:
            email: Email address.

        Returns:
            Hunter verification response or None.
        """

        params = {
            "email": email,
            "api_key": self.api_key,
        }

        try:
            response = requests.get(
                HUNTER_VERIFY_URL,
                params=params,
            )

            response.raise_for_status()

            return response.json()

        except requests.RequestException:
            print("Error during Hunter domain search")
            return None





