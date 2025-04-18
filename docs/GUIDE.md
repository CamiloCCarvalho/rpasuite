# Overview

**RPA Suite** é uma biblioteca voltada para o uso em desenvolvimento de bots e RPAs profissionais.
Com ferramentas que **aceleram o desenvolvimento**, reduzindo o tempo necessario para desenvolver pequenos blocos que são responsaveis por tarefas muito comuns e repetitivas no mundo dos RPAs.

## Components

Os componentes são divididos por categoria de atuação ou de funcionalidade. Estão organizados na subpasta *core*.
Você pode fazer a importação de pelo menos duas formas diferentes.

<hr>
<br>

## Quick Start

### Instalation


Primeiramente certifique-se de ter instalado o Python, este passo é muito importante 😄

Segundo passo também é essencial que seria instalar a nossa lib:

```pip
python -m pip install rpa-suite
```

Ou:

```pip
pip install rpa-suite
```

Ou ainda, desta forma também:

```pip
pip install rpa_suite
```

> **⚠️ Lembrete:**
> para o uso em ambientes virtuais lembre-se de ativar o seu ambiente no terminal onde pretende fazer instalações.

> **⚠️ Importante:**
> Atualmente não estamos fazendo otimizações para versão na plataforma Linux, recomendamos o uso apenas na plataforma Windows (8.1 ou superior).

<hr>
<br>

## Usage Guide

### Form 1:

A variavel **rpa** esta disponivel já na importação do modulo com a maioria dos objetos instanciados.

Você pode acessar diretamente os metodos dos submodulos com esta variavel.

```python
# Importando a suite instanciada com todas funcionalidades
from rpa_suite import rpa

# Usando como exemplo o modulo de log, fazendo sua configuração
rpa.log.config_logger()

# Gerando um log no arquivo
rpa.log.log_start_run_debug(f'teste')


# Este código deve gerar uma pasta 'log' no diretório raiz onde esta sendo executado, com um arquigo 'log.log' e escrever um log inicial no arquivo e no terminal
>>> DD.MM.YY.HH:MM DEBUG    teste
```

### Form 2:

Também é possivel instanciar a Suite de ferramentas criando seu proprio objeto.

Importe a classe ``Suite``, instancie  e acesse da mesma forma todos recursos.

```python
# Importando objeto Suite para criar sua propria instancia
from rpa_suite.suite import Suite

# Instancie a Suite com nome que desejar
rpa = Suite()

# Usando como exemplo o modulo de log, fazendo sua configuração
rpa.log.config_logger()


# Gerando um log no arquivo
rpa.log.log_start_run_debug(f'teste')


# Este código deve gerar uma pasta 'log' no diretório raiz onde esta sendo executado, com um arquigo 'log.log' e escrever um log inicial no arquivo e no terminal
>>> DD.MM.YY.HH:MM DEBUG    teste
```

### Form 3:

Opcionalmente pode usar a variavel **suite** que possui as classes disponiveis.

```python
# Importando o objeto instanciado 'suite' também te dará acesso aos outros objetos 
from rpa_suite import suite

# Instanciando apenas um obojeto de Log
my_logger = suite.Log()

# Usando como exemplo o modulo de log, fazendo sua configuração
my_logger.config_logger()

# Gerando um log no arquivo
my_logger.log_start_run_debug(f'teste')

# Este código deve gerar uma pasta 'log' no diretório raiz onde esta sendo executado, com um arquigo 'log.log' e escrever um log inicial no arquivo e no terminal
>>> DD.MM.YY.HH:MM DEBUG    teste
```

### Form 4:

Para usar isoladamente apenas um Submodulo, acesse ``core`` e faça a importação do modulo desejado.

```python

# Importando diretamente a classe do modulo desejado
from rpa_suite.core import Log

# Instancie o Objeto
my_logger = Log()

# Usando como exemplo o modulo de log, fazendo sua configuração
my_logger.config_logger()

# Escrevendo no arquivo de log
my_logger.log_start_run_debug(f'teste')

# Este código deve gerar uma pasta 'log' no diretório raiz onde esta sendo executado, com um arquigo 'log.log' e escrever um log inicial no arquivo e no terminal
>>> DD.MM.YY.HH:MM DEBUG    teste
```

