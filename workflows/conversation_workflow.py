from database.repository import LeadRepository
from database.db import get_db
from services.gmail_service import GmailService
from services.llm_service import LlmService 
from prompts.conversation_prompt import prompt,parser

class ConversationWorkflow:
    
    def __init__(self):
        
        self.db = get_db() 
        self.repsitory = LeadRepository(self.db)
        self.gmail_service = GmailService() 
        self.llm_service = LlmService(prompt,parser) 
        

    def run(self):
        
        get_converation_lead = self.repsitory.get_pending_conversation()
        print("hello wrold")
        
        for lead in get_converation_lead:
  
            latest_message = self.gmail_service.get_latest_recruiter_message(lead.thread_id)
            # print(latest_message)
            subject=latest_message.get("subject")
            email=latest_message.get("snippet")
            payload = {
                "subject":subject,
                "email":email
            }
            recruiter_response_analyze = self.llm_service.email_generator(payload,k=1)
            print(recruiter_response_analyze)
            break
            
            
            
            
            
            
            
             
            


            
            
            
            





c1 = ConversationWorkflow() 
c1.run() 
        
