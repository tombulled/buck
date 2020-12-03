from . import responses
from . import dependencies

import fastapi
import fastapi.responses

router = fastapi.APIRouter \
(
    default_response_class = responses.AwsResponse,
)

"""

TODO:
    * Make StackError which raises a service error
        * e.g: StackError [S3] Invalid bucket name
    * stack.Stack needs major improvements
    * Need to store bucket owner
    * Need to overwrite the default fastapi json errors: e.g. GET /bucket_name/
    * stack.model and stack.services.s3.models.base shouldn't both exist
    * dependencies.py needs a nice sortout
    * Handle a generic Exception being raised in AwsExceptionHandlerMiddleware more appropriately (use rich?)

    * Use poetry!
        * Use rich for those beautiful errors atleast?
    * Ensure all errors (from constants.ERRORS) are being used appropriately
    * Remove references to aws (replace with 'stack')
    * Should I be avoiding inheriting from starlette.middleware.base.BaseHTTPMiddleware ?
    * Improve responses.RangedStreamingResponse to get the request object itself so can be used as response_class
    * Apply s3 dependency at router level so each method doesn't need to declare it.
    * Flesh out all required headers etc. for simple methods
    * AWS CLI fails on create-bucket when it returns status_code:307
    * Still still still not happy with how validation is carried out :/
"""

@router.get('/')
def list_buckets \
        (
            s3 = fastapi.Depends(dependencies.s3),
        ):
    return \
    {
        'ListAllMyBucketsResult': \
        {
            'Buckets': \
            {
                'Bucket': \
                [
                    {
                        'Name':         bucket.name,
                        'CreationDate': bucket.creation_date,
                    }
                    for bucket in s3.list_buckets()
                ],
            },
            'Owner': \
            {
                'DisplayName': s3.user and s3.user.name,
                'ID':          s3.user and s3.user.id,
            },
        },
    }

@router.put('/{bucket_name}', response_class = responses.RedirectResponse)
def create_bucket \
        (
            bucket_name: str,
            s3 = fastapi.Depends(dependencies.s3),
        ):
    s3.create_bucket(bucket_name)

    return f'/{bucket_name}'

@router.head('/{bucket_name}', response_class = responses.Response)
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

@router.delete('/{bucket_name}', response_class = responses.StatusResponse)
def delete_bucket \
        (
            bucket_name: str,
            s3 = fastapi.Depends(dependencies.s3),
        ):
    s3.delete_bucket(bucket_name)

    return 204

@router.put('/{bucket_name}/{object_key:path}', response_class = responses.Response)
async def put_object \
        (
            request: fastapi.Request,
            bucket_name: str,
            object_key: str,
            s3 = fastapi.Depends(dependencies.s3),
        ):
    request_body = await request.body()

    s3.put_object(bucket_name, object_key, request_body)

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

@router.delete('/{bucket_name}/{object_key:path}', response_class = responses.StatusResponse)
def delete_object \
        (
            bucket_name: str,
            object_key: str,
            s3 = fastapi.Depends(dependencies.s3),
        ):
    s3.delete_object(bucket_name, object_key)

    return 204

@router.head('/{bucket_name}/{object_key:path}', response_class = responses.Response)
def head_object \
        (
            bucket_name: str,
            object_key: str,
            s3 = fastapi.Depends(dependencies.s3),
        ):
    s3.head_object(bucket_name, object_key)

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
