
"""
providers/domain_provider.py
============================

Responsible for discovering a company's official domain.
"""

from urllib.parse import urlparse

from apify_client import ApifyClient

from config.settings import (
    APIFY_TOKEN,
    DOMAIN_ACTOR_ID,
)


class DomainProvider:
    """
    Find the official company domain using an Apify Actor.
    """

    def __init__(self) -> None:
        self.client = ApifyClient('apify_api_1a5Pk8VUYi3UPrggvDNztx5EUsq1sV06UQCR')

    def find_domain(
        self,
        company_name: str,
        location: str,
    ) -> str | None:
        """
        Find the company's official domain.

        Args:
            company_name: Company name.
            location: Company country/location.

        Returns:
            Company domain if found else None.
        """

        run_input = {
            "name": company_name,
            "country": location,
        }

        run = self.client.actor(
            DOMAIN_ACTOR_ID
        ).call(run_input=run_input)
    
        dataset_id = run.default_dataset_id

        for item in self.client.dataset(dataset_id).iterate_items():

            website = item.get("official_website")

            if not website:
                return None

            domain = (
                urlparse(website)
                .netloc
                .replace("www.", "")
            )

            return domain

        return None
 
 
 

    
    
# provider = DomainProvider()
# domain = provider.find_domain(
#         company_name="Hire Feed",
#         location="India",
#     )

# print(domain)    