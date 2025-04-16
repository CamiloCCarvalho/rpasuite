# Overview

**RPA Suite** é uma biblioteca voltada para o uso em desenvolvimento de bots e RPAs profissionais.
Com ferramentas que **aceleram o desenvolvimento**, reduzindo o tempo necessario para desenvolver pequenos blocos que são responsaveis por tarefas muito comuns e repetitivas no mundo dos RPAs.

## Components

Os componentes são divididos por categoria de atuação ou de funcionalidade. Estão organizados na subpasta *core*.
Você pode fazer a importação de pelo menos duas formas diferentes.

<hr>
<br>

## Quick Start

### Exemplo de uso pratico

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

## Formas de uso

### Forma 1:

rpa é um objeto já instanciado com os demais modulos (objetos) instanciados sendo atributos do Objeto principal rpa.

Assim sendo, você pode acessar diretamente os methodos do submodulo que esta usando em uma unica linha.

```python
# O código a baixo deve funcionar
from rpa_suite import rpa
rpa.log.config_logger(...)

```

### Forma 2:

Também deixamos o acesso facilitado para você importar as proprias classes para instaciar seus objetos para trabalhar de forma modular se assim desejar.

Com isso também pode ser feito o acesso a todos recursos acessando a partição "**core**".

```python

# O código a baixo deve funcionar
from rpa_suite.core import AsyncRunner, Clock, Date, Directory, ...

# clame pela classe e instacie seu objeto
my_clock_obj = Clock()

# exemplo de uso 
my_clock_obj.exec_at(...)

```

### Forma 3:

Se ainda não estiver bom, voce também pode importar a classe de Suite assim podendo instanciar quando desejar e usar da mesma forma que a varaivel rpa pré-instanciada.

Assim, pode ter a flexibilidade necessaria.

```python

# O código a baixo deve funcionar
from rpa_suite.suite import Suite

# clame pela classe Suite esta deixara os submodulos instanciados prontos para uso
my_rpa_obj = Suite()

# exemplo de uso 
hour, minutes, secs = my_rpa_obj.date.get_hms()

```

<hr>
<br>

# Guia de Modulos

## Print

Print é um submodulo do nosso conjunto. Este tem um caracteristica difernente dos demais.
Este possui a sua classe (Print) em um arquivo dentro de "**core**" chamado "print.py".

Mas também é feita a implementação de todas seus methodos diretamente no objeto Suite a finalidade é facilitar seu uso já que provavelmente é a função mais utilizada da lib no dia a dia provavelmente.

Abaixo todos métodos disponiveis de **Print** e seu uso.

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
> se desejar importar ou instanciar de outra forma veja o guia na parte de "Componentes" ou "Formas de Uso".

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

```python

# Importação do objeto de Suite e Colors
from rpa_suite import rpa
from rpa_suite.core.print import Colors

# Passagem de argumentos, mudança de comportamento e cores
rpa.success_print(f'It`s red now!', color=Colors.RED)
rpa.alert_print(f"This don't breakline on ending", ending=' ')
rpa.error_print(f'This message display on same line to alert.')

# Exemplo com todos argumentos explicitos
rpa.info_print(string_text=f'All arguments explicts',
               color=Colors.BLUE,
               ending="\n\n"
              )
```


