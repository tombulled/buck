from . import responses
from . import middleware
from . import aws
from . import storage
from . import utils

import fastapi
import datetime
import typing
import fastapi.responses
import fastapi.staticfiles
import hashlib
import re
import os

from pprint import pprint as pp

# REF: https://docs.aws.amazon.com/AmazonS3/latest/API/s3-api.pdf
# REF: https://docs.aws.amazon.com/AmazonS3/latest/API/API_Operations_Amazon_Simple_Storage_Service.html
# REF: https://docs.aws.amazon.com/cli/latest/reference/s3api/

"""
Rename to buckit?

TODO:
    PutObject
    HeadObject
    GetObject
    ListObjects
    DeleteObject

    ? DeleteObjects
    # ListObjectsV2
    # ListObjectVersions
    # RestoreObject

Tables:
    bucket: id, name, creation_date, (owner_id)
    user: id, name, secret_key, access_key
    object: id, key, last_modified?, etag?, size?, storage_class?, owner_id

Version id of object: commit id
"""

api = fastapi.FastAPI()
# storage = storage.Storage('/tmp/buck-store')
storage = storage.VersionedStorage('/tmp/buck-store')

# api.add_middleware(middleware.AwsAuthenticationMiddleware)
api.add_middleware(middleware.RequestBodyMiddleware)

api.mount('/static', fastapi.staticfiles.StaticFiles(directory='/home/mint/Videos'), name='static')

# Temp
# @api.middleware('http')
# async def middleware_test(request, call_next):
#     print('Request Body:', await request.body())
#
#     return await call_next(request)

class User(object):
    def __init__(self, access_key):
        self.access_key = access_key

    @property
    def id(self) -> str:
        if self.access_key:
            return hashlib.md5(self.access_key.encode()).hexdigest()

        return ''

    @property
    def display_name(self) -> str:
        if self.access_key:
            return self.access_key

        return ''

@api.get('/')
def list_buckets(*, request: fastapi.Request):
    access_key = request.state._state.get('access_key', None)

    # Move this?
    user = User(access_key)

    data = \
    {
        'Buckets': \
        {
            'Bucket': \
            [
                {
                    'Name': bucket.name,
                    'CreationDate': utils.iso_datetime(bucket.creation_date),
                }
                for bucket in storage.list_buckets()
            ],
        },
        'Owner': \
        {
            'DisplayName': user.display_name,
            'ID': user.id,
        },
    }

    return responses.AwsResponse('ListAllMyBucketsResult', data)

@api.put('/{bucket_name}')
def create_bucket(*, request: fastapi.Request, bucket_name: str):
    bucket_name = bucket_name.lower()

    if storage.head_bucket(bucket_name):
        return responses.AwsErrorResponse() # Error

    bucket = storage.create_bucket(bucket_name)

    if bucket is None:
        return responses.AwsErrorResponse() # Error

    response = fastapi.responses.RedirectResponse(url = f'/{bucket.name}', status_code = 200)

    return response

@api.head('/{bucket_name}')
def head_bucket(*, request: fastapi.Request, bucket_name: str):
    bucket_name = bucket_name.lower()

    if not storage.head_bucket(bucket_name):
        return responses.AwsErrorResponse() # Error!

    return fastapi.Response(status_code = 200)

@api.delete('/{bucket_name}')
def delete_bucket(*, request: fastapi.Request, bucket_name: str):
    bucket_name = bucket_name.lower()

    if not storage.head_bucket(bucket_name):
        return responses.AwsErrorResponse() # Error!

    success = storage.delete_bucket(bucket_name)

    if not success:
        return responses.AwsErrorResponse() # Error!

    return fastapi.Response(status_code = 204)

@api.put('/{bucket_name}/{object_path:path}')
async def put_object \
        (
            *,
            request: fastapi.Request,
            bucket_name: str,
            object_path: str,
        ):
    bucket_name = bucket_name.lower()
    object_path = object_path.lower()

    bucket = storage.get_bucket(bucket_name)

    if bucket is None:
        return responses.AwsErrorResponse() # Error!

    object = bucket.put_object(object_path, request.state.body)

    return fastapi.Response()

# TODO (All Below):

# @api.delete('/{bucket_name}/{object_path:path}')
# def delete_object(*, request: fastapi.Request, db = fastapi.Depends(database), bucket_name: str, object_path: str):
#     bucket_name = bucket_name.lower()
#     object_path = object_path.lower()
#
#     bucket = storage.get_bucket(bucket_name)
#
#     if bucket is None:
#         return responses.AwsErrorResponse() # Error!
#
#     object = bucket.get_object(object_path, request.state.body)
#
#     return responses.AwsErrorResponse() # TODO

# @api.post('/')
# def delete_objects(*, request: fastapi.Request, db = fastapi.Depends(database)):
#     return responses.AwsErrorResponse() # TODO
#

