from . import router
from . import middleware
from . import responses
from . import exceptions
from . import stack
# from . import s3
from .stack.services import s3

import uvicorn
import fastapi
import typer
import functools

import fs

from pprint import pprint as pp # Dev

api = fastapi.FastAPI()
cli = typer.Typer()

api.include_router(router.router)

# Defaults
PORT = 8000
HOST = '127.0.0.1'
AUTH = None
MEM  = False
DIR  = '.'

def app \
        (
            dir:     str  = typer.Argument(DIR),
            port:    int  = typer.Option(PORT, help = 'Port to bind server to'),
            host:    str  = typer.Option(HOST, help = 'Host to bind server to'),
            auth:    str  = typer.Option(AUTH, help = 'Auth to use for server in form: `key` or `access_key:secret_key`'),
            virtual: bool = typer.Option(MEM, '--mem', help = 'Whether to use in-memory filesystem'),
        ):
    if virtual:
        s3_service = s3.S3Mem
    else:
        s3_service = functools.partial(s3.S3Fs, dir = dir)

    api.stack = stack.Stack('buck')

    api.stack.add_service('s3', s3_service)

    if auth is not None:
        chunks = auth.split(':')

        if len(chunks) == 1:
            access_key = chunks[0]
            secret_key = chunks[0]
        else:
            access_key, secret_key, *_ = chunks

        user = api.stack.add_user \
        (
            name       = 'User',
            access_key = access_key,
            secret_key = secret_key,
        )

        api.add_middleware \
        (
            middleware.AwsAuthenticationMiddleware,
            stack = api.stack,
        )
    else:
        user = api.stack.add_user \
        (
            name = 'Anonymous',
        )

        api.add_middleware \
        (
            middleware.AwsAnonymousAuthenticationMiddleware,
            stack = api.stack,
            user = user,
        )

    # @api.exception_handler(exceptions.S3Error)
    # async def unicorn_exception_handler(request: fastapi.Request, exc: exceptions.S3Error):
    #     return fastapi.JSONResponse(
    #         status_code=418,
    #         content={"message": f"Oops! {exc.name} did something. There goes a rainbow..."},
    #     )

    # Make this exception_handler middleware: AwsExceptionHandlerMiddleware
    @api.middleware('http')
    async def middleware_catch_exception(request: fastapi.Request, call_next):
        exception = None

        try:
            return await call_next(request)
        except exceptions.S3Error as error:
            exception = error
        except Exception as error:
            exception = exceptions.S3Error('InternalError')

            exception.description = str(error)

            # Temp?
            raise error

        status_code = exception.status_code or 400

        error = \
        {
            'code':    exception.code,
            'message': exception.description,
        }

        return responses.AwsErrorResponse(error, status_code = status_code)

    uvicorn.run \
    (
        api,
        host = host,
        port = port,
        log_level = 'info',
    )

if __name__ == '__main__':
    typer.run(app)
