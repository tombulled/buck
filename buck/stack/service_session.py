from . import model
from . import stack
from . import service
from . import user

import dataclasses
from typing import Optional

@dataclasses.dataclass
class StackServiceSession:
    service: service.StackService
    stack: stack.Stack
    user: Optional[user.StackUser]
