import smtplib, os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from rpa_suite.logs.loggin import logging_decorator

@logging_decorator
def enviar_email(
                email_remetente: str,
                senha_remetente: str,
                email_destinatarios: list[str],
                assunto: str,
                mensagem: str,
                anexos: list = None,
                servidor_smtp: str = 'smtp.office365.com',
                porta_smtp: int = 587
                ) -> dict:

    """
    Função responsavel por enviar emails (SMTP), aceita lista de destinatários e possibilidade
    de anexar arquivos. \n
    
    Retorna um dicionário com todas informações que podem ser necessarias sobre os emails.\n
    Sendo respectivamente: \n
        - se houve pelo menos um envio com sucesso
        - lista de todos emails parametrizados para envio
        - lista de todos emails validos para envio
        - lista de todos emails invalidos para envio
        - quantidade efetiva que foi realizado envio
        - se há anexos
        - quantos anexos foram inseridos
    """

    # Variaveis locais
    mail_result: dict = {
        'sucesso': bool,
        'emails_todos': list,
        'emails_validos': list,
        'emails_invalidos': list,
        'quantidade_enviada': int,
        'anexos': bool,
        'quantidade_anexos': int
    }
    
    
    # Pré Tratamentos
    ...


    # Configuração inicial basica.
    msg = MIMEMultipart()
    msg['From'] = email_remetente
    msg['Subject'] = assunto
    msg['To'] = ', '.join(email_destinatarios)
    
    # Adicionar corpo da mensagem
    msg.attach(MIMEText(mensagem, 'html'))

    # Adicionar anexos, se houver
    if anexos:
        mail_result['anexos'] = True
        mail_result['quantidade_anexos'] = 0
        for caminho_anexo in anexos:
            nome_arquivo = os.path.basename(caminho_anexo)
            anexo = open(caminho_anexo, 'rb')
            part = MIMEBase('application', 'octet-stream')
            part.set_payload((anexo).read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', "attachment; filename= %s" % nome_arquivo)
            msg.attach(part)
            mail_result['quantidade_anexos'] += 1
    else:
        mail_result['anexos'] = False
        mail_result['quantidade_anexos'] = 0
            
    # Conectar ao servidor SMTP e enviar email
    try:
        servidor = smtplib.SMTP(servidor_smtp, porta_smtp)
        servidor.starttls()
        servidor.login(email_remetente, senha_remetente)
        texto_email = msg.as_string()
        mail_result['quantidade_enviada'] = 0
        for email in email_destinatarios:
            servidor.sendmail(email_remetente, email, texto_email)
            mail_result['quantidade_enviada'] += 1
        servidor.quit()
        print("Email(s) enviado(s) com sucesso!")
        

    except smtplib.SMTPException as e:
        print("Erro ao tentar enviar email(s):", str(e))
    
    # Pós Tratamento
    
    return mail_result


