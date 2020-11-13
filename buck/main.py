from . import responses
from . import middleware
from . import utils
from . import orm
from . import models
from . import aws

import fastapi
import datetime
import typing
import fastapi.responses
# import dulwich.porcelain

# Dev
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
database = orm.Database('sqlite:///./db.db')

database.create_all(models.BaseModel)

# api.add_middleware(middleware.AwsAuthenticationMiddleware)
api.add_middleware(middleware.RequestBodyMiddleware)

# Temp
# @api.middleware('http')
# async def middleware_test(request, call_next):
#     print('Request Body:', await request.body())
#
#     return await call_next(request)

@api.get('/')
def list_buckets(*, request: fastapi.Request, db = fastapi.Depends(database)):
    owner = db.query(models.User).filter(models.User.access_key == request.state.access_key).first()

    data = \
    {
        'Buckets': \
        {
            'Bucket': \
            [
                {
                    'CreationDate': utils.iso_datetime(bucket.creation_date),
                    'Name': bucket.name,
                }
                for bucket in owner.buckets
            ],
        },
        'Owner': \
        {
            'DisplayName': owner.name,
            'ID': owner.id,
        }
    }

    return responses.AwsResponse('ListAllMyBucketsResult', data)

@api.put('/{bucket_name}')
def create_bucket(*, request: fastapi.Request, db = fastapi.Depends(database), bucket_name: str):
    bucket_name = bucket_name.lower()

    if db.query(models.Bucket).filter(models.Bucket.name == bucket_name).first():
        return responses.AwsErrorResponse() # Error!

    owner = db.query(models.User).filter(models.User.access_key == request.state.access_key).first()

    bucket = models.Bucket \
    (
        name = bucket_name,
        creation_date = datetime.datetime.now(),
    )

    owner.buckets.append(bucket)

    db.add(bucket)
    db.commit()

    response = fastapi.responses.RedirectResponse(url = f'/{bucket_name}', status_code = 200)

    return response

@api.head('/{bucket_name}')
def head_bucket(*, request: fastapi.Request, db = fastapi.Depends(database), bucket_name: str):
    bucket_name = bucket_name.lower()

    owner = db.query(models.User).filter(models.User.access_key == request.state.access_key).first()
    bucket = db.query(models.Bucket).filter(models.Bucket.owner_id == owner.id, models.Bucket.name == bucket_name).first()

    if bucket is None:
        return responses.AwsErrorResponse() # Error!

    return fastapi.Response(status_code = 200)

@api.delete('/{bucket_name}')
def delete_bucket(*, request: fastapi.Request, db = fastapi.Depends(database), bucket_name: str):
    bucket_name = bucket_name.lower()

    owner = db.query(models.User).filter(models.User.access_key == request.state.access_key).first()
    bucket = db.query(models.Bucket).filter(models.Bucket.owner_id == owner.id, models.Bucket.name == bucket_name).first()

    if bucket is None:
        return responses.AwsErrorResponse() # Error!

    db.delete(bucket)
    db.commit()

    return fastapi.Response(status_code = 204)

# TODO (All Below):

@api.delete('/{bucket_name}/{object_path:path}')
def delete_object(*, request: fastapi.Request, db = fastapi.Depends(database), bucket_name: str, object_path: str):
    return responses.AwsErrorResponse() # TODO

@api.post('/')
def delete_objects(*, request: fastapi.Request, db = fastapi.Depends(database)):
    return responses.AwsErrorResponse() # TODO

@api.get('/{bucket_name}/{object_path:path}')
def get_object(*, request: fastapi.Request, db = fastapi.Depends(database), bucket_name: str, object_path: str):
    import io
    file = io.StringIO('Hello from the other side.')

    return fastapi.responses.StreamingResponse(file, media_type='text/plain')

@api.put('/{bucket_name}/{object_path:path}')
async def put_object \
        (
            *,
            request: fastapi.Request,
            db = fastapi.Depends(database),
            bucket_name: str,
            object_path: str,
        ):
    pp(dict(request.headers))

    print('PutObject got:', request.state.body)

    # Before proceeding need to make some big decisions

    return fastapi.Response()
