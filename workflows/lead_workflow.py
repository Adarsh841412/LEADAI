from services.scraper_service import ScraperService
from database.repository import LeadRepository
from database.db import get_db
class LeadWorkflow:
    def __init__(self)->None:
          pass 
    def run(self,job_title:str,location:str)->dict:
        
        # step1 scrapte the job 
        
        jobs = ScraperService.scrape_jobs(job_title,location)
        if not jobs :

            return {
                    "status": "failed",
                    "message": "No jobs found."
                }
                    
        db = get_db() 
        
        # step3 * save all this data into repository 
        
        try :
            repository = LeadRepository(db)
            saved_jobs = repository.save_leads(jobs)
            
            return {
                "status":'success',
                "scraped_jobs":len(jobs),
                "saved_jobs":saved_jobs
            }
        
        except Exception as e:
            print(e)
            return {
                'status':'failed',
                'message':'database error'
            }    
            
        finally:
            db.close() 
                
            
     
        
        
          
    