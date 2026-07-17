from typing import Optional

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field


class ConversationResponse(BaseModel):

    # --------------------------------------------------
    # Intent
    # --------------------------------------------------

    intent: str = Field(
        description="One of: MEETING, QUESTION, ASSESSMENT, GENERAL_REPLY, REJECTION, UNKNOWN."
    )

    # --------------------------------------------------
    # Meeting
    # --------------------------------------------------

    meeting_date: Optional[str] = Field(
        default=None,
        description="Meeting or interview date exactly as mentioned by the recruiter."
    )

    meeting_time: Optional[str] = Field(
        default=None,
        description="Meeting time exactly as mentioned by the recruiter. If a time range is provided, return the complete range exactly as written."
    )

    timezone: Optional[str] = Field(
        default=None,
        description="Meeting timezone exactly as mentioned by the recruiter."
    )

    meeting_link: Optional[str] = Field(
        default=None,
        description="Video meeting URL if present (Google Meet, Microsoft Teams, Zoom, Webex, etc.)."
    )

    meeting_platform: Optional[str] = Field(
        default=None,
        description="Meeting platform if identifiable (Google Meet, Microsoft Teams, Zoom, Webex, Phone, etc.)."
    )

    # --------------------------------------------------
    # Assessment
    # --------------------------------------------------

    assessment_link: Optional[str] = Field(
        default=None,
        description="Assessment URL if present."
    )

    assessment_deadline: Optional[str] = Field(
        default=None,
        description="Assessment deadline exactly as mentioned."
    )

    # --------------------------------------------------
    # Conversation
    # --------------------------------------------------

    reply_required: bool = Field(
        description="Whether the recruiter expects a reply."
    )


parser = PydanticOutputParser(
    pydantic_object=ConversationResponse
)


prompt = PromptTemplate(
    template="""
You are an AI Recruitment Conversation Analyzer.

Your task is to analyze ONLY the latest recruiter email from an ongoing hiring conversation.

Ignore all previous emails, quoted replies, forwarded messages, signatures, and email history.

========================================================
Recruiter Email
========================================================

Subject:
{subject}

Email:
{email}

========================================================
Task 1 — Intent Classification
========================================================

Choose EXACTLY ONE intent.

Allowed values:

- MEETING
- QUESTION
- ASSESSMENT
- GENERAL_REPLY
- REJECTION
- UNKNOWN

Definitions

MEETING

The recruiter is:

- scheduling an interview
- confirming an interview
- rescheduling an interview
- cancelling an interview
- sharing interview logistics
- sending interview instructions

QUESTION

The recruiter asks the candidate for information.

Examples:

- Notice period
- Current salary
- Expected salary
- Current CTC
- Expected CTC
- Years of experience
- Availability
- Current location
- Visa status
- Portfolio
- Resume
- Any direct question requiring a response

ASSESSMENT

The recruiter asks the candidate to complete:

- HackerRank
- Codility
- HackerEarth
- CodeSignal
- TestDome
- Mercer Mettl
- Technical Assessment
- Coding Challenge
- Online Test
- Take-home Assignment

GENERAL_REPLY

General recruiter communication.

Examples:

- Thank you.
- We received your application.
- We'll review your profile.
- We'll contact you soon.
- Thanks for your interest.

REJECTION

The recruiter informs the candidate that they are no longer being considered.

UNKNOWN

The email cannot be confidently classified.

========================================================
Task 2 — Meeting Extraction
========================================================

ONLY if intent == MEETING.

Extract:

- meeting_date
- meeting_time
- timezone
- meeting_link
- meeting_platform

Rules

Return values EXACTLY as written.

Do NOT normalize.

Examples

Date

Tuesday, 28 July 2026

Return

meeting_date = "Tuesday, 28 July 2026"

----------------------------------------

28 July 2026

Return

meeting_date = "28 July 2026"

----------------------------------------

Time

3:30 PM – 4:00 PM

Return

meeting_time = "3:30 PM – 4:00 PM"

----------------------------------------

10:00 AM

Return

meeting_time = "10:00 AM"

----------------------------------------

Timezone

Asia/Kolkata (IST)

Return

timezone = "Asia/Kolkata (IST)"

----------------------------------------

Google Meet

Join Google Meet

https://meet.google.com/abc-defg-hij

Return

meeting_platform = "Google Meet"

meeting_link = "https://meet.google.com/abc-defg-hij"

----------------------------------------

Microsoft Teams

Join Microsoft Teams Meeting

https://teams.microsoft.com/l/meetup-join/...

Return

meeting_platform = "Microsoft Teams"

meeting_link = "https://teams.microsoft.com/l/meetup-join/..."

----------------------------------------

Zoom

https://zoom.us/j/123456789

Return

meeting_platform = "Zoom"

meeting_link = "https://zoom.us/j/123456789"

----------------------------------------

Phone Interview

"We will call you on your registered mobile number."

Return

meeting_platform = "Phone"

meeting_link = null

----------------------------------------

If any meeting field is unavailable,

return null.

Never invent a meeting link.

Never generate a URL.

========================================================
Task 3 — Assessment Extraction
========================================================

ONLY if intent == ASSESSMENT.

Extract

- assessment_link
- assessment_deadline

Rules

Return values exactly as written.

The assessment link should point to the assessment platform.

Examples include

- HackerRank
- Codility
- HackerEarth
- CodeSignal
- TestDome
- Mercer Mettl
- Qualified.io

Never confuse an assessment URL with a meeting URL.

If unavailable,

return null.

========================================================
Task 4 — Reply Required
========================================================

Return true ONLY if the recruiter expects the candidate to respond.

Examples

QUESTION

→ true

----------------------------------------

ASSESSMENT

→ true

----------------------------------------

MEETING REQUEST

"Please confirm your availability."

→ true

----------------------------------------

MEETING CONFIRMATION

"Your interview has been scheduled."

→ false

----------------------------------------

GENERAL_REPLY

→ false

----------------------------------------

REJECTION

→ false

========================================================
Rules
========================================================

- Analyze ONLY the latest recruiter email.
- Ignore quoted emails.
- Ignore previous conversation.
- Never invent information.
- Never infer missing values.
- Never guess dates.
- Never guess meeting times.
- Never guess timezones.
- Never guess URLs.
- Never create meeting links.
- Never create assessment links.
- Extract URLs exactly as written.
- Do not confuse assessment links with meeting links.
- If a field is unavailable, return null.
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