# steganography-api


## Instalações e rodar projeto

Instalações necessárias para rodar a aplicação:

criar ambiente com `py -m venv .venv`

ativar o ambiente com `.\.venv\Scripts\Activate.ps1`

se der erro rodar `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass .\.venv\Scripts\Activate.ps1`

instalar dependências com `python -m pip install fastapi uvicorn python-multipart pillow reportlab`


## Explicando o comando `uvicorn main:app --reload` para rodar o projeto

### `uvicorn`

É o servidor que vai executar a aplicação FastAPI.
Por padrão abre a porta 8000 exemplo: `http://127.0.0.1:8000`

### `main`

Indica qual arquivo Python contém a aplicação FastAPI. No caso, o arquivo `main.py`.

### `:app`

O `:` separa o nome do arquivo do nome da variável. Ou, mais precisamente o módulo do objeto. Exemplo `módulo : objeto`. 

### `--reload`

O `--reload` indica que o servidor deve reiniciar automaticamente sempre que houver alterações no código. Isso é útil durante o desenvolvimento, pois permite ver as mudanças sem precisar reiniciar manualmente o servidor.


## Explicando código

