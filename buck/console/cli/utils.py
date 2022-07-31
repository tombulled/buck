from . import exceptions
import click.exceptions
import rich.style
import pathlib
import click.types


def patch_click_exceptions():
    patched_exceptions = (
        exceptions.BadOptionUsage,
        exceptions.NoSuchOption,
        exceptions.MissingParameter,
        exceptions.BadParameter,
        exceptions.UsageError,
    )

    for patched_exception in patched_exceptions:
        click_exception = getattr(click.exceptions, patched_exception.__name__)

        setattr(click_exception, "show", getattr(patched_exception, "show"))


def render(string: str, colour: str):
    style = rich.style.Style(color=colour)

    return style.render(string)


def get_colour(typ, default=str):
    type_colours = {
        str: "bright_green",
        int: "bright_cyan",
        bool: "bright_blue",
        pathlib.Path: "bright_magenta",
        type(None): "yellow",
        click.types.Path: "bright_magenta",
        click.types.IntParamType: "bright_cyan",
        click.types.StringParamType: "bright_green",
        click.types.BoolParamType: "bright_blue",
    }

    return type_colours.get(typ if typ in type_colours else default)
