import fastapi
from . import responses
from . import middleware
from . import utils
from . import orm
from . import models

"""
TODO:
    * Pass client info through to functions
"""

api = fastapi.FastAPI()
database = orm.Database('sqlite:///./db.db')

database.create_all(models.BaseModel)

# app.add_middleware(middleware.AwsSignatureV4Middleware)

# ListBuckets
@api.get('/')
def read_root(*, db = fastapi.Depends(database)):
    buckets_data = []

    buckets = db.query(models.Bucket).all()

    for bucket in buckets:
        bucket_data = \
        {
            'CreationDate': utils.iso_datetime(bucket.creation_date),
            'Name': bucket.name,
        }

        buckets_data.append(bucket_data)

    data = \
    {
        'Buckets': \
        {
            'Bucket': buckets_data,
        },
        'Owner': \
        {
            'DisplayName': '',
            'ID': '02d6176db174dc93cb1b899f7c6078f08654445fe8cf1b6ce98d8855f66bdbf4',
        }
    }

    return responses.AwsResponse('ListAllMyBucketsResult', data)
