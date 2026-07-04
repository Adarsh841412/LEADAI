import json 
class JobParser:

    @staticmethod
    def parse_job(job: dict) -> dict:
        """
        Convert one raw Apify job into a normalized lead dictionary.
        """

        return {
            "company": job.get("companyName"),
            "job_title": job.get("title"),
            "location": job.get("location"),
            "job_url": job.get("jobUrl"),
            "platform": "LinkedIn",
            "description": "\n".join(job.get("requirements", [])),
            "skills": job.get("techStack"),
            "email": job.get("companyEmail"),
            "email_verified": False,
            "status": "NEW",
            "posted_time": job.get("postedTime"),
        }

    @classmethod
    def parse_jobs(cls) -> list[dict]:
        """
        Parse all jobs returned by Apify.
        """

        parsed_jobs = []
        with open('/home/developer/LEADAI/file.txt','r') as f:
            jobs = json.load(f)

        for job in jobs:
            parsed_jobs.append(cls.parse_job(job))
       
        return parsed_jobs
    
    
