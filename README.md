![RPA Suite](https://raw.githubusercontent.com/CamiloCCarvalho/rpa_suite/db6977ef087b1d8c6d1053c6e0bafab6b690ac61/logo-rpa-suite.svg)

<h1 align="left">
    RPA Suite
</h1>
<br>

![PyPI Latest Release](https://img.shields.io/pypi/v/rpa-suite.svg)
<<<<<<< HEAD
[![PyPI Downloads](https://static.pepy.tech/badge/rpa-suite/month)](https://pepy.tech/projects/rpa_suite)
![PyPI Downloads](https://img.shields.io/pypi/dm/rpa-suite.svg?label=PyPI%20downloads)
[![PyPI version](https://img.shields.io/pypi/v/rpa-suite)](https://pypi.org/project/rpa-suite/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/rpa-suite)](https://pypi.org/project/rpa-suite/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: pyautogui](https://img.shields.io/badge/%20imports-pyautogui-%231674b1?style=flat&labelColor=ef8336)](https://github.com/asweigart/pyautogui)
[![Imports: loguru](https://img.shields.io/badge/%20imports-loguru-%231674b1?style=flat&labelColor=ef8336)](https://github.com/Delgan/loguru)
[![License MIT](https://img.shields.io/github/license/docling-project/docling)](https://opensource.org/licenses/MIT)
[![rpa-suite Actor](https://apify.com/actor-badge?actor=camiloccarvalho/rpasuite?fpr=rpa-suite)](https://apify.com/camiloccarvalho/rpasuite)


## O que é?
**RPA Suite:** um conjunto abrangente de ferramentas projetadas para simplificar e otimizar o desenvolvimento de projetos de automação RPA com Python. Embora nossa suíte seja um conjunto de Ferramentas de RPA especializado, sua versatilidade a torna igualmente útil para uma ampla gama de projetos de desenvolvimento. Esta desenvolvendo com Selenium, Botcity ou Playwright? Experimente a RPA Suite e descubra como podemos facilitar seu projeto, ou qualquer projeto de Robôs de Software.

## Sumário do conteudo

<<<<<<< HEAD
- [O que é?](#o-que-é)
- [Sumário do conteudo](#sumário-do-conteudo)
- [Destaque](#destaque)
- [Objetivo](#objetivo)
- [Instalação](#instalação)
- [Exemplo](#exemplo)
- [Dependências](#dependências)
- [Estrutura do módulo](#estrutura-do-módulo)
<<<<<<< HEAD
- [Release](#release)
- [Mais Sobre](#mais-sobre)

- [Notas da atualização: 1.4.9](#notas-da-atualização-149)


## Destaque

**Versátil**: Além da Automação de Processos e criação de BOT em RPA, mas também para uso geral podendo  ser aplicadas em outros modelos de projeto, *além do RPA*.

**Simples**: Construímos as ferramentas de maneira mais direta e assertiva possível, utilizando apenas bibliotecas conhecidas no mercado para garantir o melhor desempenho possível.

## Objetivo

Nosso objetivo é se tornar a Biblioteca Python para RPA referência. Tornando o desenvolvimento de RPAs mais produtivo, oferecendo uma gama de funções para tal:

- Envio de emails (já configurado e personalizavel)
- Validação de emails (limpeza e tratamento)
- Busca por palavras, strings ou substrings (patterns) em textos.
- Criação e deleção de pasta/arquivo temporário com um comando
- Console com mensagens de melhor visualização com cores definidas para alerta, erro, informativo e sucesso.
- E muito mais

## Instalação
<<<<<<< HEAD

Para **instalar** o projeto, utilize o comando:

```python
>>> python -m pip install rpa-suite
```

ou no conda:

```python
conda install -c conda-forge rpa-suite
```

Após instalação basta fazer a importação do modulo rpa que ja tera um objeto instanciado de ``suite``:

```python
from rpa_suite import rpa
```

Feito isso já estará pronto para o uso:

```python
# function send mail by SMTP 
rpa.email.send_mail(...)
```

> [!NOTE]
>
> Para **desinstalar** o projeto, utilize o comando abaixo:
>
> ```python
> python -m pip uninstall rpa-suite
> ```
>
> **Observação:** Caso necessário, desinstale também as bibliotecas utilizadas no projeto, como `loguru`, `mail_validator`, `colorama`, `pillow`, e `pyautogui`.

> **⚠️ IMPORTANTE:**  
> Opcionalmente, você pode querer desinstalar as bibliotecas que foram incluídas no projeto. Para isso, utilize o seguinte comando:  
>
> ```python
> python -m pip uninstall loguru mail_validator colorama pillow pyautogui
> ```

## Exemplo

Do módulo principal, importe a suite. Ela retorna uma instância do Objeto de classe Rpa_suite, onde possui variáveis apontando para todas funções dos submódulos:

```python
from rpa_suite import rpa

# Exemplo com função de execução em horário específico
rpa.clock.exec_at_hour('13:53', my_function, param_a, param_b)

# Usando submódulo clock para aguardar 30(seg) para executar minha função
time = 30
rpa.clock.wait_for_exec(time, my_function, param1, param2)

# Usando submódulo email para envio de email por SMTP comum
rpa.email.send_smtp(...)
```

## Dependências

No setup do nosso projeto já estão inclusas as dependências, só será necessário instalar nossa **Lib**, mas segue a lista das libs usadas:

=======
Para **instalar** o projeto, utilize o comando:

~~~python
>>> python -m pip install rpa-suite
~~~
ou no conda:
~~~python
conda install -c conda-forge rpa-suite
~~~

Após instalação basta fazer a importação do modulo e instanciar o Objeto ``suite``:
~~~~python
from rpa_suite import suite as rpa
~~~~

Feito isso já estará pronto para o uso:
~~~~python
# function send mail by SMTP 
rpa.send_mail(...)
~~~~

>[!NOTE]
>
>Para **desinstalar** o projeto, utilize o comando abaixo.
>**Obs.:** como usamos algumas libs no projeto, lembre-se de desinstar elas caso necessário.

~~~~python
>>> python -m pip uninstall rpa-suite
~~~~

>[!IMPORTANT]
>
>Opcionalmente você pode querer desinstalar as libs que foram inclusas no projeto, sendo assim:

~~~~python
>>> python -m pip uninstall loguru mail_validator colorama
~~~~


## Exemplo
Do módulo principal, importe a suite. Ela retorna uma instância do Objeto de classe Rpa_suite, onde possui variáveis apontando para todas funções dos submódulos:

    from rpa_suite import suite as rpa

    # Usando a função de envio de email por SMTP default
    rpa.send_email(my_email, my_pass, mail_to, subject, message_body)


    # Usando submódulo clock para aguardar 30 (seg) e então executar uma função
    time = 30
    rpa.wait_for_exec(time, my_function, param1, param2)


## Dependências
No setup do nosso projeto já estão inclusas as dependências, só será necessário instalar nossa **Lib**, mas segue a lista das libs usadas:
>>>>>>> e971ae6b515cb8571860561478181761d2fe56d3
- colorama
- loguru
- email-validator
- colorlog
<<<<<<< HEAD
- pillow
- pyautogui
- typing
- setuptools

  opcionalmente para automação de navegador:

  - selenium
  - webdriver_manager

<br>
<hr>
<br>

> **⚠️ IMPORTANTE:**  
> No caso da função de screenshot, é necessário ter as bibliotecas `pyautogui`, `pillow` e `pyscreeze` instaladas. Geralmente, a instalação de `pyautogui` já inclui as demais dependências necessárias.

## Estrutura do módulo

O módulo principal do rpa-suite é dividido em categorias. Cada categoria contém módulos com funções destinadas a categoria:

- **rpa_suite**
  
  - **clock**
    - **exec_at_hour** - Função que executa uma função no horário especificado "xx:yy", permitindo agendamento de tarefas com precisão.
    - **wait_for_exec** - Função que aguarda um tempo em segundos antes de executar a função passada como argumento.
    - **exec_and_wait** - Função que executa uma função e, em seguida, aguarda um tempo em segundos antes de continuar.
  
  - **date**
    - **get_hms** - Função que retorna hora, minuto e segundo formatados como strings.
    - **get_dmy** - Função que retorna dia, mês e ano formatados como strings.
  
  - **email**
    - **send_smtp** - Função para envio de emails via SMTP com suporte a anexos e mensagens HTML, configurável e personalizável.

  - **file**
    - **screen_shot** - Função para capturar screenshots, criando diretórios e arquivos com nomes e caminhos personalizáveis.
    - **flag_create** - Função para criar arquivos de flag indicando execução de processos.
    - **flag_delete** - Função para deletar arquivos de flag após a execução de processos.
    - **count_files** - Função para contar arquivos em diretórios, com suporte a extensões específicas.

  - **directory**
    - **create_temp_dir** - Função para criar diretórios temporários com nomes e caminhos personalizáveis.
    - **delete_temp_dir** - Função para deletar diretórios temporários, com opção de remover arquivos contidos.

  - **log**
    - **config_logger** - Função para configurar logs com suporte a arquivos e streams, utilizando a biblioteca Loguru.
    - **log_start_run_debug** - Função para registrar logs de início de execução em nível de depuração.
    - **log_debug** - Função para registrar logs em nível de depuração.
    - **log_info** - Função para registrar logs em nível informativo.
    - **log_warning** - Função para registrar logs em nível de aviso.
    - **log_error** - Função para registrar logs em nível de erro.
    - **log_critical** - Função para registrar logs em nível crítico.

  - **printer**
    - **success_print** - Função para imprimir mensagens de sucesso com destaque em verde.
    - **alert_print** - Função para imprimir mensagens de alerta com destaque em amarelo.
    - **info_print** - Função para imprimir mensagens informativas com destaque em ciano.
    - **error_print** - Função para imprimir mensagens de erro com destaque em vermelho.
  - **regex**
    - **check_pattern_in_text** - Função para verificar a presença de padrões em textos, com suporte a case-sensitive.
  
  - **validate**
    - **emails** - Função para validar listas de emails, retornando listas de emails válidos e inválidos.
    - **word** - Função para buscar palavras ou padrões específicos em textos, com suporte a contagem de ocorrências.
  
  - **browser**
    - **start_browser** - Função para iniciar o navegador Chrome com suporte a depuração remota.
    - **find_ele** - Função para localizar elementos na página utilizando estratégias de localização do Selenium.
    - **get** - Função para navegar para URLs específicas.
    - **close_browser** - Função para fechar o navegador e encerrar processos relacionados.

  - **parallel**
    - **run** - Função para iniciar um processo em paralelo.
    - **is_running** - Função para capturar o status atual do processo que esta rodando em paralelo.
    - **get_result** - Função para coletar o retorno da execução em paralelo junto com resultado da função ou funções que foram enviadas a este processo com retorno em forma de dict.
    - **terminate** - Função para finalizar o processo paralelo mantendo apenas o processo principal do seu código, também é chamada de forma automatica esta função ao final de um procesos paralelo ou no final da função "get_result".

  - **async**
    - **run** - Função para iniciar a execução assíncrona de uma função mantendo o fluxo principal da aplicação.
    - **is_running** - Função para verificar se a tarefa assíncrona ainda está em execução.
    - **get_result** - Função para obter o resultado da execução assíncrona, incluindo tempo de execução e status, com suporte a timeout.
    - **cancel** - Função para cancelar a tarefa assíncrona em execução.

## Release Notes

### Versão: **Beta 1.5.0**

- **Data de Lançamento:** *20/02/2024*  
- **Última Atualização:** *15/04/2025*  
- **Status:** Em desenvolvimento  

Esta versão marca um grande avanço no desenvolvimento da RPA Suite, trazendo melhorias significativas na arquitetura, novas funcionalidades e maior simplicidade no uso. Confira as principais mudanças na seção [Notas da atualização: 1.5.0](#notas-da-atualização-150).

### Notas da atualização: 1.5.0

- Submódulos agora são objetos internos do objeto principal `Suite`, acessíveis via `rpa.modulo.function()` ou diretamente pelo submódulo.
- Estrutura reformulada para maior simplicidade, com pastas `core` (núcleo) e `utils` (ferramentas utilitárias).
- Novo submódulo `Parallel` para execução de processos em paralelo com suporte a timeout e recuperação de resultados.
- Novo submódulo `AsyncRunner` para facilitar o uso de funções assíncronas com menos código.
- Adicionado suporte à automação de navegadores (inicialmente apenas Chrome).
- Função `get_dma` renomeada para `get_dmy` para padronização em inglês.
- Função `send_email` simplificada para maior compatibilidade.
- Melhorias nas descrições e adição de docstrings em todas as funções e objetos.
- Submódulo de logs unificado com Loguru, agora com suporte a configuração de diretórios, nomes de arquivos e streams para console e arquivo.
- Regex e busca em textos simplificados, com novas funcionalidades planejadas.
- Melhorias gerais na arquitetura e correções de bugs.


## Mais Sobre

Para mais informações, visite os links abaixo:

- **[Repositório no GitHub](https://github.com/CamiloCCarvalho/rpa_suite)**  
  Explore o código-fonte, contribua com melhorias e acompanhe o desenvolvimento do projeto.

- **[Página no PyPI](https://pypi.org/project/rpa-suite/)**  
  Confira a documentação oficial, instale a biblioteca e veja as versões disponíveis.

---

=======

[!IMPORTANT]
No caso da função de screenshot é necessario ter as libs 'pyautogui' 'pillow' e 'pyscreeze' instalados, geralmente a instalação de pyautogui já instala as demais dependências deste caso.
  
## Estrutura do módulo
O módulo principal do rpa-suite é dividido em categorias. Cada categoria contém módulos com funções destinadas a cada tipo de tarefa
- **rpa_suite**
    - **clock**
        - **waiter** - Função capaz de aguardar para executar a função do argumento, ou executar a função do argumento para aguardar posteriormente
        - **exec_at** - Função capaz de executar a função do argumento no horario especificado "xx:yy" parecido com scheduler, porem com a vantagem de ter o horario como variavel dentro do escopo de código podendo gerar variações pela propria natureza da aplicação
    - **date**
        - **date** - Funções capazes de extrair dia/mes/ano e hora/min/seg, facilitando a necessidade de formatar o resultado de datetime, a função ja devolve os valores em trio formatados em string
    - **email**
        - **sender_smtp** - Funções para envio de email SMPT com configuração simples já default porem personalizavel
    - **file**
        - **counter** - Funções para contagem de arquivos
        - **temp_dir** - Funções para diretórios temporários
        - **screen_shot** -  Função para criar diretório e arquivo de print com nome do diretório, arquivo e delay personalizáveis
        - **file_flag** -  Funções para criar e deletar arquivo utilizado como flag de execução, tendo path e nome do arquivo já automatico porem personalizavel para se adequar ao seu projeto
    - **log**
        - **logger_uru** - Instanciador de stream e handlefile que cria na pasta raiz do arquivo chamador pasta de log e seta o stream para as funções de log
        - **functions_logger_uru** - Funções de log parecida com os prints personalizados, setadas e personalizadas para todos log levels usado pelo ´logger_uru´, já escreve no arquivo setado além de gerar o print no terminal
        - **printer** - Funções de print personalizados (alerta, erro, sucesso, informativo)
    - **regex**
        - **pattern_in_text** - Função para otimizar o uso mais comum de regex buscando padrões em um texto
    - **validate**
        - **mail_validator** - Função para validar lista de emails, devolvendo a lista com emails validos a partir da lista original 
        - **string_validator** - Função que valida presença de letras, palavras, e textos e possibilita contar as ocorrencias em uma string

## Release
Versão: **Beta 1.3.1**

Lançamento: *20/02/2024*

Última atualização: *10/11/2024*

Status: Em desenvolvimento.

#
### Notas da atualização: 1.3.1

- Correções de bugs em diversas funções relacionadas a tempo: *exec_at_hour* , *wait_for_exec* , *exec_and_wait*
- Correções de bugs com tempo superior a 10 minutos nas funções de data: *get_hms* e *get_dma*
- Função **get_dma** atualizada e **renomeada** para **get_dmy** para manter o padrão em ingles
- Função *send_email* atualizada para suportar autenticação *SSL* ou *TLS* via argumentos recebidos nos parametros
- Adicionado parametro de *"display_message"* para o usuario poder ativar ou desativar as mensagens de console em cada função
- Correção de bug na função *"count_files"* para realizar de maneira correta a soma de todos arquivos nos diretórios
- Funções de regex e busca em textos por strings e palavras atualizadas
- Implementado nova função para arquivo de flag para execuções, no submodulo file, as funções são: *"file_flag_create"* e *"file_flag_delete"*
- correção de imports no arquivo suite.py das funções *"get_dmy"* e *"search_str_in"*
- ajuste de cores no svg da logo rpa-suite

## Mais Sobre

Para mais informações, visite nosso projeto no Github ou PyPi:
<br>
<a href='https://github.com/CamiloCCarvalho/rpa_suite' target='_blank'>
    Ver no GitHub.
</a>
<br>
<a href='https://pypi.org/project/rpa-suite/' target='_blank'>
    Ver projeto publicado no PyPI.
</a>

<hr>
>>>>>>> e971ae6b515cb8571860561478181761d2fe56d3
