from services.scraper_service import ScraperService
from database.repository import LeadRepository
from database.db import get_db
class LeadWorkflow:
    def __init__(self,job_title:str,location:str)->None:
        self.job_title = job_title
        self.location = location 
    
    def run(self)->dict:
        
        # step1 scrapte the job 
        
        jobs = ScraperService.scrape_jobs(self.job_title,self.location)
        print("this is jobs",jobs)
        # step2 open database session 
        
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
            
        finally:
            db.close() 
                
            
     
        
        
          
    