from . import utils
from . import exceptions

import typer
import inspect
import rich.console
import rich.table
import functools
import rich
import rich.style
from pathlib import Path

utils.patch_click_exceptions()

class Cli(typer.Typer):
    def __init__(self, *args, version: str = None, **kwargs):
        super().__init__(*args, **kwargs)

        self.info.version = version

        self.console = rich.console.Console()

    def __repr__(self):
        render = lambda string, color: rich.style.Style(color=color).render(string)

        return '<{class_name}: name={name}, version={version}>'.format \
        (
            class_name = render(self.__class__.__name__, 'cyan'),
            name = render(repr(self.info.name), 'bright_green'),
            version = render(self.info.version, 'bright_blue'),
        )

    def print_help(self):
        # padding and colours should be attributes

        padding = 2

        def t(name: str, columns: int = 0):
            table = rich.table.Table(box = None, show_header = False, title=name.upper(), padding=(0, 0, 0, padding), title_justify='left', title_style='bold')

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
                Path:       'bright_magenta',
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

        examples = command.examples
        main   = command.callback
        description = main.__doc__

        examples.append(((), {'help': True}))

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

            if parameter_default.hidden: continue # cool

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

        print('\n')

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
            print()

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

        for arguments, options in examples:
            example(*arguments, **options)

        self.console.print(table)

        print()

    def print_version(self):
        print(self.info.version)

    def example(self, *arguments, **options):
        def wrapper(func):
            registered_command = self.registered_commands[-1]

            registered_command.examples = getattr(registered_command, 'examples', [])

            registered_command.examples.append((arguments, options))

            return func

        return wrapper

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
