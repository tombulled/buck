from . import model
from . import user
from . import stack

from typing import Union

class StackSession(model.Model):
    stack: stack.Stack
    user:  Union[user.StackUser, None]

    def __repr__(self):
        return super().__repr__ \
        (
            stack = self.stack.name,
            user  = self.user and self.user.name,
        )

    def service(self, name, **kwargs):
        service_class = self.stack.get_service(name)

        return service_class \
        (
            name    = name,
            session = self,
            **kwargs,
        )
