# rpa_suite/core/email.py

# imports internal
from rpa_suite.functions._printer import alert_print, error_print, success_print

# imports third-party
import smtplib
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders


class Email():
    
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
        ...     email_password="your_password",
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

    pt-br
    ----------
    Classe que fornece utilitários para envio de emails via protocolo SMTP.
    
    Esta classe oferece funcionalidades para:
        - Envio de emails com anexos
        - Formatação de mensagens em HTML
        - Configuração de servidor SMTP
        - Validação de email
        
    Métodos:
        send_smtp: Envia um email através do servidor SMTP especificado
        
    A classe Email é parte do RPA Suite e pode ser acessada através do objeto rpa:
        >>> from rpa_suite import rpa
        >>> rpa.email.send_smtp(
        ...     email_user="seu@email.com",
        ...     email_password="sua_senha",
        ...     email_to="destino@email.com",
        ...     subject_title="Teste",
        ...     body_message="<p>Mensagem de teste</p>"
        ... )
    """


    smtp_server:str = "smtp.hostinger.com",
    smtp_port:str = 465,
    email_user:str = "your_email@email.com",
    email_password:str = "password",
    email_to: str = "to@email.com",
    attachments: list[str] = [],
    subject_title: str = 'Test title',
    body_message: str = '<p>Testing message body</p>'
    auth_tls: bool = False,


    def __init__(self):
        ...

    def send_smtp(
        self,
        email_user:str,
        email_password:str,
        email_to: str,
        subject_title: str = 'Test title',
        body_message: str = '<p>Testing message body</p>',
        attachments: list[str] = [],
        smtp_server:str = "smtp.hostinger.com",
        smtp_port:str = 465,
        auth_tls: bool = False,
        display_message: bool = True,
        ):

        """
        Sends an email using the specified SMTP server.

        Args:
            smtp_server (str, optional): Address of the SMTP server. 
                Default: "smtp.hostinger.com".
            smtp_port (str, optional): Port of the SMTP server. 
                Default: 465.
            email_user (str, optional): User (email) for authentication on the SMTP server. 
                Default: "example@email.com".
            email_password (str, optional): Password for authentication on the SMTP server. 
                Default: "example123".
            email_to (str, optional): Email address of the recipient. 
                Default: "person@email.com".
            attachments (list[str], optional): List of file paths to attach to the email. 
                Default: [].
            subject_title (str, optional): Title (subject) of the email. 
                Default: 'test title'.
            body_message (str, optional): Body of the email message, in HTML format. 
                Default: '<p>test message</p>'.

        Returns:
            None: This function does not explicitly return any value, but prints success or failure messages when sending the email.
        
        pt-br
        ------
        
        Envia um email usando o servidor SMTP especificado.

        Args:
            smtp_server (str, opcional): Endereço do servidor SMTP. 
                Padrão: "smtp.hostinger.com".
            smtp_port (str, opcional): Porta do servidor SMTP. 
                Padrão: 465.
            email_user (str, opcional): Usuário (email) para autenticação no servidor SMTP. 
                Padrão: "example@email.com".
            email_password (str, opcional): Senha para autenticação no servidor SMTP. 
                Padrão: "example123".
            email_to (str, opcional): Endereço de email do destinatário. 
                Padrão: "person@email.com".
            attachments (list[str], opcional): Lista de caminhos de arquivos para anexar ao email. 
                Padrão: [].
            subject_title (str, opcional): Título (assunto) do email. 
                Padrão: 'título de teste'.
            body_message (str, opcional): Corpo da mensagem do email, em formato HTML. 
                Padrão: '<p>mensagem de teste</p>'.

        Returns:
            Nenhum: Esta função não retorna explicitamente nenhum valor, mas imprime mensagens de sucesso ou falha ao enviar o email.
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

            # Criando a mensagem
            msg = MIMEMultipart()
            msg['From'] = self.email_user
            msg['To'] = ', '.join(self.email_to) if isinstance(self.email_to, list) else self.email_to
            msg['Subject'] = str(self.subject_title)

            # Corpo do e-mail
            body = str(self.body_message)
            msg.attach(MIMEText(body, 'html'))

            # Anexos (opcional)
            if self.attachments:
                from email.mime.base import MIMEBase
                from email import encoders
                import os

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
                        error_print(f"Erro ao anexar o arquivo {attachment_path}: {str(e)}")

            try:
                if self.auth_tls:
                    # Conectando ao servidor SMTP com TLS
                    server = smtplib.SMTP(self.smtp_server, self.smtp_port)
                    server.starttls()
                    server.login(self.email_user, self.email_password)
                else:
                    # Conectando ao servidor SMTP com SSL
                    server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port)
                    server.login(self.email_user, self.email_password)

                # Enviando o e-mail
                server.sendmail(self.email_user, self.email_to, msg.as_string())
                if display_message: success_print("E-mail enviado com sucesso!")

                # Encerrando a conexão
                server.quit()

            except Exception as e:
                alert_print(f"Falha ao enviar o e-mail: {str(e)}")

        except Exception as e:
            error_print(f"Ocorreu um erro geral na função sendmail: {str(e)}")
