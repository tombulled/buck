from .cli import Cli, Argument, Option
from ..api import Api, api
from .. import __name__, __version__
from pathlib import Path


def cli(port: int = 8000, host: str = "127.0.0.1", path: str = "."):
    app: Cli = Cli(
        name=__name__,
        version=__version__,
    )

    @app.example("/mnt/data", auth="access_key:secret_key")
    @app.example(virtual=True, auth="admin")
    @app.example(host="0.0.0.0", port=8080)
    @app.example("/tmp/store")
    @app.command()
    def main(
        dir: Path = Argument(
            path,
            help="Bucket storage directory",
            exists=True,
            file_okay=False,
            dir_okay=True,
            writable=True,
            readable=True,
            resolve_path=True,
        ),
        port: int = Option(port, help="Port to bind server to"),
        host: str = Option(host, help="Host to bind server to"),
        auth: str = Option(None, help="Client auth key(s)"),
        virtual: bool = Option(False, help="Whether to use in-memory mode"),
        dev: bool = Option(False, help="Reload server on code changes", hidden=True),
    ):
        """Blazing fast self-hosted object storage for the 21st century"""

        user_auth = []

        if auth is not None:
            chunks = auth.split(":")

            if len(chunks) == 1:
                access_key = chunks[0]
                secret_key = chunks[0]
            else:
                access_key, secret_key, *_ = chunks

            user_auth.append((access_key, secret_key))

        api_app = api(
            path=str(dir),
            auth=user_auth,
        )

        api_app.serve(
            host=host,
            port=port,
        )

    return app
