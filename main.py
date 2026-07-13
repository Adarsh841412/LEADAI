# from workflows.lead_workflow import LeadWorkflow
# from workflows.connect_workflow import ConnectWorkflow
# from workflows.outreach_workflow import OutreachWorkflow

# def main():

#  #* handling lead workflow 

#     flow_number = input('Enter the flow number \n 1 . Lead_workflow \n 2 . Connect workflow \n 3.Outreach worflow\n').strip() 
#     if flow_number == '1':
#         workflow = LeadWorkflow(
#         job_title="Python Developer",
#         location="USA",
#     )

#         result = workflow.run()
#         print(result)
    
#     elif flow_number == '2':
#         workflow = ConnectWorkflow() 
#         result = workflow.run() 
#         print(result )
        
        
#     elif flow_number == '3':
#         workflow = OutreachWorkflow() 
#         result = workflow.run() 
#         print(result)
                
#     else :
#         print("all is good")    
        
        
       
    
# main() 



from workflows.followup_workflow import *

# # # from providers.gmail import *

# # from prompts.followup_prompt import *

# # from database.models import * 




























# from google_auth_oauthlib.flow import InstalledAppFlow

# SCOPES = [
#     "https://www.googleapis.com/auth/gmail.send",
#     "https://www.googleapis.com/auth/gmail.readonly",
#     "https://www.googleapis.com/auth/gmail.modify",
# ]

# flow = InstalledAppFlow.from_client_secrets_file(
#     "credentials.json",
#     SCOPES,
# )

# creds = flow.run_local_server(port=0)

# with open("token.json", "w") as token:
#     token.write(creds.to_json())

# print("Token generated successfully!")