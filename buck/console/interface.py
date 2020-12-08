from . import cli
from .. import api
from .. import __name__, __version__
from pathlib import Path

app: cli.Cli = cli.Cli \
(
    name    = __name__,
    version = __version__,
)

@app.example('/mnt/data', auth = 'access_key:secret_key')
@app.example(virtual = True, auth = 'admin')
@app.example(host = '0.0.0.0', port = 8080)
@app.example('/tmp/store')
@app.command()
def main \
        (
            dir: Path  = cli.Argument \
            (
                '.',
                help         = 'Bucket storage directory',
                exists       = True,
                file_okay    = False,
                dir_okay     = True,
                writable     = True,
                readable     = True,
                resolve_path = True,
            ),
            port:    int  = cli.Option(8000,        help = 'Port to bind server to'),
            host:    str  = cli.Option('127.0.0.1', help = 'Host to bind server to'),
            auth:    str  = cli.Option(None,        help = 'Client auth key(s)'),
            virtual: bool = cli.Option(False,       help = 'Whether to use in-memory mode'),
            dev:     bool = cli.Option(False,       help = 'Reload server on code changes', hidden = True),
        ):
    '''Blazing fast self-hosted object storage for the 21st century'''

    api: api.Api = api.Api \
    (
        anonymous = auth is None,
        path      = None if virtual else str(dir),
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
        host   = host,
        port   = port,
    )