<hr>
<br>

# Modules Guide

## Print

**Print** é um submodulo do nosso conjunto.
Este tem um caracteristica difernente dos demais.

Sua implementação foi feita tanto no Objeto raiz como também no seu modulo dedicado, acesse seus métodos tanto pela variavel ``rpa`` como também pela classe **Print**.

Abaixo todos métodos e argumentos disponiveis de **Print**:

Metodos:

- ``success_print``
- ``alert_print``
- ``error_print``
- ``info_print``
- ``magenta_print``
- ``blue_print``
- ``print_call_fn``
- ``print_return_fn``

Argumentos:

- ``string_text``: ``str``
- ``color`` : ``Obj Colors``
- ``ending`` : ``str``

> Se desejar importar ou instanciar de outra forma veja o guia na parte de "Componentes" ou "Formas de Uso".
>
> Também é possivel fazer o import da seguinte forma, para usar o Objeto isolado:
>
> `from rpa_suite.core import Print`

<br>

Exemplo de uso das funções de ``Print``:

```python
# Importação do objeto instanciado de Suite
from rpa_suite import rpa

"""
Cores disponiveis
  black   
  blue  
  green   
  cyan  
  red   
  magenta 
  yellow  
  white   
  default 
  call_fn (variação de blue) 
  retur_fn (variação de magenta)
"""

# Como explicado anteriormente, já foi implementada diretamente todas funções do obj Print diretamente no modulo principal

rpa.success_print(f'It`s green here')
rpa.alert_print(f'It`s yellow message')
rpa.error_print(f'It`s red message')
rpa.info_print(f'It`s blue message')

rpa.magenta_print(f'What color? Magenta')
rpa.blue_print(f'Other blue')

# variações (estas tem apenas objetivo de serem cores distintas para quem quer ser mais direto e sem muitas cores)
rpa.print_call_fn(f'foo')
rpa.print_return_fn(f'foo2')
```

Abaixo variações do uso e possibilidade de mudar as cores a sua vontade:

> É possivel mudar a cor do seu print a sua vontade, importe o objeto de cores para isso.
>
> Defina também o "ending" assim como o print padrão do python.

<br>

Exemplo manipulando as cores e o ending:

```python
# Importação do objeto de Suite e Colors
from rpa_suite import rpa
from rpa_suite.core.print import Colors

# Passagem de argumentos, mudança de comportamento e cores
rpa.success_print(f'It`s red now!', color=Colors.red)
rpa.alert_print(f"This don't breakline on ending", ending=' ')
rpa.error_print(f'This message display on same line to alert.')

# Exemplo com todos argumentos explicitos
rpa.info_print(string_text=f'All arguments explicts',
               color=Colors.blue,
               ending="\n\n"
              )
```

<br>

## Date

**Date** é um Objeto simples que tem por finalidade apenas acelerar a conversão de Data e Hora.
Em muitos casos precisamos capturar Datas o que já é bem facil, no entando queremos pular a parte chata de ter que ficar formatando.

Sua principal funcionalidade é devolver uma tupla ja com **Dia**, **Mes** e **Ano** formatada como **string** usando 2 digitos e o ano em 4 digitos. O mesmo valoe para **Horas**, **Minutos** e **Segundos** (este ultimo apenas com 2 digitos).

Abaixo todos métodos e argumentos disponiveis de **Date**:

Metodos:

- ``get_dmy``
- ``get_hms``

Argumentos:

- ``Na verão atual não há argumentos``

Retorno:

- ``get_dmy``  -> ``Tuple(str)``: ``'dd', 'mm', 'YYYY'``
- ``get_hms``  -> ``Tuple(str)``: ``'hour', 'min', 'sec'``
- Obs.: Apenas "Year" tem 4 digitos, os demais dados são sempre em 2 digitos **string**.

> Se desejar importar ou instanciar de outra forma veja o guia na parte de "Componentes" ou "Formas de Uso".
>
> Também é possivel fazer o import da seguinte forma, para usar o Objeto isolado:
>
> `from rpa_suite.core import Date`

<br>

Exemplo de uso dos Metodos de ``Date``:

```python
# Importando a suite instanciada com todas funcionalidades
from rpa_suite import rpa

