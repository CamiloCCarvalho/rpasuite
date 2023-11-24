import smtplib, os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from rpa_suite.log.printer import error_print, success_print
from rpa_suite.validate.mail_validator import email_validator

def send_email(
                email_from: str,
                pass_from: str,
                email_to: list[str],
                subject_title: str,
                body_message: str,
                attachments: list[str] = None,
                smtp_server: str = 'smtp.office365.com',
                smtp_port: int = 587
                ) -> dict:

    """
    Função responsavel por enviar emails ``(SMTP)``, aceita ``lista de destinatários`` e possibilidade
    de ``anexar arquivos``. \n
    
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

    # Variaveis locais
    by_smtp_result: dict = {
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
    
    # Pré Tratamentos
    by_smtp_result['success'] = False
    by_smtp_result['qt_mails_sent'] = 0
    by_smtp_result['attchament'] = False

    # Configuração inicial basica.
    msg = MIMEMultipart()
    msg['From'] = email_from
    msg['Subject'] = subject_title

    # Adicionar corpo da mensagem
    msg.attach(MIMEText(body_message, 'html'))

    # Adicionar anexos, se houver
    if attachments:
        by_smtp_result['attchament'] = True
        for path_to_attach in attachments:
            file_name = os.path.basename(path_to_attach)
            attachs = open(path_to_attach, 'rb')
            part = MIMEBase('application', 'octet-stream')
            part.set_payload((attachs).read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', "attachment; filename= %s" % file_name)
            msg.attach(part)
            by_smtp_result['qt_attach'] += 1
    else:
        by_smtp_result['attchament'] = False
        by_smtp_result['qt_attach'] = 0

    # Conectar ao servidor SMTP e enviar email
    try:
        server_by_smtp = smtplib.SMTP(smtp_server, smtp_port)
        server_by_smtp.starttls()
        server_by_smtp.login(email_from, pass_from)
        email_content = msg.as_string()

        try:  
            for emails in email_to:
                try:
                    v = email_validator.validate_email(emails)
                    email_valido.append(emails)

                except email_validator.EmailNotValidError:
                    email_invalido.append(emails)

        except Exception as e:
            error_print(f'Erro ao tentar validar lista de emails: {str(e)}')

        msg['To'] = ', '.join(email_valido)
        for email in email_valido:
            try:
                server_by_smtp.sendmail(email_from, email, email_content)
                by_smtp_result['qt_mails_sent'] += 1
                by_smtp_result['all_mails'] = email_to

            except smtplib.SMTPException as e:
                error_print(f'O email: {email} não foi enviado, por causa do erro: {str(e)}')

        server_by_smtp.quit()
        by_smtp_result['success'] = True
        success_print(f'Email(s) enviado(s) com sucesso!')
        

    except smtplib.SMTPException as e:
        by_smtp_result['success'] = False
        error_print(f'Erro ao enviar email(s): {str(e)}')

    # Pós Tratamento
    by_smtp_result['valid_mails'] = email_valido
    by_smtp_result['invalid_mails'] = email_invalido

    return by_smtp_result
