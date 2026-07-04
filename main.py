from workflows.lead_workflow import LeadWorkflow


def main():

 #* handling lead workflow 

    workflow = LeadWorkflow(
        job_title="Python Developer",
        location="India",
    )

    result = workflow.run()



if __name__ == "__main__":
    main()

