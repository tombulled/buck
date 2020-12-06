from buck.cli import cli
from typing import Union, Callable, List, Any
from typer import Typer
from typer.models import OptionInfo, ArgumentInfo
import typer
import typer.models
import inspect
from pydantic import BaseModel
from rich.console import Console
from rich.style import Style
from rich.table import Table
import buck

import rich
import io

# dev
from rich.pretty import pprint as pp

# Test
# from inspect import Signature, Parameter
# # ref: https://smarie.github.io/python-makefun/
# parameters = [Parameter('b', kind=Parameter.POSITIONAL_OR_KEYWORD),
#               Parameter('a', kind=Parameter.POSITIONAL_OR_KEYWORD, default=0), ]
# func_sig = Signature(parameters)
# func_name = 'foo'
#
# def bar():
#     pass
#
# bar.__signature__ = func_sig
#
# print(bar)
# rich.inspect(bar)

class ArgumentSchema(BaseModel):
    name:    str
    type:    type
    help:    Union[str, None]
    default: Union[Any, None]
    hidden:  bool

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, *, name: str, type: type, info: ArgumentInfo):
        super().__init__ \
        (
            name    = name,
            type    = type,
            help    = info.help,
            default = info.default,
            hidden  = info.hidden,
        )

class OptionSchema(BaseModel):
    name:    str
    type:    type
    help:    Union[str, None]
    default: Union[Any, None]
    hidden:  bool

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, *, name: str, type: type, info: OptionInfo):
        super().__init__ \
        (
            name    = name,
            type    = type,
            help    = info.help,
            default = info.default,
            hidden  = info.hidden,
        )

class TyperSchema(BaseModel):
    arguments: List[ArgumentSchema]
    options:   List[OptionSchema]

    def __init__(self, cli: Callable):
        signature = self.inspect_callable(cli)

        super().__init__(**signature)

    @staticmethod
    def inspect_callable(callable: Callable):
        signature = inspect.signature(callable)

        arguments = []
        options   = []

        for parameter in signature.parameters.values():
            parameter_annotation = parameter.annotation
            parameter_default    = parameter.default
            parameter_name       = parameter.name

            if parameter.POSITIONAL_ONLY:
                parameter_default = typer.Argument(...)
            elif (parameter.KEYWORD_ONLY or parameter.POSITIONAL_OR_KEYWORD) \
                    and not isinstance(parameter_default, (typer.models.OptionInfo, typer.models.ArgumentInfo)):
                parameter_default = typer.Option(parameter_default)

            if isinstance(parameter_default, typer.models.ArgumentInfo):
                parameter_schema = ArgumentSchema \
                (
                    name = parameter_name,
                    type = parameter_annotation,
                    info = parameter_default,
                )

                arguments.append(parameter_schema)
            elif isinstance(parameter_default, typer.models.OptionInfo):
                parameter_schema = OptionSchema \
                (
                    name = parameter_name,
                    type = parameter_annotation,
                    info = parameter_default,
                )

                options.append(parameter_schema)
            else:
                raise Exception()

        return \
        {
            'arguments': arguments,
            'options':   options,
        }

class TyperHelp(object):
    name: str
    schema: TyperSchema
    description: str

    def __init__(self, main: Callable, name: str, version: str = None, primary_colour: str = 'cyan', secondary_colour: str = 'green', padding: int = 2): # change, shouldn't be red
        self.name = name
        self.version = version
        self.description = main.__doc__.strip() # needs more than just .strip

        self.padding = padding

        self.primary_colour   = primary_colour
        self.secondary_colour = secondary_colour

        schema = TyperSchema(main)

        self.schema = schema

        self.console = Console()

    def __repr__(self):
        return f'<{self.__class__.__name__}: name={self.name!r} version={self.version!r}>'

    def print(self):
        arguments = self.schema.arguments
        options = self.schema.options

        r = lambda *args, **kwargs: typer.secho(*args, nl=False, **kwargs)
        br = lambda: r('\n')

        def t(name: str, columns: int = 0):
            table = Table(box = None, show_header = False, title=name.upper(), padding=(0, 0, 0, self.padding), title_justify='left', title_style='bold')

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
                f'[cyan]--{switch}[/cyan]',
                data_type,
                description,
                data_default,
            )

        r(self.name.title(), bold = True)

        if self.version:
            r(' version ')
            r(self.version, fg = self.primary_colour)

        br()
        br()

        if self.description:
            r(' ' * self.padding) # ??
            r(self.description)
            br()
            br()

        r('USAGE', bold = True)
        br()
        r(' ' * self.padding)
        r(self.name, underline = True)
        r(' [OPTIONS] [ARGUMENTS]')
        br()
        br()

        min_widths = [0, 0, 0, 0]
        console = self.console

        table_arguments = t('arguments', len(min_widths))

        for argument in arguments:
            row(table_arguments, argument.name, argument.type, argument.help, argument.default)

        table_options = t('options', len(min_widths))

        for option in options:
            row(table_options, option.name, option.type, option.help, option.default)

        table_global_options = t('global options', len(min_widths))

        row(table_global_options, 'help',    ..., 'Display the help manual', ...)
        row(table_global_options, 'version', ..., 'Shows the version of the project', ...)

        table_examples = t('examples', 1)

        table_examples.add_row('[blue]$[/blue] [i]buck [cyan]--memory[/cyan] [cyan]--port[/cyan] [bright_cyan]8080[/bright_cyan][/i]')
        table_examples.add_row('[blue]$[/blue] [i]buck [bright_green]/tmp/foo[/bright_green][/i]')
        table_examples.add_row('[blue]$[/blue] [i]buck [cyan]--help[/cyan][/i]')

        tables = \
        (
            table_arguments,
            table_options,
            table_global_options,
        )

        for table in tables:
            col_widths = table._calculate_column_widths(console, console.width)

            for index, min_width in enumerate(min_widths):
                min_widths[index] = max(min_width, col_widths[index] - self.padding)

        for table in tables:
            for index, min_width in enumerate(min_widths):
                table.columns[index].min_width = min_width

            console.print(table)
            rich.print()

        console.print(table_examples)
        rich.print()

# cli.print_help = lambda: TyperHelp(cli.registered_commands[0].callback, cli.info.name, cli.info.version).print()

cli()
