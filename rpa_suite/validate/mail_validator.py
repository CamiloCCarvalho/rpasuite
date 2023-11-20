import email_validator
from rpa_suite.log.loggin import logging_decorator

@logging_decorator
def valid_emails(
                email_list: list[str]
                ) -> dict:
    
    """
    Função responsavel por validar de forma rigorosa lista de emails usando a biblioteca email_validator. \n
    
    o Retorno será um dicionário. \n
    Sendo respectivamente: \n
        - lista de emails validos
        - lista de emails invalidos
        - boleano contendo falso pois nem todos emails são validos
        - quantidade de emails validos
        - quantidade de emails invalidos
        - mapa da validação de cada email (dicionário)
    """
    
    # Variaveis locais
    mail_validation_result: dict = {
        'emails_validos': list,
        'emails_invalidos': list,
        'todos_validaram_sucesso': bool,
        'quantidade_emails_validos': int,
        'quantidade_emails_invalidos': int,
        'mapa_do_validador': list[dict]
    }

    
    # Pré Tratamento
    valid_emails: list = []
    invalid_emails: list = []
    map_validation: list[dict] = []
    
    # Processo
    try:
        for email in email_list:
            try:
                v = email_validator.validate_email(email)
                valid_emails.append(email)
                map_validation.append(v)
                
            except email_validator.EmailNotValidError:
                invalid_emails.append(email)
                
    except Exception as e:
        print(f'Erro ao tentar validar lista de emails: {str(e)}')

    
    # Pós Tratamento
    mail_validation_result = {
        'emails_validos': valid_emails,
        'emails_invalidos': invalid_emails,
        'todos_validaram_sucesso': len(invalid_emails) == 0,
        'quantidade_emails_validos': len(valid_emails),
        'quantidade_emails_invalidos': len(invalid_emails),
        'mapa_do_validador': map_validation
    }
    
    # Retorno
    return mail_validation_result


if __name__ == '__main__':
    dictio = valid_emails(['camilo.carvalho@triasoftware.com.br', 'asfaltorodas@gmail.com', '@gmail.com.camio'])