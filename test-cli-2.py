import typer
import inspect
import rich

def main1(name: str, _help: str = 'hey'):
    print('hello', name)

signature1 = inspect.signature(main1)

params = list(signature1.parameters.values())

signature2 = inspect.Signature \
(
    parameters = \
    [
        *params,
        inspect.Parameter('hello', kind=inspect.Parameter.POSITIONAL_OR_KEYWORD, default=0),
    ],
)

def main2(*args, **kwargs):
    print('main2', args, kwargs)

main2.__signature__ = signature2

# typer.run(main1)
typer.run(main2)
