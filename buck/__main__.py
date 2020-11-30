from . import router
from . import middleware
# from . import storage
from . import responses
from . import exceptions
from . import stack
from . import s3

import uvicorn
import fastapi
import typer
import functools

import rich # TODO: Use me!

from pprint import pprint as pp # Dev

api = fastapi.FastAPI()
cli = typer.Typer()

api.include_router(router.router)

# Defaults
PORT = 8000
HOST = '127.0.0.1'
AUTH = None
MODE = None
DIR  = None

def app \
        (
            port: int = typer.Option(PORT, help = 'Port to bind server to'),
            host: str = typer.Option(HOST, help = 'Host to bind server to'),
            auth: str = typer.Option(AUTH, help = 'Auth to use for server in form: `key` or `access_key:secret_key`'),
            mode: str = typer.Option(MODE, help = 'Mode to use (mem, fs)'),
            dir:  str = typer.Option(DIR,  help = 'Directory to serve (implies --mode fs)'),
        ):
    s3_services = \
    {
        'mem': \
        {
            'service': s3.memory.SimpleStorageService,
            'args': {},
        },
        'fs': \
        {
            'service': s3.fs.SimpleStorageService,
            'args': \
            {
                'path': 'dir',
            },
        },
    }

    if dir is not None and mode is None:
        mode = 'fs'

    if mode == 'fs' and dir is None:
        dir = '.'

    if mode is None:
        mode = 'fs'
        dir = '.'

    if mode not in s3_services:
        modes = tuple(s3_services)

        typer.echo(f'Invalid mode {mode!r}, must be one of: {modes!r}')

        raise typer.Exit(code = 1)

    s3_service = s3_services[mode]['service']

    vars = dict(locals())

    kwargs = \
    {
        kwarg_key: vars.get(var_key)
        for kwarg_key, var_key in s3_services[mode]['args'].items()
    }

    s3_service_wrapper = functools.partial(s3_service, **kwargs)

    api.stack = stack.Stack('buck')

    api.stack.add_service('s3', s3_service_wrapper)

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
