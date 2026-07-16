from langchain_core.prompts import PromptTemplate 
from langchain_core.output_parsers import PydanticOutputParser 
from pydantic import BaseModel,Field 
from langchain_core.prompts import PromptTemplate

from pydantic import BaseModel, Field
from typing import Optional


class ConversationResponse(BaseModel):

    intent: str = Field(
        description="MEETING, QUESTION, ASSESSMENT, GENERAL_REPLY, REJECTION or UNKNOWN."
    )

    meeting_date: Optional[str] = Field(
        default=None,
        description="Interview date if available."
    )

    meeting_time: Optional[str] = Field(
        default=None,
        description="Interview time if available."
    )

    timezone: Optional[str] = Field(
        default=None,
        description="Meeting timezone if available."
    )

    reply_required: bool = Field(
        description="Whether the recruiter expects a response."
    )




parser = PydanticOutputParser(pydantic_object=ConversationResponse) 


prompt = PromptTemplate(
    template="""
You are an AI Recruitment Conversation Analyzer.

Your job is to analyze the latest email received from a recruiter.

The email belongs to an ongoing hiring conversation.

-----------------------------
Recruiter Email
-----------------------------

Subject:
{subject}

Email:
{email}

-----------------------------
Your Tasks
-----------------------------

1. Determine the primary intent of the recruiter.

Choose ONLY ONE of the following intents:

- MEETING
- QUESTION
- ASSESSMENT
- GENERAL_REPLY
- REJECTION
- UNKNOWN

Definitions:

MEETING
The recruiter is scheduling, confirming, rescheduling, or discussing an interview or meeting.

QUESTION
The recruiter is asking for information such as:
- Notice period
- Current CTC
- Expected CTC
- Years of experience
- Availability
- Location
- Visa status
- Any direct question requiring a response.

ASSESSMENT
The recruiter is asking the candidate to complete:
- Coding test
- Online assessment
- HackerRank
- Take-home assignment
- Technical challenge

GENERAL_REPLY
A normal recruiter reply that does not require meeting extraction.

Examples:
- Thank you.
- We will review your profile.
- We'll get back to you soon.

REJECTION
The recruiter has rejected the application.

UNKNOWN
The email does not clearly belong to any category.

-----------------------------
Meeting Extraction
-----------------------------

If the intent is MEETING, extract:

- meeting_date
- meeting_time
- timezone

If they are not mentioned,
return null.

-----------------------------
Reply Required
-----------------------------

Determine whether the recruiter expects a reply.

Return:

true

or

false

Examples:

Question
→ true

Meeting Confirmation
→ false

General acknowledgement
→ false

Assessment invitation
→ true

-----------------------------
Important Rules
-----------------------------

- Analyze ONLY the recruiter's email.
- Never invent information.
- Never guess missing meeting details.
- If a value is unavailable, return null.
- Return ONLY the structured output.
- Do not explain your reasoning.

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


