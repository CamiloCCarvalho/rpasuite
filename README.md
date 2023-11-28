<div style="text-align:center">
    <img src='./logo-rpa-suite.png' alt='Logo - RPA Suite' width='56px'>
</div>
<h1 style="text-align:center">
    Suite RPA
</h1> 

## Kit de ferramentas para o desenvolvimento do seu bot, automação ou projeto.

**Versátil**: Embora tenha sido criado com foco no desenvolvimento de BOTs em RPA, as ferramentas são de uso geral e podem ser aplicadas em outros tipos de projetos, *além do RPA*.

**Simples**: Construímos as ferramentas de maneira mais direta e assertiva possível, utilizando apenas bibliotecas conhecidas no mercado para garantir o melhor aproveitamento e desempenho possível.

## Objetivo:

Nosso objetivo é tornar o desenvolvimento de RPAs mais produtivo, oferecendo funções prontas para usos comuns, como:

- envio de emails (configurações já pré-montadas)
- validação de emails (limpeza e tratamento de listas)
- busca por palavras ou patterns em textos ou cadeias de string
- criação de pastas e arquivos temporarios e deleta-los com apenas um comando
- console com mensagens de melhor visualização com cores definidas para alerta, erro, informativo e sucesso.
- e muitas outras facilidades

### Instalação:
Para instalar o projeto, utilize o comando

    >>> python -m pip install rpa-suite

### Dependencias:
No setup do nosso projeto já estão inclusas as dependencias, só será necessario instalar nossa **Lib**, mas segue a lista das libs usadas:
- colorama
- loguru
- email-validator
  
### Estrutura do módulo:
O módulo principal do rpa-suite é dividido em categorias. Cada categoria contém módulos com funções destinadas a cada tipo de tarefa
- **rpa_suite**
    - **clock**
        - **waiter** - módulo com funções para aguardar execução
    - **email**
        - **sender_smtp** - módulo com funções para envio de email SMPT 
    - **file**
        - **counter** - módulo com funções para contagens
        - **temp_dir** - módulo com funções para diretórios temporarios
    - **log**
        - **loggin** - módulo com funções responsaveis por gerar decoradores de de print para logs de execução
        - **printer** - módulo com funções de print personalizados para notificações em prompt
    - **validate**
        - **mail_validator** - módulo com funções para validação de emails
        - **string_validator** - módulo com funções para validação e varredura de strings / substrings / palavras

### Versão do projeto:
A versão mais recente é a **Alpha 0.4.6**, lançada em *23/11/2023*. O projeto está atualmente em desenvolvimento.

### Mais Sobre:

Para mais informações, visite nosso projeto no Github ou PyPi:
<a href='https://github.com/CamiloCCarvalho/rpa_suite' target='_blank'>
    Ver no GitHub.
</a>
<a href='https://pypi.org/project/rpa-suite/' target='_blank'>
    Ver projeto publicado no PyPi.
</a>
