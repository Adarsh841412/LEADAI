from typing import Any
from datetime import datetime, timezone, timedelta


class JobFilter:

    TECH_KEYWORDS = {
        # Languages
        "python", "django", "fastapi", "flask",
        "react", "vue", "angular", "javascript", "typescript",
        "node", "nodejs", "express", "nestjs", "mern",
        "mongodb", "mysql", "postgresql", "postgres", "sql",
        "aws", "azure", "gcp", "docker", "kubernetes", "devops",
        "terraform", "jenkins",
        "ruby", "rails", "ruby on rails",
        "ai", "artificial intelligence", "machine learning", "ml",
        "genai", "llm", "langchain", "langgraph", "rag", "nlp",
        "data engineer", "data engineering", "spark", "hadoop",
        "airflow", "pandas", "numpy", "scikit",
        
        # 🔥 ADD THESE - Common tech terms in your job descriptions
        "go", "golang", "rust", "c++", "c#", "java",
        "spring", "springboot", "graphql",
        "microservices", "api", "backend", "frontend",
        "fullstack", "full stack", 
        "software engineer", "software developer",
        "distributed systems", "scalable",
        "typescript", "javascript", "html", "css",
        "redis", "kafka", "rabbitmq",
        "docker", "kubernetes", "terraform",
        "ci/cd", "jenkins", "github actions",
        "react", "vue", "angular", "next.js", "nextjs",
        "node.js", "nodejs", "express.js", "nestjs",
        "postgres", "mysql", "mongodb",
        "aws", "azure", "gcp", "cloud",
        "devops", "sre", "site reliability",
        "data", "analytics", "big data",
        "machine learning", "deep learning", "nlp",
        "llm", "langchain", "rag",
        "infrastructure", "automation",
        "agile", "scrum", "kanban",
        "git", "github", "bitbucket",
    }


    RECENT_DAYS_THRESHOLD = 2  # jobs posted within this many days count as "recent"

    @staticmethod
    def is_recent(posted_time: str | None, max_days: int = RECENT_DAYS_THRESHOLD) -> bool:
        """
        Return True if the job was posted within `max_days` days.

        Supports two formats:
        1. ISO datetime strings (what your LinkedIn scraper actually returns),
           e.g. '2026-07-03T00:00:00+00:00'
        2. Relative text like 'today', 'yesterday', '2 days ago', '5 hours ago'
        """
        if not posted_time:
            return False

        posted_time = str(posted_time).strip().lower()

        # --- Case 1: ISO datetime string (actual format from your scraper) ---
        try:
            posted_dt = datetime.fromisoformat(posted_time.replace("z", "+00:00"))
            if posted_dt.tzinfo is None:
                posted_dt = posted_dt.replace(tzinfo=timezone.utc)
            now = datetime.now(timezone.utc)
            return (now - posted_dt) <= timedelta(days=max_days)
        except ValueError:
            pass  # not ISO format, fall through to relative-text parsing

        # --- Case 2: relative text format ('today', '2 days ago', etc.) ---
        if posted_time in {"today", "yesterday"}:
            return True

        if "hour" in posted_time:
            return True

        if "day" in posted_time:
            try:
                days = int(posted_time.split()[0])
                return days <= max_days
            except (ValueError, IndexError):
                return False

        return False

    @classmethod
    def filter_recent_jobs(cls, jobs: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """
        Keep only jobs posted within the last RECENT_DAYS_THRESHOLD days.
        Reads from 'datePosted' (actual scraper field) with fallback to 'posted_time'.
        """
        return [
            job for job in jobs
            if cls.is_recent(job.get("datePosted") or job.get("posted_time"))
        ]

    @classmethod
    def filter_tech_jobs(cls, jobs: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """
        Keep only jobs whose title/description/skills mention a tech keyword.
        Reads from 'title' (actual scraper field) with fallback to 'job_title'.
        """
        filtered = []

        for job in jobs:
            title = job.get("title") or job.get("job_title", "")
            description = job.get("description", "")
            skills = job.get("skills", [])

            skills_text = " ".join(skills) if isinstance(skills, list) else str(skills)

            text = " ".join([str(title), str(description), skills_text]).lower()

            if any(keyword in text for keyword in cls.TECH_KEYWORDS):
                filtered.append(job)

        return filtered

    @classmethod
    def filter_recent_tech_jobs(cls, jobs: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """
        Convenience method: apply both filters together (recent AND tech).
        """
        recent = cls.filter_recent_jobs(jobs)
        return cls.filter_tech_jobs(recent)

    
    
