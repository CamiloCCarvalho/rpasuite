# rpa_suite/core/email.py

# imports standard
import os
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# imports internal
from rpa_suite.functions._printer import success_print


class EmailError(Exception):
    """Custom exception for Email errors."""

    def __init__(self, message):
        clean_message = message.replace("EmailError:", "").strip()
        super().__init__(f"EmailError: {clean_message}")


class Email:
    """
    Class that provides utilities for sending emails via SMTP protocol.

    This class offers functionalities for:
        - Sending emails with attachments
        - HTML message formatting
        - SMTP server configuration
        - Email validation

    Methods:
        send_smtp: Sends an email through specified SMTP server

    The Email class is part of RPA Suite and can be accessed through the rpa object:
        >>> from rpa_suite import rpa
        >>> rpa.email.send_smtp(
        ...     email_user="your@email.com",
        ...     email_password="123",
        ...     email_to="destination@email.com",
        ...     subject_title="Test",
        ...     body_message="<p>Test message</p>"
        ... )
    """

    smtp_server: str = ("smtp.hostinger.com",)
    smtp_port: str = (465,)
    email_user: str = ("your_email@email.com",)
    email_password: str = ("password",)
    email_to: str = ("to@email.com",)
    attachments: list[str] = ([],)
    subject_title: str = ("Test title",)
    body_message: str = "<p>Testing message body</p>"
    auth_tls: bool = (False,)

    def __init__(self) -> None:
        """
        Constructor function for the Email class that provides utilities for email management.

        This class offers functionalities for sending emails via SMTP protocol with support
        for attachments, HTML formatting, and various SMTP server configurations.
        """

    def send_smtp(  # pylint: disable=too-many-positional-arguments,too-many-locals
        self,
        email_user: str,
        email_password: str,
        email_to: str,
        subject_title: str = "Test title",
        body_message: str = "<p>Testing message body</p>",
        attachments: list[str] | None = None,
        smtp_server: str = "smtp.hostinger.com",
        smtp_port: str = 465,
        auth_tls: bool = False,
        verbose: bool = True,
    ):
        """
        Sends an email using the specified SMTP server.

        Parameters:
        -----------
        email_user : str
            User (email) for authentication on the SMTP server.

        email_password : str
            Password for authentication on the SMTP server.

        email_to : str | list[str]
            Email address(es) of the recipient(s). Can be a single email or a list of emails.

        subject_title : str, optional
            Title (subject) of the email. Default: "Test title".

        body_message : str, optional
            Body of the email message, in HTML format. Default: "<p>Testing message body</p>".

        attachments : list[str] | None, optional
            List of file paths to attach to the email. Default: None.

        smtp_server : str, optional
            Address of the SMTP server. Default: "smtp.hostinger.com".

        smtp_port : str | int, optional
            Port of the SMTP server. Default: 465.

        auth_tls : bool, optional
            Whether to use TLS authentication instead of SSL. Default: False.

        verbose : bool, optional
            Whether to print success messages. Default: True.

        Returns:
        --------
        None
            This function does not explicitly return any value, but prints success or failure
            messages when sending the email (if verbose=True).

        Raises:
        -------
        EmailError
            If there is an error sending the email or attaching files.
        """

        try:
            self.smtp_server = smtp_server
            self.smtp_port = smtp_port
            self.email_user = email_user
            self.email_password = email_password
            self.email_to = email_to
            self.subject_title = subject_title
            self.body_message = body_message
            self.attachments = attachments
            self.auth_tls = auth_tls

            # Creating the message
            msg = MIMEMultipart()
            msg["From"] = self.email_user
            msg["To"] = ", ".join(self.email_to) if isinstance(self.email_to, list) else self.email_to
            msg["Subject"] = str(self.subject_title)

            # Email body
            body = str(self.body_message)
            msg.attach(MIMEText(body, "html"))

            # Attachments (optional)
            if self.attachments:
                for attachment_path in self.attachments:
                    try:
                        with open(attachment_path, "rb") as attachment:
                            part = MIMEBase("application", "octet-stream")
                            part.set_payload(attachment.read())
                            encoders.encode_base64(part)
                            part.add_header(
                                "Content-Disposition",
                                f"attachment; filename= {os.path.basename(attachment_path)}",
                            )
                            msg.attach(part)

                    except Exception as e:
                        raise EmailError(f"Error attaching file {attachment_path}: {str(e)}") from e

            try:
                if self.auth_tls:
                    # Connecting to SMTP server with TLS
                    server = smtplib.SMTP(self.smtp_server, self.smtp_port)
                    server.starttls()
                    server.login(self.email_user, self.email_password)
                else:
                    # Connecting to SMTP server with SSL
                    server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port)
                    server.login(self.email_user, self.email_password)

                # Sending the email
                server.sendmail(self.email_user, self.email_to, msg.as_string())
                if verbose:
                    success_print("Email sent successfully!")

                # Closing the connection
                server.quit()

            except Exception as e:
                raise EmailError(f"Failed to send email: {str(e)}") from e

        except Exception as e:
            raise EmailError(f"A general error occurred in the sendmail function: {str(e)}") from e
