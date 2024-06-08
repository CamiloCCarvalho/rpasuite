"""MODULE CLOCK"""
from .clock.waiter import wait_for_exec, exec_and_wait
from .clock.exec_at import exec_at_hour

"""MODULE DATE"""
from .date.date import get_hms, get_dma

"""MODULE EMAIL"""
from .email.sender_smtp import send_email

"""MODULE FILE"""
from .file.counter import count_files
from .file.temp_dir import create_temp_dir, delete_temp_dir

"""MODULE LOG"""
# from .log.loggin import logging_decorator
from .log.printer import alert_print, success_print, error_print, info_print, print_call_fn, print_retur_fn, magenta_print, blue_print

"""MODULE REGEX"""
from .regex.list_from_text import create_list_using_regex

"""MODULE VALIDATE"""
from .validate.mail_validator import valid_emails
from .validate.string_validator import search_in

class Rpa_suite():
    """
    The ``Rpa_suite`` class is a generic representation of the modules, with the aim of centralizing all submodules for access through an instance of this representational Object. It contains variables pointed to the functions of the submodules present in the rpa-site.
    
    Call
    ----------
    When calling the maintainer file of this class, an instance of this object will be invoked to be used or reused through another variable
    
    Objective
    ----------
    Flexibility being able to call each submodule individually or by importing the representational object of all submodules.
    
    Description: pt-br
    ----------
    Classe ``Rpa_suite`` é uma representação genérica do dos módulos, com objetivo de centralizar todos submódulos para acesso através de uma instância deste Objeto representacional. Ele contem variaveis apontadas para as funções dos submódulos presentes no rpa-site.
    
    Chamada
    ----------
    Ao chamar o arquivo mantenedor desta classe, sera invocada uma instancia deste objeto para poder ser utilziado ou reutilizado através de outra variável
    
    Objetivo
    ----------
    Flexibilidade podendo chamar cada submódulo de forma individual ou fazendo a importação do objeto representacional de todos submódulos.
    """
    
    # clock
    wait_for_exec = wait_for_exec
    exec_and_wait = exec_and_wait
    exec_at_hour = exec_at_hour
    
    # date
    get_hms = get_hms
    get_dma = get_dma
    
    # email
    send_email = send_email
    
    # file
    count_files = count_files
    create_temp_dir = create_temp_dir
    delete_temp_dir = delete_temp_dir
    #clear_temp_dir = clear_temp_dir
    
    # log
    alert_print = alert_print
    success_print = success_print
    error_print = error_print
    info_print = info_print
    print_call_fn = print_call_fn
    print_retur_fn = print_retur_fn
    magenta_print = magenta_print
    blue_print = blue_print
    
    # regex
    create_list_using_regex = create_list_using_regex
    
    # validate
    valid_emails = valid_emails
    search_in = search_in
    
# Create a instance of Rpa_suite


# Define function to return this instance
def invoke():
    suite = Rpa_suite()
    return suite

