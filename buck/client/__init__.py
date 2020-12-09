from .client import client
import functools

s3 = functools.partial(client, service = 's3')
