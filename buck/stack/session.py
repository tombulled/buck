from . import model
# from .user import StackUser
from . import user
# from .stack import Stack
from . import stack

class StackSession(model.Model):
    stack: stack.Stack
    user: user.StackUser

    def __repr__(self):
        return super().__repr__ \
        (
            stack = self.stack.name,
            user  = self.user.name,
        )

    def service(self, name, **kwargs):
        service_class = self.stack.get_service(name)

        return service_class \
        (
            name    = name,
            session = self,
            **kwargs,
        )
