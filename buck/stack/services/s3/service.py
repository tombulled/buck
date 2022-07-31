from fs.base import FS
import fs

from .service_session import SimpleStorageServiceSession

from ... import service


class SimpleStorageService(service.StackService):
    fs: FS

    def __init__(self, path: str = None):
        super().__init__(
            name="s3",
            session=SimpleStorageServiceSession,
            fs=fs.open_fs(path or "mem://"),
        )
