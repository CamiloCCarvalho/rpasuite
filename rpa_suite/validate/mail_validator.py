import email_validator
from rpa_suite.log.printer import error_print, success_print

def valid_emails(
                email_list: list[str]
                ) -> dict:
    
    """
    Função responsavel por validar de forma rigorosa lista de emails usando a biblioteca email_validator. \n
    
    Paramentros:
    ------------
    ``email_list: list`` uma lista de strings contendo os emails a serem validados
    
    Retorno:
    ------------
    >>> type: dict
    Retorna um dicionário com os respectivos dados:
        * 'success': bool - representa se a lista é 100% valida
        * 'valid_emails': list - lista de emails validos
        * 'invalid_emails': list - lista de emails invalidos
        * 'qt_valids': int - quantidade de emails validos
        * 'qt_invalids': int - quantidade de emails invalidos
        * 'map_validation' - mapa da validação de cada email
    """
    
    # Variáveis locais
    result: dict = {
        'success': bool,
        'valid_emails': list,
        'invalid_emails': list,
        'qt_valids': int,
        'qt_invalids': int,
        'map_validation': list[dict]
    }

    
    # Pré Tratamento
    validated_emails: list = []
    invalid_emails: list = []
    map_validation: list[dict] = []
    
    # Processo
    try:
        for email in email_list:
            try:
                v = email_validator.validate_email(email)
                validated_emails.append(email)
                map_validation.append(v)
                
            except email_validator.EmailNotValidError:
                invalid_emails.append(email)
        success_print(f'Função: {valid_emails.__name__} executada.')
    except Exception as e:
        error_print(f'Erro ao tentar validar lista de emails: {str(e)}')

    
    # Pós Tratamento
    result = {
        'valid_emails': validated_emails,
        'invalid_emails': invalid_emails,
        'success': len(invalid_emails) == 0,
        'qt_valids': len(validated_emails),
        'qt_invalids': len(invalid_emails),
        'map_validation': map_validation
    }
    
    return result
