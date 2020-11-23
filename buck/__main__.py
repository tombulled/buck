from . import router
from . import middleware
from . import storage
from . import responses
from . import exceptions

import uvicorn
import fastapi
import typer

api = fastapi.FastAPI()
cli = typer.Typer()

@api.exception_handler(exceptions.S3Error)
async def exception_handler(request: fastapi.Request, exception: exceptions.S3Error):
    status_code = exception.status_code or 400

    error = \
    {
        'code':    exception.code,
        'message': exception.description,
    }

    return responses.AwsErrorResponse(error, status_code = status_code)

api.include_router(router.router)

# Defaults
HOST = '127.0.0.1'
PORT = 8000
DIR  = '.'

def app \
        (
            port: int = typer.Option(PORT, help = 'Port to bind server to'),
            host: str = typer.Option(HOST, help = 'Host to bind server to'),
            dir:  str = typer.Option(DIR,  help = 'Directory to serve'),
            auth: str = typer.Option(None, help = 'Auth to use for server in form: `key` or `access_key:secret_key`'),
        ):
    if auth is not None:
        chunks = auth.split(':')

        if len(chunks) == 1:
            access_key = chunks[0]
            secret_key = chunks[0]
        else:
            access_key, secret_key, *_ = chunks

        api.add_middleware(middleware.AwsAuthenticationMiddleware)
    else:
        api.add_middleware(middleware.AwsAnonymousAuthenticationMiddleware)

    # api.storage = storage.SimpleStorageService()
    api.storage = storage.FSSimpleStorageService(dir)

    uvicorn.run \
    (
        api,
        host = host,
        port = port,
        log_level = 'info',
    )

if __name__ == '__main__':
    typer.run(app)
