# import base64
# from pathlib import Path
# from email.message import EmailMessage

# from google.oauth2.credentials import Credentials
# from google.auth.transport.requests import Request
# from googleapiclient.discovery import build


# SCOPES = [
#     "https://www.googleapis.com/auth/gmail.send",
# ]


# class Gmail:
#     """
#     Gmail API Provider.
#     """

#     def __init__(self) -> None:

#         self.scopes = SCOPES

#     def get_gmail_service(self):

#         creds = Credentials.from_authorized_user_file(
#             "token.json",
#             self.scopes,
#         )

#         if creds.expired and creds.refresh_token:

#             creds.refresh(Request())

#             with open(
#                 "token.json",
#                 "w",
#             ) as token:

#                 token.write(
#                     creds.to_json()
#                 )

#         return build(
#             "gmail",
#             "v1",
#             credentials=creds,
#         )

#     def send_email(
#         self,
#         recipient: str,
#         subject: str,
#         body: str,
#         resume_path: str,
#     ) -> dict:

#         service = self.get_gmail_service()

#         message = EmailMessage()

#         message["To"] = recipient

#         message["Subject"] = subject

#         message.set_content(body)
#         print("i am adarsh dubey")
#         print(body)

#         # Attach Resume
       
#         resume = Path(resume_path)

#         with open(
#             resume,
#             "rb",
#         ) as file:

#             message.add_attachment(
#                 file.read(),
#                 maintype="application",
#                 subtype="pdf",
#                 filename=resume.name,
#             )


#         # Encode Message
      
#         encoded_message = base64.urlsafe_b64encode(
#             message.as_bytes()
#         ).decode()

#         result = (
#             service.users()
#             .messages()
#             .send(
#                 userId="me",
#                 body={
#                     "raw": encoded_message,
#                 },
#             )
#             .execute()
#         )

#         return {
#             "message_id": result["id"],
#             "thread_id": result["threadId"],
#         }




import base64
from pathlib import Path
from email.message import EmailMessage

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build


SCOPES = [
    "https://www.googleapis.com/auth/gmail.send",
]


def convert_to_html(plain_text: str) -> str:
    """
    Converts plain text (with \n\n between greeting/body/closing/signature)
    into HTML so Gmail renders the line breaks correctly instead of
    collapsing them.
    """
    paragraphs = plain_text.strip().split("\n\n")
    html_paragraphs = [
        "<p style='margin:0 0 16px 0;'>" + p.replace("\n", "<br>") + "</p>"
        for p in paragraphs
    ]
    body_html = "".join(html_paragraphs)

    return f"""\
<html>
  <body style="font-family: Arial, sans-serif; font-size: 14px; color: #202124;">
    {body_html}
  </body>
</html>
"""


class Gmail:
    """
    Gmail API Provider.
    """

    def __init__(self) -> None:

        self.scopes = SCOPES

    def get_gmail_service(self):

        creds = Credentials.from_authorized_user_file(
            "token.json",
            self.scopes,
        )

        if creds.expired and creds.refresh_token:

            creds.refresh(Request())

            with open(
                "token.json",
                "w",
            ) as token:

                token.write(
                    creds.to_json()
                )

        return build(
            "gmail",
            "v1",
            credentials=creds,
        )

    def send_email(
        self,
        recipient: str,
        subject: str,
        body: str,
        resume_path: str,
    ) -> dict:

        service = self.get_gmail_service()

        message = EmailMessage()

        message["To"] = recipient

        message["Subject"] = subject

        # Set the plain-text version first (fallback for clients that
        # don't render HTML).
        message.set_content(body)

        # Add the HTML version as an alternative. Gmail will render this
        # one, and it preserves the paragraph/line-break structure that
        # was being lost before.
        message.add_alternative(
            convert_to_html(body),
            subtype="html",
        )

        # Attach Resume
        resume = Path(resume_path)

        with open(
            resume,
            "rb",
        ) as file:

            message.add_attachment(
                file.read(),
                maintype="application",
                subtype="pdf",
                filename=resume.name,
            )

        # Encode Message
        encoded_message = base64.urlsafe_b64encode(
            message.as_bytes()
        ).decode()

        result = (
            service.users()
            .messages()
            .send(
                userId="me",
                body={
                    "raw": encoded_message,
                },
            )
            .execute()
        )

        return {
            "message_id": result["id"],
            "thread_id": result["threadId"],
        }