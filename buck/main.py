from . import responses
from . import middleware
from . import aws
from . import storage
from . import utils
from . import dependencies

import fastapi
import datetime
import typing
import fastapi.responses
import fastapi.staticfiles
import hashlib
import os
import xmltodict
from typing import Optional

from pprint import pprint as pp # Dev

# REF: https://docs.aws.amazon.com/AmazonS3/latest/API/s3-api.pdf
# REF: https://docs.aws.amazon.com/AmazonS3/latest/API/API_Operations_Amazon_Simple_Storage_Service.html
# REF: https://docs.aws.amazon.com/cli/latest/reference/s3api/

"""
Tables:
    bucket: id, name, creation_date, (owner_id)
    user: id, name, secret_key, access_key
    object: id, key, last_modified?, etag?, size?, storage_class?, owner_id

Version id of object: commit id
"""

api = fastapi.FastAPI()
storage = storage.Storage('/tmp/buck-store')

# api.add_middleware(middleware.AwsAuthenticationMiddleware)

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

    request_body = await request.body()

    bucket = storage.get_bucket(bucket_name)

    if bucket is None:
        return responses.AwsErrorResponse() # Error!

    object = bucket.put_object(object_path, request_body)

    return fastapi.Response()

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

    file = object.path.open('rb')

    return responses.RangedStreamingResponse(request, file)

@api.delete('/{bucket_name}/{object_path:path}')
def delete_object(*, request: fastapi.Request, bucket_name: str, object_path: str):
    bucket_name = bucket_name.lower()
    object_path = object_path.lower()

    bucket = storage.get_bucket(bucket_name)

    if bucket is None:
        return responses.AwsErrorResponse() # Error!

    object = bucket.get_object(object_path)

    if object is None:
        return responses.AwsErrorResponse() # Error!

    success = object.delete()

    if not success:
        return responses.AwsErrorResponse() # Error!

    return fastapi.Response(status_code = 204)

@api.post('/{bucket_name}')
async def delete_objects \
        (
            *,
            request: fastapi.Request,
            request_body = fastapi.Depends(dependencies.payload),
            bucket_name: str,
            delete: str,
        ):
    bucket_name = bucket_name.lower()

    bucket = storage.get_bucket(bucket_name)

    if bucket is None:
        return responses.AwsErrorResponse() # Error!

    try:
        deleted_results = []
        error_results = []

        object_entries = request_body['Delete']['Object']

        for object_entry in object_entries:
            object_key = object_entry['Key'].lower()

            object = bucket.get_object(object_key)

            success = object.delete() if object is not None else True

            if success:
                result = \
                {
                    # 'DeleteMarker': ,
                    # 'DeleteMarkerVersionId': ,
                    'Key': object_key,
                    # 'VersionId': ,
                }

                deleted_results.append(result)
            else:
                result = \
                {
                    'Code': 'AccessDenied', # Temp placeholder
                    'Key': object_key,
                    'Message': 'Access Denied', # Temp placeholder
                    'VersionId': '1', # Temp placeholder
                }

                error_results.append(result)

        response_data = \
        {
            'Deleted': deleted_results,
            'Error': error_results,
        }

        return responses.AwsResponse('DeleteResult', response_data, pretty=True)
    except: # This is kinda cheating
        return responses.AwsErrorResponse() # Error!

@api.get('/{bucket_name}')
def list_objects \
        (
            *,
            request: fastapi.Request,
            bucket_name: str,
            prefix: Optional[str] = None,
            list_type: Optional[int] = 1,
        ):
    bucket_name = bucket_name.lower()

    bucket = storage.get_bucket(bucket_name)

    if bucket is None:
        return responses.AwsErrorResponse() # Error!

    contents = []

    if list_type not in (1, 2):
        return responses.AwsErrorResponse() # Error!

    objects = bucket.list_objects(prefix=prefix)

    for object in objects:
        object_data = \
        {
            'Key': object.name,
            'LastModified': utils.iso_datetime(object.last_modified_date),
            'ETag': '', # Temp
            'Size': object.size,
            'StorageClass': 'STANDARD', # Temp
        }

        contents.append(object_data)

    data = \
    {
        'IsTruncated': False,
        # 'Marker': '',
        # 'NextMarker': '',
        'Contents': contents,
        'Name': bucket.name,
        'Prefix': prefix,
        # 'Delimeter': '',
        # 'MaxKeys': '',
        # 'CommonPrefixes': '',
        'EncodingType': 'url',
    }

    return responses.AwsResponse('ListBucketResult', data)
