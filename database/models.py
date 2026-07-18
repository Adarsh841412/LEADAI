from datetime import date, datetime, time
import enum
from sqlalchemy.dialects.postgresql import JSONB

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Enum,
    Integer,
    String,
    Text,
    Time,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column
from database.db import Base



class LeadStatus(str, enum.Enum):
    NEW = "NEW"
    CONNECTED = "CONNECTED"
    OUTREACH_SENT = "OUTREACH_SENT"
    FOLLOWUP_SENT = "FOLLOWUP_SENT"
    REPLIED = "REPLIED"
    ASSESSMENT_PENDING = "ASSESSMENT_PENDING"
    MEETING_SCHEDULED = "MEETING_SCHEDULED"
    REJECTED = "REJECTED"


class EmailStatus(str,enum.Enum):
    PENDING = "PENDING"
    FOUND = "FOUND"
    VERIFIED = "VERIFIED"
    NOT_FOUND = "NOT_FOUND"
    FAILED = "FAILED"
    
class MeetingStatus(str, enum.Enum):
    SCHEDULED = "SCHEDULED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"




class Lead(Base):
    """
    Lead table.

    Stores the complete lifecycle of a lead from
    scraping to meeting scheduling.
    """

    __tablename__ = "leads"
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    
    job_id:Mapped[str]=mapped_column(
        String(40), nullable=False
    )
    company: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    job_title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    location: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    job_url: Mapped[str] = mapped_column(
        Text,
        unique=True,
        nullable=False,
    )

    platform: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    skills: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

   
    email: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    email_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    email_status:Mapped[EmailStatus | None ] = mapped_column(Enum(EmailStatus),default = EmailStatus.PENDING,nullable=False)
 
    status: Mapped[LeadStatus] = mapped_column(
        Enum(LeadStatus),
        default=LeadStatus.NEW,
        nullable=False,
    )
    company_domain: Mapped[str | None] = mapped_column(
    String(255),
    nullable=True,
)   
    
    rfc_message_id :Mapped[str|None] = mapped_column(
        String(255),
        nullable=True
    )
  
    thread_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    message_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )


    followup_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    last_contact_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )


    replied: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    
    conversation_processed: Mapped[bool] = mapped_column(
    Boolean,
    default=False,
    nullable=False,
)
    

    reply_received_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )


    meeting_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    meeting_time: Mapped[time | None] = mapped_column(
        Time,
        nullable=True,
    )

    meeting_status: Mapped[MeetingStatus | None] = mapped_column(
        Enum(MeetingStatus),
        nullable=True,
    )
    
    
    
    
    assesment_link:Mapped[str]=mapped_column(String(255),nullable=True)
    assessment_deadline:Mapped[date|None] = mapped_column(Date,nullable=True)
    
    
    
    timezone:Mapped[str|None]=mapped_column(String(50),nullable=True)
    meeting_link = mapped_column(Text, nullable=True)
    meeting_platform = mapped_column(Text,nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
 
    manual_review: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default=text("false"),
    )
    metadata_info:Mapped[dict]=mapped_column(JSONB,nullable=True)
    
    
  
    def __repr__(self) -> str:
        return (
            f"Lead("
            f"id={self.id}, "
            f"company='{self.company}', "
            f"job_title='{self.job_title}', "
            f"status='{self.status.value}'"
            f")"
        )
        
        
from database.db import init_db

init_db()         
