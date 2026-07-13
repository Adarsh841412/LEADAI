from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field


class FollowUpMessage(BaseModel):
    subject: str = Field(
        description="Professional follow-up email subject."
    )

    email_message: str = Field(
        description="Professional follow-up email message ."
    )


parser = PydanticOutputParser(
    pydantic_object=FollowUpMessage
)


prompt = PromptTemplate(
    template="""
You are an experienced technical recruiter outreach assistant.

An outreach email has already been sent to the client.

Your job is to write the FIRST follow-up email.

========================
Company
========================

{company}

========================
Job Title
========================

{job_title}

========================
Job Description
========================

{description}

========================
Previous Email
========================

Subject:
{previous_subject}

Body:
{previous_email}

=========================================================
Instructions
=========================================================

The client has already received the previous email.

The client has NOT replied yet.

Do NOT rewrite or repeat the previous email.

Do NOT introduce yourself again.

Do NOT repeat the same opening sentence.

Assume the client has already read your previous email.

Instead:

• Briefly remind them about your previous outreach.

• Mention ONE additional reason why your experience matches the role.

• Reference one important requirement from the job description.

• Keep the tone professional, confident and friendly.

• Never sound desperate.

• Never guilt the client for not replying.

• Do not over-sell.

• Keep the email concise (60–90 words).

• End with a simple call-to-action like:
  "If this role is still open, I'd be happy to discuss how I can contribute."

• Sign off professionally.

• Do not use placeholders like
  [Your Name]
  [Company Name]

• Produce a completely new email.

• Do not copy sentences from the previous email.

Return ONLY the structured output.

{format_instructions}
""",
    input_variables=[
        "company",
        "job_title",
        "description",
        "previous_subject",
        "previous_email",
    ],
    partial_variables={
        "format_instructions": parser.get_format_instructions()
    },
)




