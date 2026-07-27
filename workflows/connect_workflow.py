# from database.db import get_db
# from database.repository import LeadRepository
# from services.connect_service import ConnectService


# class ConnectWorkflow:
#     """
#     Connect Workflow.

#     Flow:
#         Repository
#             ↓
#         Pending Leads
#             ↓
#         Connect Service
#             ↓
#         Update Repository
#     """

#     def __init__(self) -> None:

#         self.db = get_db()

#         self.repository = LeadRepository(self.db)

#         self.connect_service = ConnectService()

#     def run(self) -> dict:
#         """
#         Execute the Connect Workflow.
#         """

#         processed = 0
#         success = 0
#         failed = 0
     

#         # Leads without email
#         try :
            
#             leads = self.repository.get_pending_connections()
#             pending_connections = len(leads) | 0 
            
#             print(leads)
#             if not leads:
#                 return {
#                     "processed": 0,
#                     "success": 0,
#                     "failed": 0,
#                 }

#             for lead in leads:

#                 processed += 1

#                 try:

#                     enriched = self.connect_service.enrich_lead(
#                       lead =     {
#                             "company": lead.company,
#                             "location": lead.location,
                           
                            
#                         },
#                       pending_connections=pending_connections,
#                     )

#                     if not enriched:
#                         failed += 1
#                         continue
            
            
#                     self.repository.update_company_domain(
#                         lead.id,
#                         enriched["company_domain"],
#                     )

#                     self.repository.update_contact(
#                         lead_id = lead.id,
#                         company_domain=enriched['company_domain'],
#                         email=enriched["email"],
#                         email_verified=False,
#                     )

#                     success += 1

#                 except Exception as e:

#                     print(e)

#                     failed += 1

#             return {
#                 "processed": processed,
#                 "success": success,
#                 "failed": failed,
#             }
#         except Exception as e:
#             print("error at connect workflow",e)
        
#         finally :
#             self.db.close() 
            





# workflows/connect_workflow.py
import logging
from typing import Dict, Any, Optional
from sqlalchemy import text

from database.db import get_db
from database.repository import LeadRepository
from services.connect_service import ConnectService

logger = logging.getLogger(__name__)


class ConnectWorkflow:
    """
    Connect Workflow for email enrichment and outreach.

    Flow:
        Repository → Pending Leads → Connect Service → Update Repository
    """

    def __init__(self) -> None:
        """Initialize the ConnectWorkflow with database connection and services."""
        self.db = None
        self.repository = None
        self.connect_service = None
        
        try:
            self.db = get_db()
            self.repository = LeadRepository(self.db)
            self.connect_service = ConnectService()
            logger.info("ConnectWorkflow initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize ConnectWorkflow: {e}", exc_info=True)
            raise

    def _close_db_connection(self) -> None:
        """Safely close database connection."""
        if self.db:
            try:
                self.db.close()
                logger.debug("Database connection closed")
            except Exception as e:
                logger.warning(f"Error closing database connection: {e}")

    def run(self) -> Dict[str, Any]:
        """
        Execute the Connect Workflow.

        Returns:
            Dict with workflow results:
            {
                "status": "success" or "failed",
                "processed": int,
                "success": int,
                "failed": int,
                "message": str
            }
        """
        processed = 0
        success = 0
        failed = 0
        leads = []

        try:
            logger.info("Starting Connect Workflow...")

            #  Step 1: Get pending leads (without email)
            
            try:
                leads = self.repository.get_pending_connections()
                logger.info(f"Found {len(leads)} pending leads")
            except Exception as e:
                logger.error(f"Failed to get pending leads: {e}", exc_info=True)
                return {
                    "status": "failed",
                    "processed": 0,
                    "success": 0,
                    "failed": 0,
                    "message": f"Failed to fetch leads: {str(e)}"
                }

            #  Step 2: Check if leads exist
            if not leads:
                logger.info("No pending leads found")
                return {
                    "status": "success",
                    "processed": 0,
                    "success": 0,
                    "failed": 0,
                    "message": "No pending leads to process"
                }

            total_leads = len(leads)

            #  Step 3: Process each lead
            for index, lead in enumerate(leads, 1):
                processed += 1

                try:
                    logger.info(f"Processing lead {index}/{total_leads}: {lead.company}")

                    #  Step 3a: Enrich lead data
                    enriched = self.connect_service.enrich_lead(
                        lead={
                            "company": lead.company,
                            "location": lead.location,
                        },
                        pending_connections=total_leads,
                    )

                    #  Step 3b: Check if enrichment failed
                    if not enriched:
                        logger.warning(f"Enrichment failed for lead {lead.id} - {lead.company}")
                        failed += 1
                        continue

                    #  Step 3c: Validate enriched data
                    if not enriched.get("email"):
                        logger.warning(f"No email found for lead {lead.id} - {lead.company}")
                        failed += 1
                        continue

                    #  Step 3d: Update company domain
                    try:
                        self.repository.update_company_domain(
                            lead.id,
                            enriched.get("company_domain", "")
                        )
                    except Exception as e:
                        logger.error(f"Failed to update domain for lead {lead.id}: {e}")
                        # Continue to update contact anyway

                    #  Step 3e: Update contact info
                    try:
                        self.repository.update_contact(
                            lead_id=lead.id,
                            company_domain=enriched.get("company_domain", ""),
                            email=enriched.get("email", ""),
                            email_verified=False,
                        )
                        success += 1
                        logger.info(f"Successfully enriched lead {lead.id} - {lead.company}")
                    except Exception as e:
                        logger.error(f"Failed to update contact for lead {lead.id}: {e}")
                        failed += 1

                except Exception as e:
                    logger.error(f"Error processing lead {lead.id}: {e}", exc_info=True)
                    failed += 1

            #  Step 4: Return results
            logger.info(f"Connect Workflow completed: processed={processed}, success={success}, failed={failed}")
            
            return {
                "status": "success" if success > 0 else "failed",
                "processed": processed,
                "success": success,
                "failed": failed,
                "message": f"Processed {processed} leads: {success} enriched, {failed} failed"
            }

        except Exception as e:
            logger.error(f"Connect Workflow error: {e}", exc_info=True)
            return {
                "status": "failed",
                "processed": processed,
                "success": success,
                "failed": failed,
                "message": f"Workflow error: {str(e)}"
            }

        finally:
            #  Always close database connection
            self._close_db_connection()