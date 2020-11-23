from . import responses
from . import aws
from . import utils
from . import dependencies
from . import exceptions

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

"""
Next:
    Push update to GitHub
    
    Make <User> instance an attribute of storage:
        @depend storage
        print(storage.user.id)
    ... Storage instances can only be created when provided with user credentials

    Move all actions to S3 objects to become form:
            s3.delete_object(bucket_name, object_key)
        not:
            bucket.delete_object(object_key)
        ??

    Validate bucket names, object keys etc.
    Testcases
    Logging:
        e.g. User 'bob' created bucket 'foo'
    When no user, create 'anonymous' user

Notes:
    * <User> object?
    * ACL
    * Use dynamodb.py as database when made
    * Use base-classes that allow all, but keep extensible

Attributes:
    Bucket: name, region, Amazon resource name (ARN), creation date,
        Access (rights), versioning (enabled), tags, encryption,
        archive configuration, access logging, CloudTrail data events,
        event notifications, transfer acceleration, object lock,
        requester pays, static website hosting
"""

# REF: https://docs.aws.amazon.com/AmazonS3/latest/API/s3-api.pdf
# REF: https://docs.aws.amazon.com/AmazonS3/latest/API/API_Operations_Amazon_Simple_Storage_Service.html
# REF: https://docs.aws.amazon.com/cli/latest/reference/s3api/

router = fastapi.APIRouter()

@router.get('/')
def list_buckets \
        (
            storage = fastapi.Depends(dependencies.storage),
            user = fastapi.Depends(dependencies.user),
        ):
    data = \
    {
        'Buckets': \
        {
            'Bucket': \
            [
                {
                    'Name': bucket.name,
                    'CreationDate': bucket.creation_date,
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

@router.put('/{bucket_name}')
def create_bucket \
        (
            bucket_name: str,
            storage = fastapi.Depends(dependencies.storage),
        ):
    bucket = storage.create_bucket(bucket_name)

    return fastapi.responses.RedirectResponse(url = f'/{bucket.name}')

@router.head('/{bucket_name}')
def head_bucket \
        (
            bucket_name: str,
            storage = fastapi.Depends(dependencies.storage),
            headers = fastapi.Depends(dependencies.amz_headers),
        ):
    expected_bucket_owner = headers.get('expected-bucket-owner')

    storage.head_bucket \
    (
        name = bucket_name,
        expected_owner = expected_bucket_owner,
    )

    return fastapi.Response()

@router.delete('/{bucket_name}')
def delete_bucket \
        (
            bucket_name: str,
            storage = fastapi.Depends(dependencies.storage),
        ):
    storage.delete_bucket(bucket_name)

    return fastapi.Response(status_code = 204)

@router.put('/{bucket_name}/{object_key:path}')
async def put_object \
        (
            request: fastapi.Request,
            bucket_name: str,
            object_key: str,
            storage = fastapi.Depends(dependencies.storage),
        ):
    request_body = await request.body()

    bucket = storage.get_bucket(bucket_name)

    bucket.put_object(object_key, request_body)

    return fastapi.Response()

@router.get('/{bucket_name}/{object_key:path}')
def get_object \
        (
            request: fastapi.Request,
            bucket_name: str,
            object_key: str,
            storage = fastapi.Depends(dependencies.storage),
        ):
    bucket = storage.get_bucket(bucket_name)

    object = bucket.get_object(object_key)

    file = object.open()

    return responses.RangedStreamingResponse(request, file)

@router.delete('/{bucket_name}/{object_key:path}')
def delete_object \
        (
            bucket_name: str,
            object_key: str,
            storage = fastapi.Depends(dependencies.storage),
        ):
    bucket = storage.get_bucket(bucket_name)

    bucket.delete_object(object_key)

    return fastapi.Response(status_code = 204)

@router.head('/{bucket_name}/{object_key:path}')
def head_object \
        (
            bucket_name: str,
            object_key: str,
            storage = fastapi.Depends(dependencies.storage),
        ):
    bucket = storage.get_bucket(bucket_name)

    bucket.head_object(object_key)

    return fastapi.Response()

"""
@router.post('/{bucket_name}')
async def delete_objects \
        (
            bucket_name: str,
            delete: str,
            payload = fastapi.Depends(dependencies.payload),
            storage = fastapi.Depends(dependencies.storage),
        ):
    bucket = storage.get_bucket(bucket_name)

    try:
        deleted_results = []
        error_results = []

        object_entries = payload['Delete']['Object']

        for object_entry in object_entries:
            object_key = object_entry['Key']

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
"""

"""
@router.get('/{bucket_name}')
def list_objects \
        (
            bucket_name: str,
            prefix: Optional[str] = None,
            list_type: Optional[int] = 1,
            storage = fastapi.Depends(dependencies.storage),
        ):
    bucket = storage.get_bucket(bucket_name)

    if bucket is None:
        return responses.AwsErrorResponse() # Error!

    contents = []

    if list_type not in (1, 2):
        return responses.AwsErrorResponse() # Error!

    kwargs = {}

    if prefix is not None:
        kwargs['prefix'] = prefix

    objects = bucket.list_objects(**kwargs)

    for object in objects:
        object_data = \
        {
            'Key': object.key,
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
"""
