

# import base64
# from pathlib import Path
# from email.message import EmailMessage
# from google.oauth2.credentials import Credentials
# from google.auth.transport.requests import Request
# from googleapiclient.discovery import build,HttpError


# SCOPES = [
#     "https://www.googleapis.com/auth/gmail.send",
#     "https://www.googleapis.com/auth/gmail.readonly",
#     "https://www.googleapis.com/auth/gmail.modify",
    
# ]


# def convert_to_html(plain_text: str) -> str:
#     """
#     Converts plain text (with \n\n between greeting/body/closing/signature)
#     into HTML so Gmail renders the line breaks correctly instead of
#     collapsing them.
#     """
#     paragraphs = plain_text.strip().split("\n\n")
#     html_paragraphs = [
#         "<p style='margin:0 0 16px 0;'>" + p.replace("\n", "<br>") + "</p>"
#         for p in paragraphs
#     ]
#     body_html = "".join(html_paragraphs)

#     return f"""\
# <html>
#   <body style="font-family: Arial, sans-serif; font-size: 14px; color: #202124;">
#     {body_html}
#   </body>
# </html>
# """


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
#         resume_path: str | None = None 
#     ) -> dict:

#         service = self.get_gmail_service()

#         message = EmailMessage()

#         message["To"] = recipient

#         message["Subject"] = subject

#         # Set the plain-text version first (fallback for clients that
#         # don't render HTML).
#         message.set_content(body)

#         # Add the HTML version as an alternative. Gmail will render this
#         # one, and it preserves the paragraph/line-break structure that
#         # was being lost before.
#         message.add_alternative(
#             convert_to_html(body),
#             subtype="html",
#         )

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
        
        
        
#     # * part of followup workflow 
    
#     def check_reply(self,thread_id:str='19f51f1d72105eaf'):
#        """
#        it will check reply , and respond accordingly 
#        """
    
#        try : 
#         service = self.get_gmail_service() 
#         thread = service.users().threads().get(userId='me', id=thread_id).execute()
#         messages = thread.get('messages', [])
#         return {
#             "replied": len(messages) > 1,
#             "message_count": len(messages),
#             "messages": messages,
#         }
#        except HttpError as e:
#            print(f"invalid thread_id",{thread_id})  
#            return None 
       
            

#     def send_followup(
#         self,
#         to: str,
#         subject: str,
#         body: str,
#         thread_id: str,
#     ) -> dict | None:
#         """
#         Send a follow-up email in an existing Gmail thread.

#         Args:
#             to: Recipient email.
#             subject: Email subject.
#             body: Plain text email body.
#             thread_id: Gmail thread ID from the original outreach email.

#         Returns:
#             {
#                 "thread_id": "...",
#                 "message_id": "..."
#             }

#             Returns None if sending fails.
#         """

#         try:
#             # Step 1 : Gmail Service
#             service = self.get_gmail_service()
#             # Step 2 : Build Email
#             message = EmailMessage()

#             message["To"] = to
#             message["Subject"] = subject

#             # Plain text version
#             message.set_content(body)

#             # HTML version
#             message.add_alternative(
#                 convert_to_html(body),
#                 subtype="html",
#             )
#             # Step 3 : Encode Email
#             encoded_message = base64.urlsafe_b64encode(
#                 message.as_bytes()
#             ).decode()

#             # Step 4 : Send inside existing thread

#             result = (
#                 service.users()
#                 .messages()
#                 .send(
#                     userId="me",
#                     body={
#                         "raw": encoded_message,
#                         "threadId": thread_id,
#                     },
#                 )
#                 .execute()
#             )

#             # Step 5 : Return IDs

#             return {
#                 "thread_id": result["threadId"],
#                 "message_id": result["id"],
#             }

#         except HttpError as e:

#             print(f"Gmail API Error: {e}")

#             return None


        
        
        
        
        
import base64
from email.message import EmailMessage
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build, HttpError


SCOPES = [
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.modify",
]


