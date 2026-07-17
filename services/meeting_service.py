from datetime import datetime
from database.models import MeetingStatus
import re 

class MeetingService:

    DATE_FORMATS = (
        "%A, %d %B %Y",   # Tuesday, 28 July 2026
        "%d %B %Y",       # 28 July 2026
        "%d/%m/%Y",       # 28/07/2026
        "%Y-%m-%d",       # 2026-07-28
    )

    TIME_FORMATS = (
    "%I:%M %p",   # 3:30 PM
    "%I %p",      # 3 PM
    "%H:%M",      # 15:30
)

    def validate_meeting(
        self,
        meeting_date: str | None,
        meeting_time: str | None,
        timezone: str | None,
        meeting_link:str|None = None ,
        meeting_platform:str|None = None ,
    ) -> dict | None:
        """
        Validate and normalize meeting details.

        Returns:
            dict | None
        """

        if not meeting_date:
            print("Meeting date not found.")
            return None

        if not meeting_time:
            print("Meeting time not found.")
            return None

        if not timezone:
            print("Timezone not found.")
            return None

        parsed_date = self._parse_date(meeting_date)

        if parsed_date is None:
            print("Invalid meeting date format.")
            return None

        parsed_time = self._parse_time(meeting_time)

        if parsed_time is None:
            print("Invalid meeting time format.")
            return None

        return {
            "meeting_date": parsed_date,
            "meeting_time": parsed_time,
            "timezone": timezone.strip(),
            "meeting_link":meeting_link,
            "meeting_platform":meeting_platform,
            "meeting_status": MeetingStatus.SCHEDULED,
        }

    def _parse_date(self, meeting_date: str):
        """
        Parse meeting date using supported formats.
        """

        meeting_date = meeting_date.strip()

        for fmt in self.DATE_FORMATS:

            try:
                return datetime.strptime(
                    meeting_date,
                    fmt,
                ).date()

            except ValueError:
                continue

        return None



    def _parse_time(self, meeting_time: str):
        """
        Parse meeting time.

        Supports:
        - 3:30 PM
        - 3 PM
        - 15:30
        - 3:30 PM – 4:00 PM
        - 3:30 PM - 4:00 PM
        """

        meeting_time = meeting_time.strip()

        # Normalize different dash characters
        meeting_time = (
            meeting_time
            .replace("–", "-")
            .replace("—", "-")
            .replace("−", "-")
        )

        # If it's a time range, keep only the start time
        meeting_time = re.split(r"\s*-\s*", meeting_time)[0].strip()

        print(f"Normalized Time: {meeting_time}")   # Optional for debugging

        # Parse using all supported formats
        for fmt in self.TIME_FORMATS:
            try:
                return datetime.strptime(
                    meeting_time,
                    fmt,
                ).time()

            except ValueError:
                continue

        return None