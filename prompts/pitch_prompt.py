from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field


class EmailMessage(BaseModel):
    subject: str = Field(
        description=(
            "A concise, professional subject line relevant to the job opportunity."
        )
    )

    email_message: str = Field(
        description=(
            "A complete ready-to-send email body."
        )
    )


parser = PydanticOutputParser(
    pydantic_object=EmailMessage
)


prompt = PromptTemplate(
    template="""
You are an expert technical recruiter outreach email writer.

Your task is to write a professional cold email from the applicant's perspective.

Job Information
---------------

Company:
{company}

Job Title:
{job_title}

Job Description:
{description}

Instructions
------------

- Write as the applicant, never as the company.
- Be professional, confident and concise.
- Maximum 150 words.
- Mention that the resume is attached.
- Do not use markdown.
- Do not use bullet points.
- Do not use placeholders like [Your Name].
- If the hiring manager's name is unknown, start with "Hi,".
- End politely with:
    Best regards,

Do NOT invent:
- years of experience
- companies worked for
- achievements
- certifications
- skills that are not mentioned in the job description

Focus on:
1. Introduce yourself.
2. Mention why you're interested in this role.
3. Explain why your technical skills are relevant.
4. Mention that your resume is attached.
5. Ask politely for an opportunity to discuss further.

{format_instructions}
""",
    input_variables=[
        "company",
        "job_title",
        "description",
    ],
    partial_variables={
        "format_instructions": parser.get_format_instructions()
    },
)