from . import utils
from . import exceptions

import typer
import typer.main
import click.core
import inspect
import rich.console
import rich.table
import functools
import rich
import rich.style
import pathlib
import builtins

utils.patch_click_exceptions()

class Cli(typer.Typer):
    padding = 2
    colour  = 'cyan'

    def __init__(self, *args, version: str = None, **kwargs):
        super().__init__(*args, **kwargs)

        self.info.version = version

        self.console = rich.console.Console()

    def __repr__(self):
        class_name = utils.render(self.__class__.__name__, self.colour)
        name       = utils.render(repr(self.info.name),    utils.get_colour(str))
        version    = utils.render(self.info.version,       utils.get_colour(int))

        return f'<{class_name}: name={name} version={version}>'

    def print_help(self):
        create_table = lambda name: rich.table.Table \
        (
            box           = None,
            show_header   = False,
            title         = name.upper(),
            padding       = (0, 0, 0, self.padding),
            title_justify = 'left',
            title_style   = 'bold',
        )

        add_row = lambda table, name, type, description, default: table.add_row \
        (
            '[{style}]{data}[/{style}]'.format \
            (
                style = self.colour,
                data  = name,
            ),
            '[{style}]<{data}>[/{style}]'.format \
            (
                style = utils.get_colour(type),
                data  = type.__name__,
            ) if type is not Ellipsis else '',
            description,
            '[dim i]Default: [{style}]{data!r}[/{style}][/dim i]'.format \
            (
                style = utils.get_colour(builtins.type(default)),
                data  = default,
            ) if default is not Ellipsis else '',
        )

        create_option = lambda name, help: click.core.Option \
        (
            param_decls = [f'--{name}'],
            is_flag     = True,
            help        = help,
            hidden      = True,
        )

        global_options = \
        (
            create_option('help',    'Display the program help manual'),
            create_option('version', 'Display the program version'),
        )

        table_names = \
        (
            'arguments',
            'options',
            'global options',
        )

        column_names = \
        (
            'name',
            'type',
            'description',
            'default',
        )

        command_info = self.registered_commands[0]
        command      = typer.main.get_command_from_info(command_info)

        command_examples = command_info.examples

        command_examples.append(((), {global_options[0].name: True}))

        tables = {}

        for table_name in table_names:
            table = create_table(table_name)

            for column_name in column_names:
                table.add_column(header = column_name)

            tables[table_name] = table

        for param in command.params:
            if param.hidden \
                    or param.name in [option.name for option in global_options]:
                continue

            if param.param_type_name == 'option':
                param_name = f'--{param.name}'

            add_row \
            (
                tables[f'{param.param_type_name}s'],
                f'--{param.name}',
                command.callback.__annotations__[param.name],
                param.help,
                param.default,
            )

        for global_option in global_options:
            add_row \
            (
                tables['global options'],
                f'--{global_option.name}',
                ...,
                global_option.help,
                ...,
            )

        typer.secho(self.info.name.title(), bold = True, nl = False)

        if self.info.name is not None:
            typer.secho(' version ', nl = False)
            typer.secho(self.info.version, fg = self.colour, nl = False)

        print('\n')

        if command.help:
            print(' ' * self.padding + command.help, end='\n\n')

        tables = \
        (
            tables['arguments'],
            tables['options'],
            tables['global options'],
        )

        min_widths = [0 for _ in range(len(column_names))]

        for table in tables:
            col_widths = table._calculate_column_widths(self.console, self.console.width)

            for index, min_width in enumerate(min_widths):
                min_widths[index] = max(min_width, col_widths[index] - self.padding)

        for table in tables:
            for index, min_width in enumerate(min_widths):
                table.columns[index].min_width = min_width

            self.console.print(table)
            print()

        table = create_table('examples')

        table.add_column('example')

        def example(*arguments, **options):
            data = ''

            for argument in arguments:
                argument_colour = utils.get_colour(type(argument))

                if isinstance(argument, str) and ' ' in argument:
                    argument = repr(argument)

                data += f'[{argument_colour}]{argument!s}[/{argument_colour}] '

            for option_key, option_val in options.items():
                option_colour = utils.get_colour(type(option_val))

                if isinstance(option_val, str) and ' ' in option_val:
                    option_val = repr(option_val)

                data += f'[{self.colour}]--{option_key}[/{self.colour}]'

                if not isinstance(option_val, bool):
                    data += f' [{option_colour}]{option_val!s}[/{option_colour}]'

                data += ' '

            table.add_row \
            (
                f'[blue]$[/blue] [i]{self.info.name} {data}[/i]',
            )

        for arguments, options in command_examples:
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

            create_parameter = lambda name: inspect.Parameter \
            (
                name       = name,
                kind       = inspect.Parameter.KEYWORD_ONLY,
                annotation = bool,
                default    = False,
            )

            wrapper.__signature__ = inspect.Signature \
            (
                parameters = \
                [
                    *inspect.signature(func).parameters.values(),
                    create_parameter('help'),
                    create_parameter('version'),
                ],
            )

            return decorator(wrapper)

        return patch
