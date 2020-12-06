import click.exceptions
import sys
import typer

class NoSuchOption(click.exceptions.NoSuchOption):
    def show(self, file = None):
        echo = lambda *args, **kwargs: typer.secho \
        (
            *args,
            nl = False,
            file = file or sys.stderr,
            **kwargs,
        )

        echo('ERROR ', fg='bright_red')
        echo(f'[{self.__class__.__name__}] ', fg='bright_blue')

        echo('No such option: ')
        echo(self.option_name, fg='cyan')

        if self.possibilities:
            echo(' (Did you mean ')
            echo(self.possibilities[0], fg='cyan')
            echo('?)')

        echo('\n')

class MissingParameter(click.exceptions.MissingParameter):
    def show(self, file = None):
        echo = lambda *args, **kwargs: typer.secho \
        (
            *args,
            nl = False,
            file = file or sys.stderr,
            **kwargs,
        )

        echo(f'Missing {self.param.param_type_name}: ')
        echo(self.param.name, fg='cyan')
        echo('\n')

class BadParameter(click.exceptions.BadParameter):
    def show(self, file = None):
        echo = lambda *args, **kwargs: typer.secho \
        (
            *args,
            nl = False,
            file = file or sys.stderr,
            **kwargs,
        )

        echo('Invalid value for: ')
        echo(self.param.opts[0], fg='cyan')

        echo(' (couldn\'t cast to ')
        echo(self.param.type.name.title(), fg='bright_cyan')
        echo(')\n')

class UsageError(click.exceptions.UsageError):
    def show(self, file = None):
        typer.secho(self.format_message(), file = file or sys.stderr)
