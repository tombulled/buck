from .api import Api

import typer

def cli \
        (
            # Arguments
            dir: str  = typer.Argument('.'),

            # Options
            port:    int  = typer.Option(8000,        help = 'Port to bind server to'),
            host:    str  = typer.Option('127.0.0.1', help = 'Host to bind server to'),
            auth:    str  = typer.Option(None,        help = 'Auth to use for server in form: `key` or `access_key:secret_key`'),
            virtual: bool = typer.Option(False,       help = 'Whether to use in-memory filesystem'),
        ):
    api = Api \
    (
        anonymous = auth is None,
        path      = None if virtual else dir,
    )

    if auth is not None:
        chunks = auth.split(':')

        if len(chunks) == 1:
            access_key = chunks[0]
            secret_key = chunks[0]
        else:
            access_key, secret_key, *_ = chunks

        api.add_user \
        (
            name       = 'User',
            access_key = access_key,
            secret_key = secret_key,
        )

    api.serve \
    (
        host = host,
        port = port,
    )
