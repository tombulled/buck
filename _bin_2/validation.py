import pydantic

class Config:
    arbitrary_types_allowed: bool = True

def validate_arguments(func):
    return pydantic.validate_arguments \
    (
        func   = func,
        config = Config,
    )