# Usando a variavel date (objeto Date já instanciado) acessamos seu método que captura dia, mes e ano atual do seu sistema.
dd, mm, yyyy = rpa.date.get_dmy()

# Usando a variavel date (objeto Date já instanciado) acessamos seu método que captura hora, segundos e minutos atual do seu sistema.
hour, minute, sec = rpa.date.get_hms()

# exibindo o retorno obtido para data
rpa.info_print(f'date: {dd}/{mm}/{yyyy}')

# exibindo o retorno obtido para horario
rpa.info_print(f'hour: {hour}:{minute}:{sec}')

>>> date: 18/04/2025
>>> hour: 04:44:29
```

<br>

## Clock

**CLock** é um Objeto dedicado a fazer controle de execução.
Por vezes precisamos que um bloco de código ou uma função inteira aguarde, execute e espere, ou até mesmo podemos usar como Schedule para um robo inteiro.

Abaixo todos métodos e argumentos disponiveis de **Clock**:

Metodo ``exec_at_hour``:

- Função temporizada, executa a função no horário especificado, por ``default`` executa no momento da chamada em tempo de execução, opcionalmente pode escolher o horário para execução, sendo uma ``string`` contendo horas e minutos com dois digitos como demonstrado a seguir: ``'hh:mm'``.
- Parametros:

  - ``hour_to_exec`` : ``str`` - Horario no formato `'hh:mm'`.
  - ``fn_to_exec``: ``Callable`` - Função que deseja executar.
  - ``*args*``: Argumentos posicionais da função.
  - ``**kwargs``: Argumentos nomeados da função.

<br>

Metodo ``wait_for_exec``:

- Função temporizada, aguarda uma quantidade de tempo em **segundos** para executa a função em seguida.
Por ``default`` executa no momento da chamada em tempo de execução.
- Parametros:

  - ``wait_time`` : ``int`` - Tempo em segundos para aguardar.
  - ``fn_to_exec`` : ``Callable`` - Função que deseja executar.
  - ``*args*``: Argumentos posicionais da sua função.
  - ``**kwargs``: Argumentos nomeados da sua função.

<br>

Metodo ``exec_and_wait``:

- Função temporizada, executa a função do argumento e em seguinda aguarda o tempo desejado em segundos, por ``default`` executa no momento da chamada em tempo de execução.
- Parametros:

  - ``wait_time``:``int`` - Tempo em segundos para aguardar após execução.
  - ``fn_to_exec``: ``Callable`` - Função que deseja executar.
  - ``*args*``: Argumentos posicionais da sua função.
  - ``**kwargs``: Argumentos nomeados da sua função.

<br>

> Se desejar importar ou instanciar de outra forma veja o guia na parte de "Componentes" ou "Formas de Uso".
>
> Também é possivel fazer o import da seguinte forma, para usar o Objeto isolado:
>
> `from rpa_suite.core import Clock`

<br>

Exemplo de uso ``exec_at_hour``:

```python
# Importando a suite instanciada com todas funcionalidades
from rpa_suite import rpa


# Aqui sua função que deseja executar
def sum(a, b):
  # realiza operações quais forem ...
  print(a*b)
  return a * b


# Este passo não é necessario, apenas par facilitar visualmente
a = 3
b = 9

# Executa a função no horario definido
rpa.clock.exec_at_hour('12:52', sum, a, b)

