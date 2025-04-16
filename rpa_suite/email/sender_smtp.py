# /sender_smtp.py

import smtplib, os
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from rpa_suite.log.printer import alert_print, error_print, success_print
from rpa_suite.validate.mail_validator import email_validator

def send_email(
                email_from: str,
                pass_from: str,
                email_to: list[str],
                subject_title: str,
                body_message: str,
                image_footer: str = None,
                attachments: list[str] = None,
                type_content: str = 'html',
                smtp_server: str = 'smtp.office365.com',
                smtp_port: int = 587,
                authentication_tls: bool = True, 
                ) -> dict:

    """
    Function responsible for sending emails ``(SMTP)``, accepts ``list of recipients`` and possibility
    of ``attaching files``. \n
    
    Parameters:
    ----------
    ``email_from: str`` - email from who will send the email.
    ``pass_from: str`` - password of the account used, advised to isolate the password elsewhere.
    ``email_to: list[str]`` - list of emails to which the emails will be sent.
    ``subject_title: str`` - email title.
    ``body_message: str``- body message of the email.
    ``image_footer: str`` - image footer of body message of the email.
    ``attachments: list[str]`` - list with path of attachments if any. (default None).
    ``type_content: str`` - type of message content can be 'plain' or 'html' (default 'html').
    ``smtp_server: str`` - server to be used to connect with the email account (default 'smtp.office365.com')
    ``smtp_port: int`` - port to be used on this server (default 587 - TLS), commum use 465 for SSL authentication 
    ``authentication_tls: bool`` - authentication method (default True), if False use SSL authentication
    
    Return:
    ----------
    >>> type:dict
    a dictionary with all information that may be necessary about the emails.
    Respectively being:
        * 'success': bool -  if there was at least one successful shipment
        * 'all_mails': list - list of all emails parameterized for sending
        * 'valid_mails': list - list of all valid emails for sending
        * 'invalid_mails': list - list of all invalid emails for sending
        * 'qt_mails_sent': int - effective quantity that was sent
        * 'attchament': bool - if there are attachments
        * 'qt_attach': int - how many attachments were inserted
        
    Description: pt-br
    ----------
    Função responsavel por enviar emails ``(SMTP)``, aceita ``lista de destinatários`` e possibilidade
    de ``anexar arquivos``. \n
    
    Parametros:
    ----------
    ``email_from: str`` - email de quem ira enviar o email.
    ``pass_from: str`` - senha da conta utilizada, aconselhado isolar a senha em outro local.
    ``email_to: list[str]`` - lista de emails para os quais serão enviados os emails.
    ``subject_title: str`` - titulo do email.
    ``body_message: str``- mensagem do corpo do email.
    ``image_footer: str`` - imagem de rodapé do corpo do email.
    ``attachments: list[str]`` - lista com caminho de anexos se houver. (default None).
    ``type_content: str`` - tipo de conteudo da mensagem pode ser 'plain' ou 'html' (default 'html').
    ``smtp_server: str`` - servidor a ser utilizado para conectar com a conta de email (default 'smtp.office365.com')
    ``smtp_port: int`` - porta a ser utilizada nesse servidor (default 587 - TLS), comum usar 465 para autenticação por SSL 
    ``authentication_tls: bool`` - metódo de autenticação (default True), caso Falso usa autenticação por SSL
    
    Retorno:
    ----------
    >>> type:dict
    um dicionário com todas informações que podem ser necessarias sobre os emails.
    Sendo respectivamente:
        * 'success': bool -  se houve pelo menos um envio com sucesso
        * 'all_mails': list - lista de todos emails parametrizados para envio
        * 'valid_mails': list - lista de todos emails validos para envio
        * 'invalid_mails': list - lista de todos emails invalidos para envio
        * 'qt_mails_sent': int - quantidade efetiva que foi realizado envio
        * 'attchament': bool - se há anexos
        * 'qt_attach': int - quantos anexos foram inseridos
    """

    # Local Variables
    result: dict = {
        'success': bool,
        'all_mails': list,
        'valid_mails': list,
        'invalid_mails': list,
        'qt_mails_sent': int,
        'attchament': bool,
        'qt_attach': int
    }
    email_valido = []
    email_invalido = []
    
    # Preprocessing
    result['success'] = False
    result['qt_mails_sent'] = 0
    result['attchament'] = False

    msg = MIMEMultipart()
    msg['From'] = email_from
    msg['Subject'] = subject_title

    # Email Body Content
    msg.attach(MIMEText(body_message, type_content))
    
    # Add image Footer 
    if image_footer:
        try:
            with open(image_footer, 'rb') as img:
                msg_image = MIMEImage(img.read())
                msg_image.add_header('Content-ID', '<logo>')
                # Notice: Content-ID correlact at "cid" on tag <img> at body mail
                msg.attach(msg_image)
        except FileNotFoundError as e:
            alert_print(f'File Not Found! Error: {str(e)}')
        except Exception as e:
            error_print(f'An Error ocurred, during set image: <{image_footer}> as MIMEImage! Error: {str(e)}')
            
    # Add Attachment
    if attachments:
        result['qt_attach'] = 0
        result['attchament'] = True
        for path_to_attach in attachments:
            file_name = os.path.basename(path_to_attach)
            attachs = open(path_to_attach, 'rb')
            part = MIMEBase('application', 'octet-stream')
            part.set_payload((attachs).read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', "attachment; filename= %s" % file_name)
            msg.attach(part)
            result['qt_attach'] += 1
    else:
        result['attchament'] = False
        result['qt_attach'] = 0

    # SMTP server config
    try:
        
        # authentication TLS True -> Using TLS
        if authentication_tls:
            
            server_by_smtp = smtplib.SMTP(smtp_server, smtp_port)
            server_by_smtp.starttls()
            server_by_smtp.login(email_from, pass_from)
            email_content = msg.as_string()
            
        else: # authentication TLS False -> Using SSL
            
            # connect SMTP server using SSL
            server_by_smtp = smtplib.SMTP_SSL(smtp_server, smtp_port)
            server_by_smtp.login(email_from, pass_from)
            email_content = msg.as_string()
            
        # Treats the email list before trying to send, keeping only valid emails
        try:  
            for emails in email_to:
                try:
                    v = email_validator.validate_email(emails)
                    email_valido.append(emails)

                except email_validator.EmailNotValidError:
                    email_invalido.append(emails)

        except Exception as e:
            error_print(f'Error while trying to validate email list: {str(e)}')

        # Attaches the treated email list to perform the sending
        msg['To'] = ', '.join(email_valido)
        for email in email_valido:
            try:
                server_by_smtp.sendmail(email_from, email, email_content)
                result['qt_mails_sent'] += 1
                result['all_mails'] = email_to

            except smtplib.SMTPException as e:
                error_print(f"The email: {email} don't sent, caused by error: {str(e)}")

        #server_by_smtp.quit()
        result['success'] = True
        success_print(f'Email(s) Sent!')


    except smtplib.SMTPException as e:
        result['success'] = False
        error_print(f'Error while trying sent Email: {str(e)}')
        
    finally:
        server_by_smtp.quit()

    # Postprocessing
    result['valid_mails'] = email_valido
    result['invalid_mails'] = email_invalido

    return result
