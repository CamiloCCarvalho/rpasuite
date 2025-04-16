# /mail_validator.py

import email_validator
from rpa_suite.log.printer import error_print, success_print

def valid_emails(
                email_list: list[str],
                display_message: bool = False,
                ) -> dict:
    
    """
    Function responsible for rigorously validating a list of emails using the email_validator library. \n
    
    Parameters:
    ------------
    ``email_list: list`` a list of strings containing the emails to be validated
    
    Return:
    ------------
    >>> type: dict
    Returns a dictionary with the respective data:
        * 'success': bool - represents if the list is 100% valid
        * 'valid_emails': list - list of valid emails
        * 'invalid_emails': list - list of invalid emails
        * 'qt_valids': int - number of valid emails
        * 'qt_invalids': int - number of invalid emails
        * 'map_validation' - map of the validation of each email
        
    Description: pt-br
    ----------
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
    
    # Local Variables
    result: dict = {
        'success': bool,
        'valid_emails': list,
        'invalid_emails': list,
        'qt_valids': int,
        'qt_invalids': int,
        'map_validation': list[dict]
    }

    
    # Preprocessing
    validated_emails: list = []
    invalid_emails: list = []
    map_validation: list[dict] = []
    
    # Process
    try:
        for email in email_list:
            try:
                v = email_validator.validate_email(email)
                validated_emails.append(email)
                map_validation.append(v)
                
            except email_validator.EmailNotValidError:
                invalid_emails.append(email)
        
        if display_message:
            success_print(f'Function:{valid_emails.__name__} executed!')
            
    except Exception as e:
        error_print(f'Error when trying to validate email list: {str(e)}')

    
    # Postprocessing
    result = {
        'valid_emails': validated_emails,
        'invalid_emails': invalid_emails,
        'success': len(invalid_emails) == 0,
        'qt_valids': len(validated_emails),
        'qt_invalids': len(invalid_emails),
        'map_validation': map_validation
    }
    
    return result
