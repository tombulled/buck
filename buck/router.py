from . import responses
from . import dependencies

import fastapi
import fastapi.responses

router = fastapi.APIRouter()

@router.get('/')
def list_buckets \
        (
            s3 = fastapi.Depends(dependencies.s3),
        ):
    data = \
    {
        'Buckets': \
        {
            'Bucket': \
            [
                {
                    'Name': bucket.name,
                    'CreationDate': str(bucket.creation_date),
                }
                for bucket in s3.list_buckets()
            ],
        },
        'Owner': \
        {
            'DisplayName': s3.session.user.name,
            'ID': s3.session.user.id,
        },
    }

    return responses.AwsResponse('ListAllMyBucketsResult', data)

@router.put('/{bucket_name}')
def create_bucket \
        (
            bucket_name: str,
            s3 = fastapi.Depends(dependencies.s3),
        ):
    s3.create_bucket(bucket_name)

    return fastapi.responses.RedirectResponse(url = f'/{bucket_name}')

@router.head('/{bucket_name}')
def head_bucket \
        (
            bucket_name: str,
            s3 = fastapi.Depends(dependencies.s3),
            headers = fastapi.Depends(dependencies.amz_headers),
        ):
    expected_bucket_owner = headers.get('expected-bucket-owner')

    s3.head_bucket \
    (
        name           = bucket_name,
        expected_owner = expected_bucket_owner,
    )

    return fastapi.Response()

@router.delete('/{bucket_name}')
def delete_bucket \
        (
            bucket_name: str,
            s3 = fastapi.Depends(dependencies.s3),
        ):
    s3.delete_bucket(bucket_name)

    return fastapi.Response(status_code = 204)

@router.put('/{bucket_name}/{object_key:path}')
async def put_object \
        (
            request: fastapi.Request,
            bucket_name: str,
            object_key: str,
            s3 = fastapi.Depends(dependencies.s3),
        ):
    request_body = await request.body()

    s3.put_object(bucket_name, object_key, request_body)

    return fastapi.Response()

@router.get('/{bucket_name}/{object_key:path}')
def get_object \
        (
            request: fastapi.Request,
            bucket_name: str,
            object_key: str,
            s3 = fastapi.Depends(dependencies.s3),
        ):
    object_data = s3.get_object(bucket_name, object_key)

    return responses.RangedStreamingResponse(request, object_data)

@router.delete('/{bucket_name}/{object_key:path}')
def delete_object \
        (
            bucket_name: str,
            object_key: str,
            s3 = fastapi.Depends(dependencies.s3),
        ):
    s3.delete_object(bucket_name, object_key)

    return fastapi.Response(status_code = 204)

@router.head('/{bucket_name}/{object_key:path}')
def head_object \
        (
            bucket_name: str,
            object_key: str,
            s3 = fastapi.Depends(dependencies.s3),
        ):
    s3.head_object(bucket_name, object_key)

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
