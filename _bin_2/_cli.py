from .api import Api
import typer
from . import __name__, __version__
import inspect
import functools
from rich.console import Console
from rich.table import Table
import rich
from rich.pretty import pprint as pp

class Cli(typer.Typer):
    def __init__(self, *args, version: str = None, **kwargs):
        super().__init__(*args, **kwargs)

        self.info.version = version

        self.console = Console()

    def print_help(self):
        # padding and coluours should be attributes
        
        padding = 2

        def t(name: str, columns: int = 0):
            table = Table(box = None, show_header = False, title=name.upper(), padding=(0, 0, 0, padding), title_justify='left', title_style='bold')

            for _ in range(columns):
                table.add_column()

            return table

        def row(table, switch: str, input_type, description: str, default):
            type_colours = \
            {
                str:        'bright_green',
                int:        'bright_cyan',
                bool:       'bright_blue',
                type(None): 'yellow',
            }

            type_colour = type_colours.get(input_type)
            default_type_colour = type_colours.get(type(default))

            if input_type is Ellipsis:
                data_type = ''
            else:
                data_type = f'[{type_colour}]<{input_type.__name__}>[/{type_colour}]'

            if default is Ellipsis:
                data_default = ''
            else:
                data_default = f'[dim i]Default: [{default_type_colour}]{default!r}[/{default_type_colour}][/dim i]'

            table.add_row \
            (
                f'[cyan]{switch}[/cyan]',
                data_type,
                description,
                data_default,
            )

        command = self.registered_commands[0]

        main   = command.callback
        description = main.__doc__

        signature = inspect.signature(main)

        table_arguments      = t('arguments', 4)
        table_options        = t('options', 4)
        table_global_options = t('global options', 4)

        for parameter in signature.parameters.values():
            parameter_annotation = parameter.annotation
            parameter_default    = parameter.default
            parameter_name       = parameter.name

            if parameter_name in ('help', 'version'): continue

            if parameter.POSITIONAL_ONLY:
                parameter_default = typer.Argument(...)
            elif (parameter.KEYWORD_ONLY or parameter.POSITIONAL_OR_KEYWORD) \
                    and not isinstance(parameter_default, (typer.models.OptionInfo, typer.models.ArgumentInfo)):
                parameter_default = typer.Option(parameter_default)

            if isinstance(parameter_default, typer.models.ArgumentInfo):
                row(table_arguments, parameter_name, parameter_annotation, parameter_default.help, parameter_default.default)
            elif isinstance(parameter_default, typer.models.OptionInfo):
                row(table_options, f'--{parameter_name}', parameter_annotation, parameter_default.help, parameter_default.default)
            else:
                raise Exception()

        row(table_global_options, '--help',    ..., 'Display the help manual', ...)
        row(table_global_options, '--version', ..., 'Shows the version of the project', ...)

        typer.secho(self.info.name.title(), bold = True, nl = False)

        if self.info.name is not None:
            typer.secho(' version ', nl = False)
            typer.secho(self.info.version, fg = 'cyan', nl = False)

        typer.secho()
        typer.secho()

        tables = \
        (
            table_arguments,
            table_options,
            table_global_options,
        )

        min_widths = [0, 0, 0, 0]

        for table in tables:
            col_widths = table._calculate_column_widths(self.console, self.console.width)

            for index, min_width in enumerate(min_widths):
                min_widths[index] = max(min_width, col_widths[index] - padding)

        for table in tables:
            for index, min_width in enumerate(min_widths):
                table.columns[index].min_width = min_width

            self.console.print(table)
            rich.print()

    def print_version(self):
        print(self.info.version)

    def command(self, *args, **kwargs):
        decorator = super().command(*args, **kwargs)

        def patch(func):
            @functools.wraps(func)
            def wrapper(*args, help: bool = False, version: bool = False, **kwargs):
                if help:
                    self.print_help()
                elif version:
                    self.print_version()
                else:
                    return func(*args, **kwargs)

            wrapper.__signature__ = inspect.Signature \
            (
                parameters = \
                [
                    *inspect.signature(func).parameters.values(),
                    inspect.Parameter \
                    (
                        name       = 'help',
                        kind       = inspect.Parameter.KEYWORD_ONLY,
                        annotation = bool,
                        default    = False,
                    ),
                    inspect.Parameter \
                    (
                        name       = 'version',
                        kind       = inspect.Parameter.KEYWORD_ONLY,
                        annotation = bool,
                        default    = False,
                    ),
                ],
            )

            return decorator(wrapper)

        return patch

class BuckCli(Cli):
    def __init__(self):
        super().__init__ \
        (
            name    = __name__,
            version = __version__,
        )

    def print_help(self):
        super().print_help()

        padding = 2

        def t(name: str, columns: int = 0):
            table = Table(box = None, show_header = False, title=name.upper(), padding=(0, 0, 0, padding), title_justify='left', title_style='bold')

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

cli = BuckCli()

@cli.command()
def main \
        (
            dir:     str  = typer.Argument('.',       help = 'Bucket dir'),
            port:    int  = typer.Option(8000,        help = 'Port to bind server to'),
            host:    str  = typer.Option('127.0.0.1', help = 'Host to bind server to'),
            auth:    str  = typer.Option(None,        help = 'Client auth key(s)'),
            virtual: bool = typer.Option(False,       help = 'Whether to use in-memory filesystem'),
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
