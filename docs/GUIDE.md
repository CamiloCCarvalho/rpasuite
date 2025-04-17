# Overview

**RPA Suite** é uma biblioteca voltada para o uso em desenvolvimento de bots e RPAs profissionais.
Com ferramentas que **aceleram o desenvolvimento**, reduzindo o tempo necessario para desenvolver pequenos blocos que são responsaveis por tarefas muito comuns e repetitivas no mundo dos RPAs.

## Components

Os componentes são divididos por categoria de atuação ou de funcionalidade. Estão organizados na subpasta *core*.
Você pode fazer a importação de pelo menos duas formas diferentes.

<hr>
<br>

## Quick Start

### Using Example

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

<hr>
<br>

## Usage Guide

### Form 1:

A variavel **rpa** esta disponivel já na importação do modulo com a maioria dos objetos instanciados

Assim sendo, você pode acessar diretamente os methodos do submodulo que esta usando em uma unica linha.

```python
# Importando a suite instanciada com todas funcionalidades
from rpa_suite import rpa

# Usando como exemplo o modulo de log, fazendo sua configuração
rpa.log.config_logger()

# Gerando um log no arquivo
rpa.log.log_start_run_debug(f'teste')


# result:
# > este código deve gerar uma pasta no diretório raiz onde esta sendo executado, com um arquigo de log e gerar um log inicial

```

### Form 2:

Também deixamos o acesso facilitado para você instanciar a Suite de ferramentas criando seu proprio objeto.

Assim você importa a classe Suite e instancia, tendo acesso da mesma forma a todos recursos.

```python

# Importando objeto Suite para criar sua propria instancia
from rpa_suite.suite import Suite

# Instancie a Suite com nome que desejar
rpa = Suite()

# Usando como exemplo o modulo de log, fazendo sua configuração
rpa.log.config_logger()


# Gerando um log no arquivo
rpa.log.log_start_run_debug(f'teste')


# result:
# > este código deve gerar uma pasta no diretório raiz onde esta sendo executado, com um arquigo de log e gerar um log inicial

```

### Form 3:

Também é possivel importar a variavel **suite** que tem os Objetos como classes para você instanciar.

```python

# Importando o objeto instanciado 'suite' também te dará acesso aos outros objetos 
from rpa_suite import suite

# Instanciando apenas um obojeto de Log
my_logger = suite.Log()

# Usando como exemplo o modulo de log, fazendo sua configuração
my_logger.config_logger()

# Gerando um log no arquivo
my_logger.log_start_run_debug(f'teste')

# result:
# > Este código deve gerar uma pasta no diretório raiz onde esta sendo executado e escrever no arquigo de log

```


### Form 4:

Também é possivel importar a variavel **suite** que tem os Objetos como classes para você instanciar.

```python

# Importando diretamente a classe do modulo desejado
from rpa_suite.core import Log

# Instancie o Objeto
my_logger = Log()

# Usando como exemplo o modulo de log, fazendo sua configuração
my_logger.config_logger()

# Escrevendo no arquivo de log
my_logger.log_start_run_debug(f'teste')

# result:
# > Este código deve gerar uma pasta no diretório raiz onde esta sendo executado e escrever no arquigo de log
```

<hr>
<br>


# Modules Guide

## Print

Print é um submodulo do nosso conjunto. Este tem um caracteristica difernente dos demais.

Este possui o arquivo "print.py" dentro de "**core** e possui a classe Print como todos outros submodulos.

Mas também é feita a implementação de todas seus methodos diretamente no objeto Suite a finalidade é facilitar seu uso já que provavelmente é a função mais utilizada da lib no dia a dia.

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
- ``string_text``
- ``color``
- ``ending``

> Se desejar importar ou instanciar de outra forma veja o guia na parte de "Componentes" ou "Formas de Uso".
>
> Também é possivel fazer o import da seguinte forma, para usar o Objeto isolado:
>
> `from rpa_suite.core import Print`


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

