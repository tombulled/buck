from .... import service_session
from .... import exceptions

import abc

def generator(iterable):
    for item in iterable:
        yield item

class SimpleStorageServiceSession(service_session.StackServiceSession, abc.ABC):
    @abc.abstractmethod
    def list_buckets(self, **kwargs):
        return generator(())

    @abc.abstractmethod
    def get_bucket(self, name: str, **kwargs):
        raise exceptions.S3Error('NoSuchBucket')

    @abc.abstractmethod
    def create_bucket(self, name: str, **kwargs):
        pass

    @abc.abstractmethod
    def delete_bucket(self, name: str, **kwargs):
        pass

    @abc.abstractmethod
    def head_bucket(self, name: str, **kwargs):
        pass

    @abc.abstractmethod
    def put_object(self, bucket_name: str, object_key: str, object_data: bytes, **kwargs):
        pass

    @abc.abstractmethod
    def get_object(self, bucket_name: str, object_key: str, **kwargs):
        raise exceptions.S3Error('NoSuchKey')

    @abc.abstractmethod
    def list_objects(self, bucket_name: str, **kwargs):
        return generator(())

    @abc.abstractmethod
    def delete_object(self, bucket_name: str, object_key: str, **kwargs):
        pass

    @abc.abstractmethod
    def head_object(self, bucket_name: str, object_key: str, **kwargs):
        raise exceptions.S3Error('NoSuchKey')
