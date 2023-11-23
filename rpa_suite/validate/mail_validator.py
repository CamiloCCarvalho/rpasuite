import email_validator

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
        * 'map_validation' - mapa da validação de cada email (dicionário)
    """
    
    # Variaveis locais
    mail_validation_result: dict = {
        'success': bool,
        'valid_emails': list,
        'invalid_emails': list,
        'qt_valids': int,
        'qt_invalids': int,
        'map_validation': list[dict]
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
        'valid_emails': valid_emails,
        'invalid_emails': invalid_emails,
        'success': len(invalid_emails) == 0,
        'qt_valids': len(valid_emails),
        'qt_invalids': len(invalid_emails),
        'map_validation': map_validation
    }
    
    # Retorno
    return mail_validation_result


if __name__ == '__main__':
    dictio = valid_emails(['camilo.carvalho@triasoftware.com.br', 'asfaltorodas@gmail.com', '@gmail.com.camio'])