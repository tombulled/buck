from . import base

import fs

class SimpleStorageService(base.BaseSimpleStorageService):
    def __init__(self, *, name, session):
        super().__init__ \
        (
            name    = name,
            session = session,
            fs      = fs.open_fs('mem://'),
        )
