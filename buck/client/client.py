import boto3

def client \
        (
            service:    str,
            host:       str = '127.0.0.1',
            port:       int = 8000,
            scheme:     str = 'http',
            access_key: str = None,
            secret_key: str = None,
            *kwargs,
        ):
    return boto3.client \
    (
        service,
        endpoint_url          = f'{scheme}://{host}:{port}',
        config                = boto3.session.Config(signature_version = 's3v4'),
        aws_access_key_id     = access_key,
        aws_secret_access_key = secret_key,
        **kwargs,
    )
