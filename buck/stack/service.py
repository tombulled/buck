import dataclasses

@dataclasses.dataclass
class StackService:
    name: str
    session: type

    def create_session(self, *, stack, user):
        return self.session \
        (
            stack   = stack,
            service = self,
            user    = user,
        )
