from . import responses
from . import aws
from ..stack import exceptions

import starlette.middleware.base
import urllib.parse
import datetime

class AwsExceptionHandlerMiddleware(starlette.middleware.base.BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        exception = None

        try:
            return await call_next(request)
        except exceptions.S3Error as error:
            exception = error
        except Exception as error:
            exception = exceptions.S3Error('InternalError')

            exception.description = str(error)

            # Temp?
            raise error

        status_code = exception.status_code or 400

        error = \
        {
            'code':    exception.code,
            'message': exception.description,
        }

        return responses.AwsErrorResponse(error, status_code = status_code)

class BaseAwsAuthenticationSignatureMiddleware(starlette.middleware.base.BaseHTTPMiddleware):
    def __init__(self, app, *, stack):
        super().__init__(app)

        self.stack = stack

class AwsAuthenticationSignatureV2Middleware(BaseAwsAuthenticationSignatureMiddleware):
    async def dispatch(self, request, call_next):
        raise exceptions.S3Error('InvalidEncryptionAlgorithmError')

class AwsAuthenticationSignatureV4Middleware(BaseAwsAuthenticationSignatureMiddleware):
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
            raise exceptions.S3Error('AccessDenied')

        auth = signer.parse_authorization(authorization)

        if auth is None:
            raise exceptions.S3Error('AuthorizationHeaderMalformed')

        data = await self.parse_request(request)

        if data is None:
            raise exceptions.S3Error('InvalidArgument')

        for header_name in tuple(data['headers']):
            for signed_header_name in auth['signed_headers']:
                if header_name.lower() == signed_header_name:
                    break
            else:
                data['headers'].pop(header_name)

        user = self.stack.get_user(auth['credential']['access_key'])

        signature = signer.create_signature \
        (
            access_key = auth['credential']['access_key'],
            secret_key = user.secret_key,
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
            raise exceptions.S3Error('SignatureDoesNotMatch')

        request.state.user = user

        response = await call_next(request)

        return response

class AwsAuthenticationMiddleware(BaseAwsAuthenticationSignatureMiddleware):
    async def dispatch(self, request, call_next):
        if self.stack.anonymous_access:
            request.state.user = None

            return await call_next(request)

        authorization = request.headers.get('Authorization')

        if authorization is None:
            raise exceptions.S3Error('AccessDenied')

        algorithm = authorization.strip().split()[0].upper()

        algorithm_version = algorithm.split('-', 1)[0]

        middleware = \
        {
            'AWS':  AwsAuthenticationSignatureV2Middleware,
            'AWS4': AwsAuthenticationSignatureV4Middleware,
        }

        if algorithm_version not in middleware:
            raise exceptions.S3Error('InvalidEncryptionAlgorithmError')

        return await middleware[algorithm_version](self.app, stack = self.stack).dispatch(request, call_next)
