"""
services/connect_service.py
===========================

Service responsible for enriching a lead with
company domain and best contact email.
"""

from typing import Any

from providers.domain_provider import DomainProvider
from providers.hunter import HunterProvider
from utils.ranking import EmailRanker


class ConnectService:
    """
    Handles lead enrichment.

    Flow:

    Lead
        ↓
    Domain Provider
        ↓
    Hunter
        ↓
    Ranking
        ↓
    Return Best Contact
    """

    def __init__(self) -> None:
        self.domain_provider = DomainProvider()
        self.hunter_provider = HunterProvider()

    def enrich_lead(
        self,
        lead: dict[str, Any],
    ) -> dict[str, Any] | None:
        """
        Enrich a single lead.

        Args:
            lead: Lead dictionary from repository.

        Returns:
            Enriched contact dictionary or None.
        """

        company = lead.get("company")
        location = lead.get("location")

        if not company:
            return None

        # -------------------------------------------------
        # Step 1 : Find Company Domain
        # -------------------------------------------------

        company_domain = self.domain_provider.find_domain(
            company_name=company,
            location=location,
        )

        if not company_domain:
            return None

        # -------------------------------------------------
        # Step 2 : Search Emails
        # -------------------------------------------------
        
        hunter_response = self.hunter_provider.domain_search(
            domain=company_domain,
        )

        # print(company_domain)
        # print(hunter_response)
        
    
        if not hunter_response:
            return None

        # -------------------------------------------------
        # Step 3 : Extract Hunter Contacts
        # -------------------------------------------------

        contacts = (
            hunter_response
            .get("data", {})
            .get("emails", [])
        )
        

        if not contacts:
            return None

        # -------------------------------------------------
        # Step 4 : Rank Contacts
        # -------------------------------------------------

        best_contact = EmailRanker.select_best_contact(
            contacts
        )

        if not best_contact:
            return None

        # -------------------------------------------------
        # Step 5 : Attach Domain
        # -------------------------------------------------

        best_contact["company_domain"] = company_domain
        return best_contact



# service = ConnectService()

# lead = {
#         "company": "Stripe",
#         "location": "United States",
#     }

# result = service.enrich_lead(lead)

# print(result)
    
    