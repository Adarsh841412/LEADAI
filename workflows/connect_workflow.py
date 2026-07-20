from database.db import get_db
from database.repository import LeadRepository
from services.connect_service import ConnectService


class ConnectWorkflow:
    """
    Connect Workflow.

    Flow:
        Repository
            ↓
        Pending Leads
            ↓
        Connect Service
            ↓
        Update Repository
    """

    def __init__(self) -> None:

        self.db = get_db()

        self.repository = LeadRepository(self.db)

        self.connect_service = ConnectService()

    def run(self) -> dict:
        """
        Execute the Connect Workflow.
        """

        processed = 0
        success = 0
        failed = 0

        # Leads without email
        try :
            
            leads = self.repository.get_pending_connections()
            print(leads)
            if not leads:
                return {
                    "processed": 0,
                    "success": 0,
                    "failed": 0,
                }

            for lead in leads:

                processed += 1

                try:

                    enriched = self.connect_service.enrich_lead(
                        {
                            "company": lead.company,
                            "location": lead.location,
                        }
                    )

                    if not enriched:
                        failed += 1
                        continue
            
            
                    self.repository.update_company_domain(
                        lead.id,
                        enriched["company_domain"],
                    )

                    self.repository.update_contact(
                        lead_id = lead.id,
                        company_domain=enriched['company_domain'],
                        email=enriched["email"],
                        email_verified=False,
                    )

                    success += 1

                except Exception as e:

                    print(e)

                    failed += 1

            return {
                "processed": processed,
                "success": success,
                "failed": failed,
            }
        except Exception as e:
            print("error at connect workflow",e)
        
        finally :
            self.db.close() 
            







# workflow = ConnectWorkflow()

# result = workflow.run()

# print(result)