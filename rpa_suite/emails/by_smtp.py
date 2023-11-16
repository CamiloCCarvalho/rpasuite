import smtplib, os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from rpa_suite.logs.loggin import logging_decorator

@logging_decorator
def enviar_email(email_remetente: str,
                 senha_remetente: str,
                 email_destinatarios: list[str],
                 assunto: str,
                 mensagem: str,
                 anexos: list=None,
                 servidor_smtp: str='smtp.office365.com',
                 porta_smtp: int=587) -> dict:

    """
    Função responsavel por enviar emails, aceita lista de destinatarios e possibilidade
    de anexar arquivos.
    
    Retorna quantidade de emails enviados, sendo valor numerico INT
    """

    # Variaveis internas
    pattern_email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    mail_result: dict = {
        'sucesso': bool,
        'todos': list,
        'validos': list,
        'invalidos': list,
        'quantidade': int
    }
    
    # Tratamentos

    msg = MIMEMultipart()
    msg['From'] = email_remetente
    msg['Subject'] = assunto
    msg['To'] = ', '.join(email_destinatarios)  # Converta a lista em uma string separada por vírgulas
    
    # Adicionar corpo da mensagem
    msg.attach(MIMEText(mensagem, 'plain'))

    # Adicionar anexos, se houver
    if anexos:
        for caminho_anexo in anexos:
            nome_arquivo = os.path.basename(caminho_anexo)
            anexo = open(caminho_anexo, 'rb')
            part = MIMEBase('application', 'octet-stream')
            part.set_payload((anexo).read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', "attachment; filename= %s" % nome_arquivo)
            msg.attach(part)
            
    # Conectar ao servidor SMTP e enviar email
    try:
        servidor = smtplib.SMTP(servidor_smtp, porta_smtp)
        servidor.starttls()
        servidor.login(email_remetente, senha_remetente)
        texto_email = msg.as_string()
        for email in email_destinatarios:
            servidor.sendmail(email_remetente, email, texto_email)
            mail_result['quantidade'] += 1
        servidor.quit()
        print("Email(s) enviado(s) com sucesso!")
        return mail_result

    except smtplib.SMTPException as e:
        print("Erro ao enviar email:", str(e))
        return mail_result