# result: A função soma deve ser executada no horario 12:52 do sistema onde esta rodando  o código.
>>> 27
>>> sum: Successfully executed!
```

<br>

Exemplo de uso ``wait_for_exec``:

```python
# Importando a suite instanciada com todas funcionalidades
from rpa_suite import rpa


# Aqui sua função que deseja executar
def sum(a, b):
  # realiza operações quais forem ...
  print(a*b)
  return a * b


# Este passo não é necessario, apenas par facilitar visualmente
a = 3
b = 9

# Executa a função após 10 segundos
rpa.clock.wait_for_exec(10, sum, a, b)

# result: A função soma deve ser executada após o tempo definido.
>>> 27
>>> Function: wait_for_exec executed the function: sum.
```

<br>

Exemplo de uso ``exec_and_wait``:

```python
# Importando a suite instanciada com todas funcionalidades
from rpa_suite import rpa


# Aqui sua função que deseja executar
def sum(a, b):
  # realiza operações quais forem ...
  print(a*b)
  return a * b


# Este passo não é necessario, apenas par facilitar visualmente
a = 3
b = 9
time_await = 10

# Executa a função, então aguarda 10 segundos para seguir com o proximo código
rpa.clock.exec_and_wait(time_await, sum, a, b)

# Esta função abaixo, sera executada sómente 10 segundos após a execução da função acima
rpa.success_print(f'Run after: {time_await}')

# result: A função soma deve ser executada após o tempo definido.
>>> 27
>>> Function: wait_for_exec executed the function: sum.
>>> Run after: 10
```

<br>


## Directory

**Directory** é um Objeto dedicado a manipulação de diretórios, criação de pastas, exclusão de pastas, e exclusão de conteudos dentro de pastas.

Abaixo todos métodos e argumentos disponiveis de **Directory**:

Metodo ``create_temp_dir``:

- Função responsavel por criar diretório temporário, pode também criar diretório com nome desejado e salvar o path relativo para uso posterior. Por ``default`` o nome do diretório é "temp" e o caminho é onde esta sendo executada a função
- Argumentos:

  - ``path_to_create``: ``str`` - Caminho para criar o diretório.
  - ``name_temp_dir``: ``str`` - Nome desejado para o diretório.
  - ``display_message``: ``bool`` - Opção se deseja que exiba mensagens no terminal.

<br>

Metodo ``delete_temp_dir``:

- Função responsavel por deletar diretório temporário, pode também deletar diretório com nome desejado e opcionalmente excluir diretórios que estejam populados com conteudo. Por ``default`` o nome do diretório é "temp" e o caminho é onde esta sendo executada a função.
- Argumentos:

  - ``path_to_delete``: ``str`` - Caminho para deletar o diretório
  - ``name_temp_dir``: ``str`` - Nome do diretório a deletar
  - ``delete_files``: ``bool`` - Opção se deseja excluir diretório mesmo populado
  - ``display_message``: ``bool`` - Opção se deseja que exiba mensagens no terminal

<br>

> Se desejar importar ou instanciar de outra forma veja o guia na parte de "Componentes" ou "Formas de Uso".
>
> Também é possivel fazer o import da seguinte forma, para usar o Objeto isolado:
>
> `from rpa_suite.core import Directory`

<br>

Exemplo de uso ``create_temp_dir``:

```python
# Importando a suite instanciada com todas funcionalidades
from rpa_suite import rpa

# Acessando a instancia de 'dir' directory acessamos seu método para criar uma pasta temporaria
result = rpa.directory.create_temp_dir()

# Exibindo o dict de resultado obtido com o retorno da função
# A função retorna um dict com o status de sucesso e o path da pasta criada
rpa.success_print(result)

>>> A função deve criar uma pasta chamada 'temp' no diretório onde esta sendo executado este código.
>>> result: {'success': True, 'path_created': 'C:\\User\\path\\to\\your_project\\temp'}


# Usando argumentos
result_example2 = rpa.directory.create_temp_dir(path_to_create=r'.\docs', name_temp_dir='mydir')

# Exibindo o dict de resultado obtido com o retorno da função
# A função retorna um dict com o status de sucesso e o path da pasta criada
rpa.success_print(result_example2)

