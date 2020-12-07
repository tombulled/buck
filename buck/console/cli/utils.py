from . import exceptions
import click.exceptions

def patch_click_exceptions():
    patched_exceptions = \
    (
        exceptions.BadOptionUsage,
        exceptions.NoSuchOption,
        exceptions.MissingParameter,
        exceptions.BadParameter,
        exceptions.UsageError,
    )

    for patched_exception in patched_exceptions:
        click_exception = getattr(click.exceptions, patched_exception.__name__)

        setattr(click_exception, 'show', getattr(patched_exception, 'show'))
