
# api/controller.py
import logging
from typing import Dict, Any
from workflows.lead_workflow import LeadWorkflow
from workflows.connect_workflow import ConnectWorkflow
from api.schemas import LeadGenerationRequest
logger = logging.getLogger(__name__)


class LeadGenerationController:
    @staticmethod
    def start(request: LeadGenerationRequest) -> Dict[str, Any]:
        """
        Start the lead generation workflow.
        
        Args:
            request: LeadGenerationRequest with job_title, location, platform
            
        Returns:
            Dict with status and message
        """
        try:
            logger.info(f"Starting lead generation for: {request.job_title} in {request.location}")
            
            # ✅ Validate request
            if not request:
                logger.error("Request is None")
                return {
                    "success": False,
                    "message": "Invalid request data"
                }
            
            # Step 1: Run LeadWorkflow
            try:
                logger.info("Starting LeadWorkflow...")

                lead_result = LeadWorkflow(
                    job_title=request.job_title or 'python developer',
                    location=request.location or 'US',
                    platform=request.platform.value or 'linkedin'
                ).run()
                
                logger.info(f"LeadWorkflow completed: {lead_result}")
                
                # Check if lead workflow failed
                if lead_result.get("status") == "failed":
                    logger.warning(f"LeadWorkflow failed: {lead_result.get('message')}")
                    return {
                        "success": False,
                        "message": f"Lead generation failed: {lead_result.get('message')}",
                        "details": lead_result
                    }
                    
                    
            except Exception as e:
                logger.error(f"LeadWorkflow error: {e}", exc_info=True)
                return {
                    "success": False,
                    "message": f"Lead generation error: {str(e)}"
                }
            
            return {
                "success": True,
                "message": "Lead generation completed successfully",
                "lead_generation": lead_result,
                # "connect_workflow": connect_result
            }
            
        except Exception as e:
            logger.error(f"Unexpected error in lead generation: {e}", exc_info=True)
            return {
                "success": False,
                "message": f"Unexpected error: {str(e)}"
            }        
            
 
 
 # api/connect_controller.py

class ConnectController:
    """
    Controller for email enrichment and outreach workflow.
    
    Steps:
        1. Fetch pending leads (without email)
        2. Enrich emails using external services
        3. Send outreach emails
        4. Update lead status
    """
    
    @staticmethod
    def start() -> Dict[str, Any]:
        """
        Start the connect workflow.
        
        Returns:
            Dict with status and results
        """
        try:
            logger.info("Starting connect workflow...")
            
            # Run workflow
            result = ConnectWorkflow().run()
            
            logger.info(f"Connect workflow completed: {result}")
            
            # Check if workflow failed
            if result.get("status") == "failed":
                return {
                    "success": False,
                    "message": result.get("message", "Connect workflow failed"),
                    "data": result
                }
            
            return {
                "success": True,
                "message": "Connect workflow completed successfully",
                "data": result
            }
            
        except Exception as e:
            logger.error(f"Connect workflow error: {e}", exc_info=True)
            return {
                "success": False,
                "message": f"Connect workflow error: {str(e)}"
            }