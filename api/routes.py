# from api.controller import LeadGenerationController 
# from api.schemas import LeadGenerationRequest 

# from fastapi import APIRouter 

# router = APIRouter(prefix="/lead-generation-start")

# @router.post("/")
# async def start_generation(request:LeadGenerationRequest):
#     return LeadGenerationController().start(request)




# api/routes.py
import logging
from fastapi import APIRouter, HTTPException
from api.controller import LeadGenerationController,ConnectController
from api.schemas import LeadGenerationRequest


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/lead-generation-start")


@router.post("/")
async def start_generation(request: LeadGenerationRequest):
    """
    Start lead generation workflow.
    
    Args:
        request: LeadGenerationRequest with job_title, location, platform
        
    Returns:
        JSON response with status
    """
    try:
        logger.info(f"Received lead generation request: {request}")
        
        #  Validate request
        if not request.job_title:
            raise HTTPException(
                status_code=400,
                detail="Job title is required"
            )
        
        if not request.location:
            raise HTTPException(
                status_code=400,
                detail="Location is required"
            )
        
        #  Call controller
        result = LeadGenerationController.start(request)
        
        #  Check result
        if not result.get("success", False):
            # Return appropriate status code based on error
            status_code = 400 if "validation" in str(result.get("message", "")).lower() else 500
            raise HTTPException(
                status_code=status_code,
                detail=result.get("message", "Unknown error")
            )
        
        return result
        
    except HTTPException:
        #  Re-raise HTTP exceptions
        raise
        
    except Exception as e:
        logger.error(f"Unexpected error in route: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )
   

         
@router.post("/connect")      
async def ConnectRoute():

       """
       start the connect workflow 
        """
       try:
           logger.info("Recived connect workflow request")
           result = ConnectController.start() 
           
           if not result.get('success',False):
                raise HTTPException(
                    status_code = 500,
                    detail = result.get("message", "Connect workflow failed")
                )
           return result     
        
       except HTTPException:
           raise 
       
       except Exception as e:
        logger.error(f"Connect route error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )
        

        
        
        
