import smtplib, os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

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
    
    
    # Pré Tratamentos
    by_smtp_result['success'] = False


    # Configuração inicial basica.
    msg = MIMEMultipart()
    msg['From'] = email_from
    msg['Subject'] = subject_title
    msg['To'] = ', '.join(email_to)
    
    # Adicionar corpo da mensagem
    msg.attach(MIMEText(body_message, 'html'))

    # Adicionar anexos, se houver
    if attachments:
        by_smtp_result['anexos'] = True
        by_smtp_result['quantidade_anexos'] = 0
        for path_to_attach in attachments:
            file_name = os.path.basename(path_to_attach)
            attachs = open(path_to_attach, 'rb')
            part = MIMEBase('application', 'octet-stream')
            part.set_payload((attachs).read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', "attachment; filename= %s" % file_name)
            msg.attach(part)
            by_smtp_result['quantidade_anexos'] += 1
    else:
        by_smtp_result['anexos'] = False
        by_smtp_result['quantidade_anexos'] = 0
            
    # Conectar ao servidor SMTP e enviar email
    try:
        server_by_smtp = smtplib.SMTP(smtp_server, smtp_port)
        server_by_smtp.starttls()
        server_by_smtp.login(email_from, pass_from)
        email_content = msg.as_string()
        by_smtp_result['quantidade_enviada'] = 0
        for email in email_to:
            server_by_smtp.sendmail(email_from, email, email_content)
            by_smtp_result['quantidade_enviada'] += 1
        server_by_smtp.quit()
        by_smtp_result['success'] = True
        print("Email(s) enviado(s) com sucesso!")
        

    except smtplib.SMTPException as e:
        by_smtp_result['success'] = False
        print("Erro ao enviar email(s):", str(e))
    
    # Pós Tratamento
    ...
    
    return by_smtp_result
