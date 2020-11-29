from . import memory
from . import entities
from . import validation

from .. import stack
from .. import exceptions

import datetime
import pathlib
import shutil

# util
def is_dir_empty(path):
    path = pathlib.Path(str(path)).absolute()

    for _ in path.glob('*'):
        return False

    return True

class SimpleStorageService(stack.StackService):
    def __init__(self, name, session, *, path):
        super().__init__(name, session)

        self.path = pathlib.Path(str(path)).absolute()
        self.region = entities.Region('us-east-2')

    def list_buckets(self):
        children = list(self.path.glob('*/'))

        for child in children:
            if child.is_dir():
                yield self.get_bucket(child.name)

    def get_bucket(self, name):
        validation.validate_bucket_name(name)

        self.head_bucket(name)

        path = self.path.joinpath(name)

        bucket = entities.Bucket \
        (
            name = name,
            region = self.region,
            creation_date = datetime.datetime.fromtimestamp(path.lstat().st_ctime),
        )

        return bucket

    def create_bucket(self, name):
        validation.validate_bucket_name(name)

        path = self.path.joinpath(name)

        if path.is_dir():
            raise exceptions.S3Error('BucketAlreadyExists')

        path.mkdir(parents = True)

    def delete_bucket(self, name):
        validation.validate_bucket_name(name)

        path = self.path.joinpath(name)

        if path.is_dir():
            shutil.rmtree(path)

    def head_bucket(self, name, **kwargs):
        validation.validate_bucket_name(name)

        path = self.path.joinpath(name)

        if not path.is_dir():
            raise exceptions.S3Error('NoSuchBucket')

    def put_object(self, bucket_name, object_key, object_data):
        validation.validate_bucket_name(bucket_name)
        validation.validate_object_key(object_key)

        bucket = self.get_bucket(bucket_name)

        # Create object to validate key
        object = entities.Object \
        (
            key = object_key,
            bucket = bucket,
            last_modified_date = datetime.datetime.now(),
        )

        path = self.path.joinpath(bucket_name, object_key)

        if path.is_dir():
            raise exceptions.S3Error('InvalidRequest')

        path.parent.mkdir \
        (
            parents  = True,
            exist_ok = True,
        )

        with open(path, 'wb') as file:
            file.write(object_data)

    def get_object(self, bucket_name, object_key):
        validation.validate_bucket_name(bucket_name)
        validation.validate_object_key(object_key)

        self.head_object(bucket_name, object_key)

        path = self.path.joinpath(bucket_name, object_key)

        return open(path, 'rb')

    def list_objects(self, bucket_name):
        validation.validate_bucket_name(bucket_name)

        bucket = self.get_bucket(bucket_name)

        tree = self.path

        # TODO: Check `tree` exists (and is_dir)

        for path, dirs, files in os.walk(tree):
            path = pathlib.Path(path)

            for file in files:
                file_path = path.joinpath(file)

                object = Object(file_path, bucket)

                yield object

    def delete_object(self, bucket_name, object_key):
        validation.validate_bucket_name(bucket_name)
        validation.validate_object_key(object_key)

        self.head_bucket(bucket_name)

        path = self.path.joinpath(bucket_name, object_key)

        if not path.is_file():
            return

        path.unlink()

        for parent in path.parents:
            if parent == self.path:
                break

            if not is_dir_empty(parent):
                break

            parent.rmdir()

    def head_object(self, bucket_name, object_key):
        validation.validate_bucket_name(bucket_name)
        validation.validate_object_key(object_key)

        self.head_bucket(bucket_name)

        path = self.path.joinpath(bucket_name, object_key)

        if path.is_dir():
            raise exceptions.S3Error('InvalidRequest')

        if not path.is_file():
            raise exceptions.S3Error('NoSuchKey')
