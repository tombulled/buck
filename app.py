import boto3

s3 = boto3.resource \
(
    's3',
    endpoint_url = 'http://127.0.0.1:8000',
    config = boto3.session.Config(signature_version = 's3v4'),
)

print(list(s3.buckets.all()))

print(s3.create_bucket(Bucket='foo'))
