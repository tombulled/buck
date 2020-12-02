import pydantic

class BaseModel(pydantic.BaseModel):
    class Config:
        allow_mutation = False
        arbitrary_types_allowed: bool = True

    def __repr__(self, **fields):
        if not fields:
            fields = self.dict()

        class_name = self.__class__.__name__

        if not fields: return f'<{class_name} />'

        attributes = ' '.join \
        (
            f'{key}={val!r}'
            for key, val in fields.items()
        )

        return f'<{class_name}: {attributes}>'

    def __str__(self):
        return self.__repr__()