Date é um Objeto simples que tem por finalidade apenas acelerar a conversão de Data e Hora, em muitos casos precisamos capturar Datas o que já é bem facil, no entando queremos pular a parte chata de ter que ficar formatando as datas e horas.

Sua principal funcionalidade é devolver uma tupla ja com **Dia**, **Mes** e **Ano** formatada como **string** usando 2 digitos e o ano em 4 digitos. O mesmo valoe para **Horas**, **Minutos** e **Segundos**.

Abaixo todos métodos e argumentos disponiveis de **Date**:

Metodos:
- ``get_dmy``
- ``get_hms``

Argumentos:
- ``Na verão atual não há argumentos``

> Se desejar importar ou instanciar de outra forma veja o guia na parte de "Componentes" ou "Formas de Uso".
>
> Também é possivel fazer o import da seguinte forma, para usar o Objeto isolado:
>
> `from rpa_suite.core import Date`

Exemplo de uso dos Metodos de ``Date``:

```python

# Importando a suite instanciada com todas funcionalidades
from rpa_suite import rpa

# Usando a variavel date (objeto Date já instanciado) acessamos seu método que captura dia, mes e ano atual do seu sistema.
dd, mm, yyyy = rpa.date.get_dmy()

# Usando a variavel date (objeto Date já instanciado) acessamos seu método que captura hora, segundos e minutos atual do seu sistema.
hour, minute, sec = rpa.date.get_hms()

# exibindo o retorno obtido para data
rpa.info_print(f'{dd}/{mm}/{yyyy}')

# exibindo o retorno obtido para horario
rpa.info_print(f'{hour}/{minute}/{sec}')
```

<br>

## Clock

CLock é um Objeto dedicado a fazer controle de execução quando é necessario aguardar para executar, executar e aguardar ou até mesmo executar num horario especifico determinado bloco de código, funções e até mesmo servir como uma especie de Schedule para execução do seu RPA. 

Abaixo todos métodos e argumentos disponiveis de **Clock**:


Metodo ``exec_at_hour``:
- Função temporizada, executa a função no horário especificado, por ``default`` executa no momento da chamada em tempo de execução, opcionalmente pode escolher o horário para execução, sendo uma string contendo horas e minutos com dois digitos como demonstrado a seguir: ``hh:mm``

- Parametros:
  - ``hour_to_exec``: Horario para execução do tipo ``string`` `hh:mm`
  - ``fn_to_exec``: Sua função que deseja que execute.
  - ``*args*``: Argumentos posicionais da sua função.
  - ``**kwargs``: Argumentos nomeados da sua função.

<br>

Metodo ``wait_for_exec``:
- Função temporizada, aguarda uma quantidade de tempo em segundos para executa a função em seguida, por ``default`` executa no momento da chamada em tempo de execução.

- Parametros:
  - ``wait_time``: Tempo em segundos para aguardar, tipo ``int``
  - ``fn_to_exec``: Sua função que deseja que execute.
  - ``*args*``: Argumentos posicionais da sua função.
  - ``**kwargs``: Argumentos nomeados da sua função.

<br>

Metodo ``exec_and_wait``:
- Função temporizada, executa a função do argumento e em seguinda aguarda o tempo desejado em segundos, por ``default`` executa no momento da chamada em tempo de execução.

- Parametros:
  - ``wait_time``: Tempo em segundos para aguardar após execução, tipo ``int``
  - ``fn_to_exec``: Sua função que deseja que execute.
  - ``*args*``: Argumentos posicionais da sua função.
  - ``**kwargs``: Argumentos nomeados da sua função.

<br>

> Se desejar importar ou instanciar de outra forma veja o guia na parte de "Componentes" ou "Formas de Uso".
>
> Também é possivel fazer o import da seguinte forma, para usar o Objeto isolado:
>
> `from rpa_suite.core import Clock`

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
# >>> 27
# >>> sum: Successfully executed!

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
# >>> 27
# >>> Function: wait_for_exec executed the function: sum.

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


### ***Other modules guide comming soon!***



