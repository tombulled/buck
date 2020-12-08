from . import router
from . import middleware
from .. import stack
from ..stack import services

import fastapi
import functools
import uvicorn

class Api(fastapi.FastAPI):
    def __init__(self, *, anonymous: bool = False, path: str = None):
        super().__init__()

        self.stack = stack.Stack \
        (
            name             = 'buck',
            anonymous_access = anonymous,
        )

        self.stack.add_service(services.SimpleStorageService(path))

        self.include_router(router.router)

        self.add_middleware \
        (
            middleware.AwsAuthenticationMiddleware,
            stack = self.stack,
        )

        self.add_middleware(middleware.AwsExceptionHandlerMiddleware)

    def __repr__(self):
        return f'<{self.__class__.__name__}: stack={self.stack.name!r}>'

    def add_user(self, *, name: str = None, access_key: str = None, secret_key: str = None):
        return self.stack.add_user \
        (
            name       = name,
            access_key = access_key,
            secret_key = secret_key,
        )

    def serve(self, host: str = '127.0.0.1', port: int = 8000, **kwargs):
        uvicorn.run \
        (
            app       = self,
            host      = host,
            port      = port,
            log_level = 'info',
            **kwargs,
        )
