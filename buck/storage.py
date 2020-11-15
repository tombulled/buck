import pathlib
import datetime
import shutil
import dulwich.errors
import dulwich.porcelain
import magic

class Object(object):
    def __init__(self, path):
        path = pathlib.Path(str(path)).absolute()

        self.path = path

    def __str__(self):
        return '<{class_name}({path})>'.format \
        (
            class_name = self.__class__.__name__,
            path = repr(str(self.path)),
        )

    def __repr__(self):
        return self.__str__()

    def _as_dict(self):
        data = \
        {
            'name': self.name,
            'creation_date': self.creation_date,
            'mime_type': self.mime_type,
        }

        return data

    def _touch(self):
        if self._exists(): return

        self.path.parent.mkdir \
        (
            parents = True,
            exist_ok = True,
        )

        with open(self.path, 'w') as file:
            pass

    def _exists(self):
        return self.path.exists()

    @property
    def name(self):
        return self.path.name

    @property
    def creation_date(self):
        return datetime.datetime.fromtimestamp(self.path.lstat().st_ctime)

    @property
    def mime_type(self):
        return magic.from_file(str(self.path), mime = True)

class Bucket(object):
    def __init__(self, path):
        path = pathlib.Path(str(path)).absolute()

        self.path = path

    def __str__(self):
        return '<{class_name}({path})>'.format \
        (
            class_name = self.__class__.__name__,
            path = repr(str(self.path)),
        )

    def __repr__(self):
        return self.__str__()

    def _as_dict(self):
        data = \
        {
            'name': self.name,
            'creation_date': self.creation_date,
        }

        return data

    def _touch(self):
        if self._exists(): return

        self.path.mkdir \
        (
            parents = True,
            exist_ok = True,
        )

    def _exists(self):
        return self.path.exists()

    @property
    def name(self):
        return self.path.name

    @property
    def creation_date(self):
        return datetime.datetime.fromtimestamp(self.path.lstat().st_ctime)

    def put_object(self, path, data):
        path = self.path.joinpath(path)

        object = Object(path)

        if object._exists(): return

        object._touch()

        with object.path.open('wb') as file:
            file.write(data)

        return object

    def get_object(self, path):
        path = self.path.joinpath(path)

        object = Object(path)

        return object

class VersionedBucket(Bucket):
    def _touch(self):
        super()._touch()

        dulwich.porcelain.init(self.path)

class Storage(object):
    def __init__(self, path):
        path = pathlib.Path(str(path)).absolute()

        path.mkdir \
        (
            parents = True,
            exist_ok = True,
        )

        self.path = path

    def __str__(self):
        return '<{class_name}({path})>'.format \
        (
            class_name = self.__class__.__name__,
            path = repr(str(self.path)),
        )

    def __repr__(self):
        return self.__str__()

    @staticmethod
    def _to_bucket(path):
        return Bucket(path)

    def _create_bucket(self, name, bucket_type):
        path = self.path.joinpath(name)

        bucket = bucket_type(path)

        if bucket._exists(): return

        bucket._touch()

        return bucket

    def get_bucket(self, name):
        path = self.path.joinpath(name)

        bucket = self._to_bucket(path)

        if bucket._exists(): return bucket

    def list_buckets(self):
        children = list(self.path.glob('*/'))

        buckets = []

        for child in children:
            if not child.is_dir():
                continue

            bucket = self._to_bucket(child)

            buckets.append(bucket)

        return buckets

    def create_bucket(self, name):
        return self._create_bucket(name, Bucket)

    def delete_bucket(self, name):
        path = self.path.joinpath(name)

        bucket = self._to_bucket(path)

        if not bucket._exists(): return False

        shutil.rmtree(str(path))

        return not bucket._exists()

    def head_bucket(self, name):
        path = self.path.joinpath(name)

        bucket = self._to_bucket(path)

        return bucket._exists()

class VersionedStorage(Storage):
    @staticmethod
    def _is_repo(path):
        try:
            repo = dulwich.porcelain.Repo(str(path))

            return True
        except dulwich.errors.NotGitRepository:
            return False

    @classmethod
    def _to_bucket(cls, path):
        if cls._is_repo(path):
            return VersionedBucket(path)

        return Bucket(path)

    def create_bucket(self, name):
        return self._create_bucket(name, VersionedBucket)
