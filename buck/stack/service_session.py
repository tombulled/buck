from . import model
from . import stack
from . import service
from . import user

from typing import Optional


class StackServiceSession(model.Model):
    service: service.StackService
    stack: stack.Stack
    user: Optional[user.StackUser]

    def __repr__(self):
        return super().__repr__(
            stack=self.stack.name,
            service=self.service.name,
            user=self.user and self.user.name,
        )
