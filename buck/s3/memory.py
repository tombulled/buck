from .. import stack
from . import entities
from .. import exceptions

import io

b = entities.Bucket('some-bucket')
o = entities.Object('a/b', b)

class SimpleStorageService(stack.StackService):
    _storage = \
    {
        b.name: \
        {
            'bucket': b,
            'objects': \
            {
                o.key: \
                {
                    'object': o,
                    'data': b'Hello World',
                },
            },
        }
    }

    def list_buckets(self):
        for bucket in self._storage.values():
            yield bucket['bucket']

    def get_bucket(self, name):
        self.head_bucket(name)

        return self._storage[name]['bucket']

    def create_bucket(self, name):
        if name in self._storage:
            raise exceptions.S3Error('BucketAlreadyExists')

        bucket = entities.Bucket(name)

        self._storage[bucket.name] = \
        {
            'bucket': bucket,
            'objects': {},
        }

    def delete_bucket(self, name):
        self.head_bucket(name)

        del self._storage[name]

    def head_bucket(self, name, **kwargs):
        if name not in self._storage:
            raise exceptions.S3Error('NoSuchBucket')

    def put_object(self, bucket_name, object_key, object_data):
        bucket = self.get_bucket(bucket_name)

        object = entities.Object(object_key, bucket)

        self._storage[bucket.name]['objects'][object.key] = object

    def get_object(self, bucket_name, object_key):
        self.head_object(bucket_name, object_key)

        data = self._storage[bucket_name]['objects'][object_key]['data']

        return io.BytesIO(data)

    def list_objects(self, bucket_name):
        self.head_bucket(bucket_name)

        for object in self._storage[bucket_name]['objects'].values():
            yield object

    def delete_object(self, bucket_name, object_key):
        self.head_bucket(bucket_name)

        if object_key in self._storage[bucket_name]['objects']:
            del self._storage[bucket_name]['objects'][object_key]

    def head_object(self, bucket_name, object_key):
        if object_key not in self._storage[bucket_name]['objects']:
            raise exceptions.S3Error('NoSuchKey')
