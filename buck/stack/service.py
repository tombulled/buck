from . import model
from .session import StackSession

class StackService(model.Model):
    name: str
    session: StackSession

    def __repr__(self):
        return super().__repr__ \
        (
            name  = self.name,
            stack = self.session.stack.name,
        )
