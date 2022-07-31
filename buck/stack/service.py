from . import model

class StackService(model.Model):
    name: str
    session: type

    def __repr__(self):
        return super().__repr__ \
        (
            name  = self.name,
        )

    def create_session(self, *, stack, user):
        return self.session \
        (
            stack   = stack,
            service = self,
            user    = user,
        )