class RangeFileWrapper(object):
    def __init__(self, filelike, blksize=8192, offset=0, length=None):
        self.filelike = filelike
        self.filelike.seek(offset, os.SEEK_SET)
        self.remaining = length
        self.blksize = blksize

    def close(self):
        if hasattr(self.filelike, 'close'):
            self.filelike.close()

    def __iter__(self):
        return self

    def __next__(self):
        if self.remaining is None:
            # If remaining is None, we're reading the entire file.
            data = self.filelike.read(self.blksize)
            if data:
                return data
            raise StopIteration()
        else:
            if self.remaining <= 0:
                raise StopIteration()
            data = self.filelike.read(min(self.remaining, self.blksize))
            if not data:
                raise StopIteration()
            self.remaining -= len(data)
            return data


@api.get('/{bucket_name}/{object_path:path}')
def get_object(*, request: fastapi.Request, bucket_name: str, object_path: str):
    bucket_name = bucket_name.lower()
    object_path = object_path.lower()

    bucket = storage.get_bucket(bucket_name)

    if bucket is None:
        return responses.AwsErrorResponse() # Error!

    object = bucket.get_object(object_path)

    if not object._exists():
        return responses.AwsErrorResponse() # Error!
    #
    # pp(dir(request.headers))
    # pp(dict(request.headers))
    # pp(request.headers.as_dict())

    # response = fastapi.Response(content=b'a'*1024)
    #

    # return response

    print('GET OBJECT')

    import os.path
    size = os.path.getsize(object.path)

    # print(size)

    # file = object.path.open('rb')
    file = open(str(object.path), 'rb')

    range = request.headers.get('range')

    # if range is None:
    #     return fastapi.responses.StreamingResponse(file, media_type = object.mime_type)
    # else:

    # response = fastapi.responses.FileResponse(object.path, media_type = object.mime_type)
    # return fastapi.responses.FileResponse(object.path, media_type = object.mime_type)
    # response = fastapi.responses.StreamingResponse(file, media_type = object.mime_type)

    # print(object.mime_type)

    if range is not None:
        # return fastapi.Response(content='hello')
        # response = fastapi.Response(content='hello')
        # response = fastapi.responses.FileResponse(object.path)
        #
        # response.headers['Content-Length'] = str(size)
        # response.headers['Accept-Ranges'] = 'bytes'
        range = range.strip().lower()
        range = range.split('=')[-1]

        range_start, range_end, *_ = map(str.strip, (range + '-').split('-'))

        # match = re.match(r'bytes=(?P<start>.*)-(?P<end>.+)?', range)

        # range_start = match.group('start')
        # range_end = match.group('end')

        # range_start = range_start.strip

        if not range_start:
            range_start = 0
        if not range_end:
            range_end = size - 1

        range_start = int(range_start)
        range_end = int(range_end)

        # range_end = range_start
        # range_start = 0
        # range_start, range_end = 0, range_start

        length = range_end - range_start + 1

        max_length = 1024 * 1024
        max_length = 1024 * 512

        # if length > max_length:
        #     range_end = range_start + max_length
        #     length = range_end - range_start + 1

        # print('Range:', range_start, range_end, 'Length:', length)

        # file.seek(range_start)

        # response = fastapi.responses.StreamingResponse(RangeFileWrapper(file, offset=range_start, length=length, blksize=1024*1024), media_type = object.mime_type)
        # response = fastapi.responses.StreamingResponse(file, media_type = object.mime_type, status_code=206)
        # response = fastapi.responses.StreamingResponse(RangeFileWrapper(file, offset=range_start, length=length), media_type = 'application/octet-stream')

        response = fastapi.responses.StreamingResponse(RangeFileWrapper(file, offset=range_start, length=length), media_type = object.mime_type, status_code=206)
        # response = fastapi.responses.StreamingResponse(RangeFileWrapper(file, offset=range_start, length=length), media_type = object.mime_type, status_code=200)

        response.headers['Accept-Ranges'] = 'bytes'
        response.headers['Content-Length'] = str(length)
        response.headers['Content-Range'] = f'bytes {range_start}-{range_end}/{size}'
        # response.headers['Connection'] = 'keep-alive'

    else:
        # import io
        # file = io.StringIO('hello')
        # bytes = io.BytesIO(file.read())
        # response = fastapi.responses.StreamingResponse(file, media_type = object.mime_type)
        # response = fastapi.responses.StreamingResponse(bytes, media_type = object.mime_type)
        # response = fastapi.responses.StreamingResponse(file, media_type = 'text/plain')
        # response = fastapi.responses.FileResponse(object.path, media_type = object.mime_type)
        # response = fastapi.responses.FileResponse(object.path, media_type = 'application/octet-stream')
        # response.chunk_size = 1024 * 1024
        # response.chunk_size = 1024 * 8
        # response.chunk_size = 1024 * 16
        # response.chunk_size = 1024
        # response.chunk_size = 1024 * 1024 * 10

        response = fastapi.responses.FileResponse(object.path, media_type = 'video/mp4; charset=utf-8')
        response.headers['Content-Length'] = str(size)

    # return fastapi.responses.StreamingResponse(file, media_type = object.mime_type)
    # response = fastapi.responses.FileResponse(object.path, media_type = object.mime_type)

    response.headers['Accept-Ranges'] = 'bytes'
    response.headers['cache-control'] = 'max-age=3600'
    response.headers['Connection'] = 'keep-alive'
    # del response.headers['etag']

    # pp(dict(response.headers))


    return response
