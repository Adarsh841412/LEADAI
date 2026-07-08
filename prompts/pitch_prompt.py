from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field


# class EmailMessage(BaseModel):
#     subject: str = Field(
#         description=(
#             "A concise, professional subject line relevant to the job opportunity."
#         )
#     )

#     email_message: str = Field(
#         description=(
#             "A complete, ready-to-send email body, written as a single unbroken paragraph."
#         )
#     )


# parser = PydanticOutputParser(pydantic_object=EmailMessage)


# prompt = PromptTemplate(
#     template="""
# You are an expert technical recruiter outreach email writer.

# Write a professional cold email from the applicant's perspective, addressed to a hiring
# manager or client, for the following opportunity.

# Job Information
# ---------------
# Company: {company}
# Job Title: {job_title}
# Job Description: {description}

# Writing Rules
# -------------
# - Write as the applicant, never as the company.
# - Tone: professional, confident, warm, and concise — not overly salesy or generic-sounding.
# - Maximum 150 words.
# - Start the message with "Hi," (never invent a hiring manager's name).
# - End the message with "Best regards,"
# - Mention that the resume is attached.
# - Do not use markdown, bullet points, or any special formatting.
# - Do not use placeholders like [Your Name] or [Company] — write it as final, sendable text.
# - Never output JSON or structured text inside the email_message field itself.

# Do NOT invent or assume:
# - years of experience
# - companies previously worked for
# - specific achievements or metrics
# - certifications
# - skills not mentioned in the job description

# Content to Cover (in one flowing paragraph)
# --------------------------------------------
# 1. Briefly introduce yourself.
# 2. Say why you're genuinely interested in this specific role and company.
# 3. Explain how your relevant technical skills align with the job description provided.
# 4. Mention that your resume is attached.
# 5. Politely ask for an opportunity to discuss further.
# 6. make sure we need to write mail as like the genuine mail formate like proper paraghaph




# STRICT folow below example FORMATTING  in below example if manger name is not found so you just need to sir :
# Hi [Manager's Name],

# I hope you're doing well. I just wanted to reach out and say hello. I wanted to check if there are any updates or tasks you'd like me to work on. Please let me know if there's anything I can help with.

# Looking forward to hearing from you.

# Best regards,
# Adarsh Dubey 

# {format_instructions}
# """,
#     input_variables=["company", "job_title", "description"],
#     partial_variables={"format_instructions": parser.get_format_instructions()},
# )
    
    
# # You are an expert technical recruiter outreach email writer.

# # Your task is to write a professional cold email from the applicant's perspective.

# # Job Information
# # ---------------

# # Company:
# # {company}

# # Job Title:
# # {job_title}

# # Job Description:
# # {description}

# # Instructions
# # ------------

# # - Write as the applicant, never as the company.
# # - Be professional, confident and concise.
# # - Maximum 150 words.
# # - Mention that the resume is attached.
# # - Do not use markdown.
# # - Do not use bullet points.
# # - Do not use placeholders like [Your Name].
# # - If the hiring manager's name is unknown, start with "Hi,".
# # - End politely with:
# #     Best regards,

# # Do NOT invent:
# # - years of experience
# # - companies worked for
# # - achievements
# # - certifications
# # - skills that are not mentioned in the job description

# # Focus on:
# # 1. Introduce yourself.
# # 2. Mention why you're interested in this role.
# # 3. Explain why your technical skills are relevant.
# # 4. Mention that your resume is attached.
# # 5. Ask politely for an opportunity to discuss further.

# # {format_instructions}
# # """,
# #     input_variables=[
# #         "company",
# #         "job_title",
# #         "description",
# #     ],
# #     partial_variables={
# #         "format_instructions": parser.get_format_instructions()
# #     },


# from langchain.prompts import PromptTemplate
# from langchain.output_parsers import PydanticOutputParser
# from pydantic import BaseModel, Field

# from langchain.prompts import PromptTemplate
# from langchain.output_parsers import PydanticOutputParser
# from pydantic import BaseModel, Field


class EmailMessage(BaseModel):
    subject: str = Field(
        description=(
            "A concise, professional subject line relevant to the job opportunity."
        )
    )

    email_message: str = Field(
        description=(
            "A complete, ready-to-send email body, formatted exactly like a genuine email: "
            "the greeting on its own line, then a blank line, then the main paragraph, "
            "then a blank line, then a short closing line, then a blank line, then "
            "'Best regards,' followed by the sender's name on the next line. "
            "Use actual newline characters (\\n\\n) between each of these parts — "
            "do NOT write it as one single unbroken block of text."
        )
    )


parser = PydanticOutputParser(pydantic_object=EmailMessage)


prompt = PromptTemplate(
    template="""
You are an expert technical recruiter outreach email writer.

Write a professional cold email from the applicant's perspective, addressed to a hiring
manager or client, for the following opportunity.

Applicant Name: Adarsh Dubey

Job Information
---------------
Company: {company}
Job Title: {job_title}
Job Description: {description}

Writing Rules
-------------
- Write as the applicant, never as the company.
- Tone: professional, confident, warm, and concise — not overly salesy or generic-sounding.
- Maximum 150 words.
- Never invent a hiring manager's name — always start with "Hi,".
- End the message with "Best regards," followed by rithik on the next line.
- Mention that the resume is attached.
- Do not use markdown, bullet points, or any special formatting.
- Do not use placeholders like [Your Name] or [Company] — write it as final, sendable text.
- Never output JSON or structured text inside the email_message field itself.

Do NOT invent or assume:
- years of experience
- companies previously worked for
- specific achievements or metrics
- certifications
- skills not mentioned in the job description

Content to Cover (in the body paragraph)
--------------------------------------------
1. Briefly introduce yourself.
2. Say why you're genuinely interested in this specific role and company.
3. Explain how your relevant technical skills align with the job description provided.
4. Mention that your resume is attached.
5. Politely ask for an opportunity to discuss further.

CRITICAL FORMATTING — the email_message field must follow this exact structure,
with real blank lines between each part (like a genuine email a person would actually send):

Hi,

<main paragraph goes here — one flowing paragraph covering all the content points above>

Looking forward to hearing from you.

Best regards,
ajay

{format_instructions}
""",
    input_variables=["company", "job_title", "description"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
)

