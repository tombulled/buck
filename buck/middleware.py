from . import responses
from . import aws

import starlette.middleware.base
import urllib.parse
import datetime

class AwsAuthenticationSignatureV2Middleware(starlette.middleware.base.BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        return responses.AwsErrorResponse() # Error: not supported

class AwsAuthenticationSignatureV4Middleware(starlette.middleware.base.BaseHTTPMiddleware):
    @staticmethod
    async def parse_request(request):
        uri = request.scope['path']
        method = request.scope['method'].upper()
        query_string = request.scope['query_string'].decode().strip()

        parameters = dict(urllib.parse.parse_qsl(query_string))

        amz_date = request.headers.get('X-Amz-Date')

        if amz_date is None: return

        headers = dict(request.headers)

        date = datetime.datetime.strptime(amz_date, '%Y%m%dT%H%M%SZ')

        body = (await request.body()).decode()

        return \
        {
            'date': date,
            'parameters': parameters,
            'headers': headers,
            'body': body,
            'uri': uri,
            'method': method,
        }

    async def dispatch(self, request, call_next):
        signer = aws.AwsSignatureV4()

        authorization = request.headers.get('Authorization')

        if authorization is None:
            return responses.AwsErrorResponse() # Error!

        auth = signer.parse_authorization(authorization)

        if auth is None:
            return responses.AwsErrorResponse() # Error!

        data = await self.parse_request(request)

        if data is None:
            return responses.AwsErrorResponse() # Error!

        for header_name in tuple(data['headers']):
            for signed_header_name in auth['signed_headers']:
                if header_name.lower() == signed_header_name:
                    break
            else:
                data['headers'].pop(header_name)

        signature = signer.create_signature \
        (
            access_key = auth['credential']['access_key'],
            secret_key = 'admin', # NOTE: This is TEMP, needs to be acquired
            date = data['date'],
            service = auth['credential']['service'],
            region = auth['credential']['region'],
            request = auth['credential']['request'],
            algorithm = auth['algorithm'],
            parameters = data['parameters'],
            headers = data['headers'],
            body = data['body'],
            method = data['method'],
            uri = data['uri'],
        )

        # Authentication invalid
        if signature != auth['signature']:
            return responses.AwsErrorResponse() # Error!

        request.state.access_key = auth['credential']['access_key']

        response = await call_next(request)

        return response

class AwsAuthenticationMiddleware(starlette.middleware.base.BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        authorization = request.headers.get('Authorization')

        if authorization is None:
            return responses.AwsErrorResponse() # Error

        algorithm = authorization.strip().split()[0].upper()

        algorithm_version = algorithm.split('-', 1)[0]

        middleware = \
        {
            'AWS': AwsAuthenticationSignatureV2Middleware,
            'AWS4': AwsAuthenticationSignatureV4Middleware,
        }

        if algorithm_version not in middleware:
            return responses.AwsErrorResponse() # Error

        return await middleware[algorithm_version](self.app).dispatch(request, call_next)

class AwsAnonymousAuthenticationMiddleware(starlette.middleware.base.BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        request.state.access_key = 'anonymous'

        return await call_next(request)
