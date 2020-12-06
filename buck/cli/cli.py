import rich.table
import typer
from .base import BaseCli
from .. import __name__, __version__
from ..api import Api

class Cli(BaseCli):
    def __init__(self):
        super().__init__ \
        (
            name    = __name__,
            version = __version__,
        )

        @self.command()
        def main \
                (
                    dir:     str  = typer.Argument('.',       help = 'Bucket storage directory'),
                    port:    int  = typer.Option(8000,        help = 'Port to bind server to'),
                    host:    str  = typer.Option('127.0.0.1', help = 'Host to bind server to'),
                    auth:    str  = typer.Option(None,        help = 'Client auth key(s)'),
                    virtual: bool = typer.Option(False,       help = 'Whether to use in-memory mode'),
                ):
            '''Blazing fast self-hosted object storage for the 21st century'''

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

    def print_help(self):
        super().print_help()

        padding = 2

        def t(name: str, columns: int = 0):
            table = rich.table.Table(box = None, show_header = False, title=name.upper(), padding=(0, 0, 0, padding), title_justify='left', title_style='bold')

            for _ in range(columns):
                table.add_column()

            return table

        table = t('examples', 1)

        def example(*arguments, **options):
            type_colours = \
            {
                str:        'bright_green',
                int:        'bright_cyan',
                bool:       'bright_blue',
                type(None): 'yellow',
            }

            data = ''

            for argument in arguments:
                argument_colour = type_colours.get(type(argument))

                if isinstance(argument, str) and ' ' in argument:
                    argument = repr(argument)

                data += f'[{argument_colour}]{argument!s}[/{argument_colour}] '

            for option_key, option_val in options.items():
                option_colour = type_colours.get(type(option_val))

                if isinstance(option_val, str) and ' ' in option_val:
                    option_val = repr(option_val)

                data += f'[cyan]--{option_key}[/cyan]'

                if not isinstance(option_val, bool):
                    data += f' [{option_colour}]{option_val!s}[/{option_colour}]'

                data += ' '

            table.add_row \
            (
                f'[blue]$[/blue] [i]{self.info.name} {data}[/i]',
            )

        example('/tmp/store')
        example(host = '0.0.0.0', port = 8080)
        example(virtual = True, auth = 'admin')
        example(help = True)

        self.console.print(table)

        print()
