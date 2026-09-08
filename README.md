# steganography-api

## Instalações

Instalações necessárias para rodar a aplicação:

`pip install pillow python-multipart fastapi uvicorn`

## Explicando o comando `uvicorn main:app --reload ` para rodar o projeto

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

