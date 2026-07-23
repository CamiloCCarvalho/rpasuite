# rpa_suite/core/email.py

# imports standard
import os
import smtplib
import warnings
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# imports internal
from rpa_suite.functions._printer import alert_print, success_print


class EmailError(Exception):
    """Custom exception for Email errors."""

    def __init__(self, message):
        clean_message = message.replace("EmailError:", "").strip()
        super().__init__(f"EmailError: {clean_message}")


def _resolve_smtp_password(
    email_password: str | None,
    password_from_env: str | None,
) -> str:
    """Resolve the SMTP password without storing it on the Email instance."""
    if password_from_env:
        env_password = os.getenv(password_from_env)
        if env_password is None:
            raise EmailError(
                f"Environment variable '{password_from_env}' not found. "
                "Please set the environment variable or provide email_password directly."
            )
        return env_password

    if email_password is not None:
        warnings.warn(
            "Passing email_password directly is deprecated for security reasons. "
            "Use password_from_env parameter to read password from environment variable instead.",
            DeprecationWarning,
            stacklevel=3,
        )
        return email_password

    raise EmailError(
        "No password provided. Please provide either email_password parameter "
        "or use password_from_env to read from environment variable."
    )


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

    Parameters:
        smtp_server (str): SMTP server address
        smtp_port (str): SMTP server port
        email_user (str): Email for SMTP authentication
        email_password (str): Password for SMTP authentication
        email_to (str): Recipient email address
        attachments (list[str]): List of file paths to attach
        subject_title (str): Email subject
        body_message (str): Email body in HTML format
        auth_tls (bool): Whether to use TLS authentication

    """

    smtp_server: str = "smtp.hostinger.com"
    smtp_port: int | str = 465
    email_user: str | None = None
    email_to: str | None = None
    attachments: list[str] | None = None
    subject_title: str = "Test title"
    body_message: str = "<p>Testing message body</p>"
    auth_tls: bool = False

    def __init__(self) -> None:
        """
        Constructor function for the Email class that provides utilities for email management.

        This class offers functionalities for sending emails via SMTP protocol with support
        for attachments, HTML formatting, and various SMTP server configurations.
        """

    def send_smtp(  # pylint: disable=too-many-positional-arguments,too-many-locals
        self,
        email_user: str,
        email_to: str,
        email_password: str | None = None,
        subject_title: str = "Test title",
        body_message: str = "<p>Testing message body</p>",
        attachments: list[str] | None = None,
        smtp_server: str = "smtp.hostinger.com",
        smtp_port: str = 465,
        auth_tls: bool = False,
        verbose: bool = True,
        password_from_env: str | None = None,
    ):
        """
        Sends an email using the specified SMTP server.

        Args:
            email_user (str): User (email) for authentication on the SMTP server.
            email_to (str): Email address of the recipient.
            email_password (str, optional): Password for authentication on the SMTP server.
                If not provided and password_from_env is not set, a deprecation warning is issued.
                Default: None.
            password_from_env (str, optional): Name of environment variable containing the password.
                If provided, the password is read from the environment variable instead of email_password.
                This is the recommended approach for security.
                Default: None.
            subject_title (str, optional): Title (subject) of the email.
                Default: 'test title'.
            body_message (str, optional): Body of the email message, in HTML format.
                Default: '<p>test message</p>'.
            attachments (list[str], optional): List of file paths to attach to the email.
                Default: None.
            smtp_server (str, optional): Address of the SMTP server.
                Default: "smtp.hostinger.com".
            smtp_port (str, optional): Port of the SMTP server.
                Default: 465.
            auth_tls (bool, optional): Whether to use TLS authentication.
                Default: False.
            verbose (bool, optional): Whether to print success messages.
                Default: True.

        Returns:
            None: This function does not explicitly return any value,
            but prints success or failure messages when sending the email.

        Raises:
            EmailError: If email_password is not provided and password_from_env is not set.

        """

        try:
            self.smtp_server = smtp_server
            self.smtp_port = smtp_port
            self.email_user = email_user
            self.email_to = email_to
            self.subject_title = subject_title
            self.body_message = body_message
            self.attachments = attachments
            self.auth_tls = auth_tls

            smtp_password = _resolve_smtp_password(email_password, password_from_env)

            # Creating the message
            msg = MIMEMultipart()
            msg["From"] = email_user
            msg["To"] = ", ".join(email_to) if isinstance(email_to, list) else email_to
            msg["Subject"] = str(subject_title)

            # Email body
            body = str(body_message)
            msg.attach(MIMEText(body, "html"))

            # Attachments (optional)
            if attachments:
                for attachment_path in attachments:
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
                if auth_tls:
                    server = smtplib.SMTP(smtp_server, smtp_port)
                    server.starttls()
                    server.login(email_user, smtp_password)
                else:
                    server = smtplib.SMTP_SSL(smtp_server, smtp_port)
                    server.login(email_user, smtp_password)

                server.sendmail(email_user, email_to, msg.as_string())
                if verbose:
                    success_print("Email sent successfully!")

                server.quit()

            except Exception as e:
                raise EmailError(f"Failed to send email: {str(e)}") from e

        except Exception as e:
            raise EmailError(f"A general error occurred in the sendmail function: {str(e)}") from e
        finally:
            if "smtp_password" in locals():
                smtp_password = ""
