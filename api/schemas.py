from typing import Annotated
from enum import Enum

from pydantic import BaseModel, Field


class Platform(str, Enum):
    LINKEDIN = "linkedin"
    INDEED = "indeed"
    GLASSDOOR = "glassdoor"


class LeadGenerationRequest(BaseModel):

    job_title: Annotated[
        str,
        Field(
            description="Enter your job title",
            examples=["Python Developer"],
        ),
    ]

    location: Annotated[
        str,
        Field(
            description="Enter your country code (e.g. US, IN)",
            examples=["US"],
        ),
    ]

    platform: Annotated[
        Platform,
        Field(
            description="Select the platform",
            examples=["linkedin"],
        ),
    ]