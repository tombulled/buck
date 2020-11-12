import fastapi
from . import responses
from . import middleware
from . import utils
from . import orm

"""
TODO:
    * Pass client info through to functions
"""

app = fastapi.FastAPI()

db = orm.Database('sqlite:///./db.db')

# app.add_middleware(middleware.AwsSignatureV4Middleware)

# ListBuckets
@app.get('/')
def read_root(*, db = fastapi.Depends(db)):
    print(db)

    data = \
    {
        'Buckets': \
        {
            'Bucket': [],
        },
        'Owner': \
        {
            'DisplayName': '',
            'ID': '02d6176db174dc93cb1b899f7c6078f08654445fe8cf1b6ce98d8855f66bdbf4',
        }
    }

    return responses.AwsResponse('ListAllMyBucketsResult', data)
