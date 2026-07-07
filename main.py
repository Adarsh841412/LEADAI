from workflows.lead_workflow import LeadWorkflow
from workflows.connect_workflow import ConnectWorkflow

def main():

 #* handling lead workflow 

    flow_number = input('Enter the flow number \n 1 . Lead_workflow \n 2 . Connect workflow \n').strip() 
    if flow_number == '1':
        workflow = LeadWorkflow(
        job_title="Python Developer",
        location="India",
    )

        result = workflow.run()
        print(result)
    
    elif flow_number == '2':
        workflow = ConnectWorkflow() 
        result = workflow.run() 
        print(result )
        
    else :
        print("all is good")    
        
        
        
    



if __name__ == "__main__":
    main()


