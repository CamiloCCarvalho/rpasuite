# Suite RPA: 

## Kit de ferramentas para o desenvolvimento do seu bot, automação ou projeto.

**Versatil**: Embora criado com foco no desenvolvimento de BOTs em RPA, as ferramentas são de uso geral, podem ser *aplicadas também em outros modelos de projetos além do RPA*.

**Simples**: Contruimos as ferramentas de maneira mais direta e acertiva possivel e usando apenas libs conhecidas no mercado, para melhor aproveitamento e performance possivel.

## Objetivo:

Estamos tornando mais produtivo o desenvolvimento de *RPAs*, proporcionando funções prontas para usos comuns como:

- envio de emails (configurações já pré-montadas)
- validação de emails (limpeza e tratamento de listas)
- busca por palavras ou patterns em textos ou cadeias de string
- criação de pastas e arquivos temporarios e deleta-los com apenas um comando
- console com mensagens de melhor visualização com cores definidas para alerta, erro, informativo e sucesso.
- e muitas outras facilidades

### Instalação:
    >>> python -m pip install rpa-suite

### Dependencias:
No setup do nosso projeto já estão inclusas as dependencias, só será necessario instalar nossa **Lib**, mas segue a lista das libs usadas:
- colorama
- loguru
- email-validator
  
### Estrutura do modulo:
O modulo principal do rpa-suite é dividido em categorias, onde por sua vez tem os modulos com funções destinadas a cada tipo de tarefa.
- **rpa_suite**
    - **clock**
        - **waiter** - modulo com funções responsaveis por aguardar
    - **email**
        - **sender_smtp** - modulo com funções para envio de email SMPT 
    - **file**
        - **counter** - modulo com funções responsaveis por contagens
        - **temp_dir** - modulo com funções responsaveis por diretórios temporarios
    - **log**
        - **loggin** - modulo com funções responsaveis por gerar decoradores de de print para logs de execução
        - **printer** - modulo com funções de print personalizados para notificações em prompt
    - **validate**
        - **mail_validator** - modulo com funções para validação de emails
        - **string_validator** - modulo com funções para validação e varredura de strings / substrings / palavras

### Versão do projeto:
Ultima versão release: **Alpha 0.4.3**
Data da ultima versão: 23/11/2023
Status: Em Desenvolvimento

### Mais Sobre:

Você pode ver mais com mais detalhes no **Github**.
https://github.com/CamiloCCarvalho/rpa_suite
