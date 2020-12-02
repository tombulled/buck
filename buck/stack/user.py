from .model import Model

class StackUser(Model):
    access_key: str
    secret_key: str
    name: str
    id: str

    def __repr__(self):
        return super().__repr__ \
        (
            name = self.name,
        )
