# """
# services/connect_service.py
# ===========================

# Service responsible for enriching a lead with
# company domain and best contact email.
# """

# from typing import Any
# from providers.domain_provider import DomainProvider
# from providers.hunter import HunterProvider
# from utils.ranking import EmailRanker
# from manager.hunter_manager import HunterManager
# from manager.apify_manager import ApifyManager 

# class ConnectService:
#     """
#     Handles lead enrichment.

#     Flow:

#     Lead
#         ↓
#     Domain Provider
#         ↓
#     Hunter
#         ↓
#     Ranking
#         ↓
#     Return Best Contact
#     """

#     def __init__(self) -> None:
        
#         self.domain_provider = DomainProvider()
#         self.hunter_manager = HunterManager() 
#         # self.api_key = self.hunter_manager.get_available_key()
#         self.hunter_provider = HunterProvider()
#         self.apify_manager = ApifyManager() 
        

#     def enrich_lead(
#         self,
#         lead: dict[str, Any],
#         pending_connections:int 
       
       
#     ) -> dict[str, Any] | None:
#         """
#         Enrich a single lead.

#         Args:
#             lead: Lead dictionary from repository.

#         Returns:
#             Enriched contact dictionary or None.
#         """
#         api_key = self.hunter_manager.get_available_key(pending_connections)
#         company = lead.get("company")
#         location = lead.get("location")

#         if not company:
#             return None

#         # -------------------------------------------------
#         # Step 1 : Find Company Domain
#         # -------------------------------------------------

#         company_domain = self.domain_provider.find_domain(
#             company_name=company,
#             location=location,
#             api = self.apify_manager.get_best_key()
            
#         )

#         if not company_domain:
#             return None

#         # -------------------------------------------------
#         # Step 2 : Search Emails
#         # -------------------------------------------------
        
#         hunter_response = self.hunter_provider.domain_search(
#             domain=company_domain,
#             api_key = api_key
            
           
#         )
        
    
#         if not hunter_response:
#             return None

#         # -------------------------------------------------
#         # Step 3 : Extract Hunter Contacts
#         # -------------------------------------------------

#         contacts = (
#             hunter_response
#             .get("data", {})
#             .get("emails", [])
#         )
        

#         if not contacts:
#             return None

#         # -------------------------------------------------
#         # Step 4 : Rank Contacts
#         # -------------------------------------------------

#         best_contact = EmailRanker.select_best_contact(
#             contacts
#         )

#         if not best_contact:
#             return None

#         # -------------------------------------------------
#         # Step 5 : Attach Domain
#         # -------------------------------------------------

#         best_contact["company_domain"] = company_domain
#         return best_contact




"""
services/connect_service.py
===========================

Service responsible for enriching a lead with
company domain and best contact email.
"""

import logging
from typing import Any, Dict, Optional

from providers.domain_provider import DomainProvider
from providers.hunter import HunterProvider
from utils.ranking import EmailRanker
from manager.hunter_manager import HunterManager
from manager.apify_manager import ApifyManager

logger = logging.getLogger(__name__)


class ConnectServiceError(Exception):
    """Base exception for ConnectService errors."""
    pass


class ConnectService:
    """
    Handles lead enrichment.

    Flow:
        Lead → Domain Provider → Hunter → Ranking → Return Best Contact
    """

    def __init__(self) -> None:
        """Initialize the ConnectService with all required providers."""
        try:
            self.domain_provider = DomainProvider()
            self.hunter_manager = HunterManager()
            self.hunter_provider = HunterProvider()
            self.apify_manager = ApifyManager()
            logger.info("ConnectService initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize ConnectService: {e}", exc_info=True)
            raise ConnectServiceError(f"Initialization failed: {str(e)}")

    def enrich_lead(
        self,
        lead: Dict[str, Any],
        pending_connections: int
    ) -> Optional[Dict[str, Any]]:
        """
        Enrich a single lead with company domain and email.

        Args:
            lead: Lead dictionary from repository.
                Required keys: "company", "location"
            pending_connections: Number of pending connections (for API key selection)

        Returns:
            Enriched contact dictionary with company_domain, email, etc.
            Returns None if enrichment fails at any step.

        Raises:
            ConnectServiceError: For unexpected errors during enrichment
        """
        #  Step 0: Validate input
        if not lead:
            logger.warning("Lead is None or empty")
            return None

        company = lead.get("company")
        location = lead.get("location")

        if not company:
            logger.warning("Lead missing company name")
            return None

        logger.info(f"Enriching lead: company='{company}', location='{location}'")

        # -------------------------------------------------
        # Step 1: Get API Key
        # -------------------------------------------------
        try:
            api_key = self.hunter_manager.get_available_key(pending_connections)
            if not api_key:
                logger.warning("No available Hunter API key")
                return None
        except Exception as e:
            logger.error(f"Failed to get API key: {e}", exc_info=True)
            return None

        # -------------------------------------------------
        # Step 2: Find Company Domain
        # -------------------------------------------------
        try:
            best_key = self.apify_manager.get_best_key()
            if not best_key:
                logger.warning("No available Apify key")
                return None

            company_domain = self.domain_provider.find_domain(
                company_name=company,
                location=location,
                api=best_key
            )

            if not company_domain:
                logger.warning(f"Could not find domain for company: {company}")
                return None

            logger.info(f"Found domain: {company_domain}")

        except Exception as e:
            logger.error(f"Domain lookup failed for {company}: {e}", exc_info=True)
            return None

        # -------------------------------------------------
        # Step 3: Search Emails
        # -------------------------------------------------
        try:
            hunter_response = self.hunter_provider.domain_search(
                domain=company_domain,
                api_key=api_key
            )

            if not hunter_response:
                logger.warning(f"No Hunter response for domain: {company_domain}")
                return None

        except Exception as e:
            logger.error(f"Hunter search failed for {company_domain}: {e}", exc_info=True)
            return None

        # -------------------------------------------------
        # Step 4: Extract Hunter Contacts
        # -------------------------------------------------
        try:
            contacts = (
                hunter_response
                .get("data", {})
                .get("emails", [])
            )

            if not contacts:
                logger.warning(f"No emails found for domain: {company_domain}")
                return None

            logger.info(f"Found {len(contacts)} emails for {company_domain}")

        except Exception as e:
            logger.error(f"Failed to extract contacts for {company_domain}: {e}", exc_info=True)
            return None

        # -------------------------------------------------
        # Step 5: Rank Contacts
        # -------------------------------------------------
        try:
            best_contact = EmailRanker.select_best_contact(contacts)

            if not best_contact:
                logger.warning(f"No valid contact found after ranking for {company_domain}")
                return None

        except Exception as e:
            logger.error(f"Failed to rank contacts for {company_domain}: {e}", exc_info=True)
            return None

        # -------------------------------------------------
        # Step 6: Attach Domain and Return
        # -------------------------------------------------
        try:
            best_contact["company_domain"] = company_domain
            logger.info(f"Successfully enriched lead: {company} -> {best_contact.get('email')}")
            return best_contact

        except Exception as e:
            logger.error(f"Failed to attach domain for {company_domain}: {e}", exc_info=True)
            return None