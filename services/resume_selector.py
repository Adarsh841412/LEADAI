import string 

RESUMES = {
    "python_backend": {
        "path": "assets/resumes/python_backend.pdf",
        "keywords": {
            "python": 10,
            "fastapi": 10,
            "django rest framework": 8,
            "flask": 8,
            "rest api": 8,
            "microservices": 7,
            "postgresql": 7,
            "redis": 6,
            "celery": 6,
            "docker": 6,
            "kubernetes": 5,
            "sql": 5,
            "asyncio": 5,
            "aws": 5,
            "rabbitmq": 4,
            "kafka": 4,
            "graphql": 4,
            "unit testing": 4,
            "pytest": 4,
            "ci/cd": 3,
            "nginx": 3,
            "gunicorn": 3,
            "orm": 3,
            "sqlalchemy": 3,
            "linux": 2,
            "git": 2,
        }
    },

    "django_backend": {
        "path": "assets/resumes/django_backend.pdf",
        "keywords": {
            "django": 10,
            "django rest framework": 10,
            "python": 8,
            "postgresql": 7,
            "celery": 7,
            "redis": 6,
            "graphql": 6,
            "docker": 6,
            "rest api": 6,
            "aws": 5,
            "multi-tenant": 5,
            "stripe": 5,
            "payment gateway": 5,
            "authentication": 4,
            "oauth": 4,
            "admin dashboard": 4,
            "rbac": 4,
            "unit testing": 4,
            "pytest": 4,
            "orm": 3,
            "nginx": 3,
            "gunicorn": 3,
            "ci/cd": 3,
            "sql": 3,
            "git": 2,
            "linux": 2,
        }
    },

    "ai_engineer": {
        "path": "assets/resumes/ai_engineer.pdf",
        "keywords": {
            "langchain": 10,
            "rag": 10,
            "llm": 10,
            "prompt engineering": 8,
            "vector database": 8,
            "agent": 7,
            "openai": 5,
            "python": 2,
            "anthropic": 5,
            "groq": 5,
            "pinecone": 5,
            "chroma": 5,
            "embeddings": 6,
            "fine-tuning": 5,
            "llamaindex": 5,
            "huggingface": 5,
            "transformers": 5,
            "fastapi": 4,
            "structured output": 4,
            "pydantic": 4,
            "semantic search": 5,
            "chatbot": 4,
            "tool calling": 5,
            "function calling": 5,
            "gpt": 4,
            "chain of thought": 3,
            "tokenization": 3,
            "context window": 3,
            "gemini": 3,
            "claude": 3,
        }
    },

    "ml_engineer": {
        "path": "assets/resumes/ml_engineer.pdf",
        "keywords": {
            "pytorch": 10,
            "tensorflow": 10,
            "scikit-learn": 8,
            "machine learning": 8,
            "mlflow": 7,
            "model deployment": 7,
            "pandas": 6,
            "numpy": 6,
            "aws sagemaker": 6,
            "docker": 5,
            "feature engineering": 5,
            "hyperparameter tuning": 5,
            "classification": 4,
            "regression": 4,
            "deep learning": 6,
            "neural network": 5,
            "cnn": 4,
            "nlp": 5,
            "computer vision": 5,
            "model monitoring": 4,
            "a/b testing": 4,
            "data preprocessing": 4,
            "python": 3,
            "sql": 3,
            "kubernetes": 3,
            "airflow": 3,
            "jupyter": 2,
            "git": 2,
        }
    },

    "data_engineer": {
        "path": "assets/resumes/data_engineer.pdf",
        "keywords": {
            "apache airflow": 10,
            "spark": 10,
            "etl": 9,
            "kafka": 8,
            "snowflake": 8,
            "dbt": 7,
            "sql": 7,
            "aws glue": 6,
            "data warehouse": 6,
            "data pipeline": 6,
            "python": 5,
            "postgresql": 5,
            "big data": 5,
            "hadoop": 4,
            "redshift": 4,
            "bigquery": 4,
            "data modeling": 5,
            "streaming": 5,
            "batch processing": 4,
            "data lake": 4,
            "docker": 3,
            "aws": 4,
            "orchestration": 4,
            "data quality": 3,
            "git": 2,
            "linux": 2,
        }
    },

    "ruby": {
        "path": "assets/resumes/ruby.pdf",
        "keywords": {
            "ruby": 10,
            "ruby on rails": 10,
            "rspec": 8,
            "sidekiq": 7,
            "postgresql": 6,
            "redis": 6,
            "activerecord": 6,
            "rest api": 5,
            "heroku": 5,
            "aws": 5,
            "docker": 5,
            "background jobs": 4,
            "graphql": 4,
            "capistrano": 3,
            "rubocop": 3,
            "bundler": 3,
            "gem": 3,
            "mvc": 3,
            "test driven development": 4,
            "ci/cd": 3,
            "unit testing": 4,
            "sql": 3,
            "git": 2,
            "linux": 2,
        }
    },

    "mern": {
        "path": "assets/resumes/mern.pdf",
        "keywords": {
            "react": 10,
            "node.js": 10,
            "express.js": 9,
            "mongodb": 9,
            "javascript": 8,
            "typescript": 7,
            "redux": 6,
            "rest api": 6,
            "next.js": 5,
            "tailwind css": 4,
            "html": 4,
            "css": 4,
            "jwt": 4,
            "graphql": 4,
            "webpack": 3,
            "docker": 4,
            "aws": 4,
            "unit testing": 4,
            "jest": 4,
            "responsive design": 3,
            "hooks": 4,
            "component library": 3,
            "state management": 4,
            "ci/cd": 3,
            "git": 2,
            "npm": 2,
        }
    },

    "fullstack": {
        "path": "assets/resumes/fullstack.pdf",
        "keywords": {
            "react": 8,
            "node.js": 7,
            "python": 7,
            "django": 6,
            "javascript": 7,
            "postgresql": 6,
            "rest api": 6,
            "docker": 6,
            "aws": 6,
            "ci/cd": 5,
            "typescript": 5,
            "html": 4,
            "css": 4,
            "git": 4,
            "github actions": 4,
            "sql": 4,
            "microservices": 4,
            "redux": 3,
            "express.js": 3,
            "mongodb": 3,
            "linux": 3,
            "agile": 3,
            "unit testing": 3,
            "system design": 4,
            "api integration": 3,
            "authentication": 3,
        }
    },
}



class ResumeSelector:
    
    def clean_text(self,description:str):
        
        translator = str.maketrans('','',string.punctuation)
        clean_text = description.translate(translator).lower()
        return clean_text
    
       
    def _score_resume(
    self,
    description: str,
) -> dict:
        """
        Score every resume against the job description
        and return the best matching resume.
        """

        description = self.clean_text(description)

        best_resume = None
        best_score = -1

        for resume_name, resume_info in RESUMES.items():

            score = 0

            keywords = resume_info["keywords"]

            for keyword, weight in keywords.items():

                if keyword.lower() in description:
                    score += weight

            if score > best_score:
                best_score = score
                best_resume = {
                    "resume_name": resume_name,
                    "resume_path": resume_info["path"],
                    "score": score,
                }

        return best_resume 
    
    @classmethod
    def select_best_resume(
        cls,
        description: str,
    ) -> dict:

        selector = cls()

        return selector._score_resume(description)

# r1 = ResumeSelector() 


# description = """
# We are looking for a Python Developer with FastAPI,
# PostgreSQL, Docker, SQLAlchemy and AWS experience.
# """

# resume = ResumeSelector.select_best_resume(description)
# print(resume)