def convert_to_html(plain_text: str) -> str:
    """
    Convert plain text to HTML while preserving paragraphs.
    """

    paragraphs = plain_text.strip().split("\n\n")

    html_paragraphs = [
        "<p style='margin:0 0 16px 0;'>"
        + p.replace("\n", "<br>")
        + "</p>"
        for p in paragraphs
    ]

    body_html = "".join(html_paragraphs)

    return f"""
<html>
  <body style="font-family: Arial, sans-serif; font-size:14px; color:#202124;">
    {body_html}
  </body>
</html>
"""


class Gmail:

    def __init__(self):

        self.scopes = SCOPES

    def get_gmail_service(self):

        creds = Credentials.from_authorized_user_file(
            "token.json",
            self.scopes,
        )

        if creds.expired and creds.refresh_token:

            creds.refresh(Request())

            with open("token.json", "w") as token:

                token.write(creds.to_json())

        return build(
            "gmail",
            "v1",
            credentials=creds,
        )

    # ---------------------------------------------------------
    # Send First Outreach Email
    # ---------------------------------------------------------

    def send_email(
    self,
    recipient: str,
    subject: str,
    body: str,
    resume_path: str | None = None,
) -> dict:

        service = self.get_gmail_service()

        message = EmailMessage()

        message["To"] = recipient
        message["Subject"] = subject

        message.set_content(body)

        message.add_alternative(
            convert_to_html(body),
            subtype="html",
        )
        if resume_path:

          resume = Path(resume_path)

          with open(resume, "rb") as file:

            message.add_attachment(
                file.read(),
                maintype="application",
                subtype="pdf",
                filename=resume.name,
            )

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

        # ---------------------------------------------
        # Fetch RFC Message-ID
        # ---------------------------------------------

        metadata = (
            service.users()
            .messages()
            .get(
                userId="me",
                id=result["id"],
                format="metadata",
                metadataHeaders=["Message-ID"],
            )
            .execute()
        )

        rfc_message_id = ""

        headers = metadata["payload"]["headers"]

        for header in headers:

            if header["name"].lower() == "message-id":

                rfc_message_id = header["value"]

                break

        return {
            "message_id": result["id"],
            "thread_id": result["threadId"],
            "rfc_message_id": rfc_message_id,
        }

    # ---------------------------------------------------------
    # Check Reply
    # ---------------------------------------------------------

    def check_reply(
        self,
        thread_id: str,
    ):

        try:

            service = self.get_gmail_service()

            thread = (
                service.users()
                .threads()
                .get(
                    userId="me",
                    id=thread_id,
                )
                .execute()
            )

            messages = thread.get(
                "messages",
                [],
            )

            return {
                "replied": len(messages) > 1,
                "message_count": len(messages),
                "messages": messages,
            }

        except HttpError:

            print(f"Invalid Thread ID : {thread_id}")

            return None

    # ---------------------------------------------------------
    # Send Follow-up
    # ---------------------------------------------------------

    def send_followup(
        self,
        to: str,
        subject: str,
        body: str,
        thread_id: str,
        rfc_message_id: str,
    ) -> dict | None:

        try:

            service = self.get_gmail_service()

            message = EmailMessage()

            message["To"] = to
            message["Subject"] = subject
            # Helps Gmail keep the same conversation
            message["In-Reply-To"] = rfc_message_id
            message["References"] = rfc_message_id

            message.set_content(body)

            message.add_alternative(
                convert_to_html(body),
                subtype="html",
            )

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
                        "threadId": thread_id,
                    },
                )
                .execute()
            )
            
            # Fetch RFC Message-ID
            metadata = (
                service.users()
                .messages()
                .get(
                    userId="me",
                    id=result["id"],
                    format="metadata",
                    metadataHeaders=["Message-ID"],
                )
                .execute()
            )

            rfc_message_id = ""

            headers = metadata["payload"]["headers"]

            for header in headers:

                if header["name"].lower() == "message-id":

                    rfc_message_id = header["value"]

                    break

            return {
                "thread_id": result["threadId"],
                "message_id": result["id"],
                'rfc_message_id':rfc_message_id
            }

        except HttpError as e:

            print(f"Gmail API Error: {e}")

            return None







