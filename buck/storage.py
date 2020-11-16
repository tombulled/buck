import pathlib
import datetime
import shutil
import magic
import os

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
            'last_modified': self.last_modified_date,
            'size': self.size,
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
    def last_modified_date(self):
        return datetime.datetime.fromtimestamp(self.path.lstat().st_mtime)

    @property
    def size(self):
        return self.path.lstat().st_size

    @property
    def mime_type(self):
        return magic.from_file(str(self.path), mime = True)

    def delete(self):
        if not self._exists(): return True

        self.path.unlink()

        return True

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

    def list_objects(self, *, prefix=''):
        if prefix:
            tree = self.path.joinpath(prefix)
        else:
            tree = self.path

        if not tree.is_dir():
            return [] # Error

        for path, dirs, files in os.walk(tree):
            path = pathlib.Path(path)

            print(path, dirs, files)

            for file in files:
                file_path = path.joinpath(file)
                
                object = Object(file_path)

                yield object

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