>>> A função deve criar uma pasta chamada 'docs' e interna a esta outra chamada 'mydir' considerando a raiz atual como ponto de partida.
>>> result_example2: {'success': True, 'path_created': '.\\docs\\mydir'}
```

<br>

Exemplo de uso ``delete_temp_dir``:

```python
# Importando a suite instanciada com todas funcionalidades
from rpa_suite import rpa

# Acessando a instancia de 'dir' directory acessamos seu método para criar uma pasta temporaria
result = rpa.directory.delete_temp_dir()

# Exibindo o dict de resultado obtido com o retorno da função
# A função retorna um dict com o status de sucesso e o path da pasta deletada
rpa.success_print(result)

>>> A função deve deleta uma pasta chamada 'temp' no diretório onde esta sendo executado este código.
>>> result: {'success': True, 'path_deleted': 'C:\\Intel\\PERSONAL\\_rpa_suite\\test_suite\\temp'}

# Usando argumentos
result_example2 = rpa.directory.delete_temp_dir(
    path_to_delete=r'.\docs', 
    name_temp_dir='mydir',
    delete_files=True)

# Exibindo o dict de resultado obtido com o retorno da função
# A função retorna um dict com o status de sucesso e o path da pasta deletada
rpa.success_print(result_example2)

>>> A função deve deletar uma pasta chamada 'mydir' interna em relação a pasta 'docs' considerando a raiz atual como ponto de partida.
>>> result_example2: {'success': True, 'path_deleted': '.\\docs\\mydir'}
```

## Email

**Email** é um Objeto dedicado a emails, envio e manipulação, no entanto temos apenas formato SMPT implementado, *em breve vamos disponibilizar outros métodos*.

Abaixo todos métodos e argumentos disponiveis de **Email**:

Metodo ``send_smtp``:

- Função responsavel por fazer envio de emails usando SMTP, com possibilidade de incluir anexos, a finalidade é reduzir a quantidade de código usado para tal, pois emails precisam de muitos detalhes declarados.
Por ``default`` o servidor, a porta e a autenticação são definidos seguindo o padrão da hostinger, e o body do email já é definido para aceitar conteudo em HTML.

- Argumentos:

  - ``email_user`` : ``str`` - Email do remetente.
  - ``email_password`` : ``str`` - Senha do remetente.
  - ``email_to`` : ``str`` - Email do destinatario.
  - ``subject_title`` : ``str`` - Titulo do email.
  - ``body_message`` : ``str`` - Mensagem do Email, **aceita HTML**.
  - ``attachments`` : ``list[str]`` - Lista com path de anexos.
  - ``smtp_server`` : ``str`` - Servidor a utilizar.
  - ``smtp_port`` : ``int`` - Porta a utilizar.
  - ``auth_tls`` : ``bool`` - Tipo de autenticação, se **False usa SSL**.
  - ``display_message``: ``bool`` - Opção se deseja que exiba mensagens no terminal.

<br>

> Se desejar importar ou instanciar de outra forma veja o guia na parte de "Componentes" ou "Formas de Uso".
>
> Também é possivel fazer o import da seguinte forma, para usar o Objeto isolado:
>
> `from rpa_suite.core import Email`

<br>

Exemplo de uso ``send_smtp``:

```python
# Importando a suite instanciada com todas funcionalidades
from rpa_suite import rpa

# Acessando a instancia de 'Email' acessamos seu método para enviar email por SMTP
rpa.email.send_smtp(email_user='your@email.com',
                    email_password='your_password',
                    email_to='destiny@email.com',
                    subject_title='Test Title',
                    body_message='Test body message.',
                    attachments=['C:/Users/rpa_suite/Pictures/logo_rpa_suite.jpg'],
                    smtp_server='smtp.gmail.com',
                    smtp_port=587,
                    auth_tls=False,
                    display_message=True)

```

<br>



## ***Other modules guide comming soon!***

<br>