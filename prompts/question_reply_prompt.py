from pydantic import BaseModel, Field
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser


class RecruiterReply(BaseModel):

    email_message: str = Field(
        description="Professional email reply."
    )


parser = PydanticOutputParser(
    pydantic_object=RecruiterReply,
)


prompt = PromptTemplate(
    template="""
You are an experienced software engineer replying to recruiters.

Write a professional email reply.

Subject:
{subject}

Recruiter Message:
{email}

Instructions:

- Answer every recruiter question politely.
- Keep the tone professional.
- Do not invent personal information.
- If information is unavailable, politely say it can be discussed during the interview.
- Keep the reply concise.
- Return ONLY the structured output.

{format_instructions}
""",
    input_variables=[
        "subject",
        "email",
    ],
    partial_variables={
        "format_instructions": parser.get_format_instructions(),
    },
)