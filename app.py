import boto3

# s3 = boto3.resource \
# (
#     's3',
#     endpoint_url = 'http://127.0.0.1:8000',
#     config = boto3.session.Config(signature_version = 's3v4'),
# )

client = boto3.client \
(
    's3',
    endpoint_url = 'http://127.0.0.1:8000',
    config = boto3.session.Config(signature_version = 's3v4'),
)

# print(list(client.buckets.all()))
#
bucket_name = 'hello'

# print(client.create_bucket(Bucket=bucket_name))

client.delete_objects \
(
    Bucket = bucket_name,
    Delete = \
    {
        'Objects': \
        [
            {'Key': 'test.txt'},
            {'Key': 'yey/test.txt'},
        ],
    },
)
