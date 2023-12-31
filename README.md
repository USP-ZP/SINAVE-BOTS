# SINAVE-BOTS

Ferramenta para "limpar" as notificações e casos de SARS-CoV-2/COVID do SINAVE.

## Autor
Programado por [Estêvão Soares dos Santos](https://github.com/tivie)

## Instruções rápidas

1. Clone o repositório

    ```bash
    git clone git@github.com:USP-ZP/SINAVE-BOTS.git
    ```

    NOTA: Se não tem o Git instalado, veja as instruções aqui: https://git-scm.com/book/en/v2/Getting-Started-Installing-Git

2. Instale as dependências com o poetry

    ```bash
    poetry install
    ```

    NOTA: Se não tem o poetry ou o python instalado, siga as instruções aqui: https://python-poetry.org/docs/

3. Crie um ficheiro chamado `config.yaml` com as suas credenciais do SINAVE

    ```yaml
    credenciais:
      username: "arnaldo.bento"
      password: "umaPasswordSuperDificil"
    ```

4. Corra o bot `python main.py`


## Exemplo de ficheiro de configuração

```yaml
credenciais:
  username: "arnaldo.bento"
  password: "umaPasswordSuperDificil"
logs:
  filename: "./logs.log"
  filemode: "a"
settings:
  concelho: "Caldas da Rainha"
```
