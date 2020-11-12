from . import main

import uvicorn
import fastapi
import typer

cli = typer.Typer()

def get_app(module):
    for attr_key, attr_val in main.__dict__.items():
        if isinstance(attr_val, fastapi.FastAPI):
            return f'{module.__name__}:{attr_key}'

# Defaults
HOST = '127.0.0.1'
PORT = 8000

def app \
        (
            port: int = typer.Option(PORT, help = 'Port to run ASGI server on'),
            host: str = typer.Option(HOST, help = 'Host to bind ASGI server on'),
            db: str = typer.Option(None, help = 'Path to sqlite database'),
        ):
    if not (app := get_app(main)):
        raise Exception('no api found :/') # Error

    uvicorn.run \
    (
        app,
        host = host,
        port = port,
        log_level='info',
    )

if __name__ == '__main__':
    typer.run(app)
