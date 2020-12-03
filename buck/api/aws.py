import re
import hashlib
import hmac
import urllib.parse
import collections

class AwsSignatureV4(object):
    @staticmethod
    def parse_authorization(authorization):
        authorization = authorization.strip()

        pattern = r'(?P<algorithm>.+)(?: +)Credential(?: *)=(?: *)(?P<credential>.*)(?: *),(?: *)SignedHeaders(?: *)=(?: *)(?P<signed_headers>.+)(?: *),(?: *)Signature(?: *)=(?: *)(?P<signature>.+)'

        match = re.match(pattern, authorization)

        if not match: return

        algorithm = match.group('algorithm')
        credential = match.group('credential')
        signed_headers = match.group('signed_headers')
        signature = match.group('signature')

        credential_scope = re.split(r'(?: *)/(?: *)', credential)

        if len(credential_scope) != 5: return

        access_key, date, aws_region, aws_service, aws_request = credential_scope

        signed_headers_list = re.split(r'(?: *);(?: *)', signed_headers)

        authorization_data = \
        {
            'algorithm': algorithm,
            'credential': \
            {
                'access_key': access_key,
                'date': date,
                'region': aws_region,
                'service': aws_service,
                'request': aws_request,
            },
            'signed_headers': signed_headers_list,
            'signature': signature,
        }

        return authorization_data

    @staticmethod
    def _sign(key, msg):
        return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()

    @classmethod
    def _get_signature_key(cls, *, secret_key, date_stamp, region, service, request):
        key_date    = cls._sign(f'AWS4{secret_key}'.encode('utf-8'), date_stamp)
        key_region  = cls._sign(key_date, region)
        key_service = cls._sign(key_region, service)
        key_signing = cls._sign(key_service, request)

        return key_signing

    @classmethod
    def create_signature \
            (
                cls,
                *,
                access_key,
                secret_key,
                date = None,
                service = 's3',
                region = 'us-east-1',
                algorithm = 'AWS4-HMAC-SHA256',
                request = 'aws4_request',
                parameters = {},
                headers = {},
                body = '',
                method = 'GET',
                uri = '/',
            ):
        if date is None:
            date = datetime.datetime.utcnow()

        date_stamp = date.strftime('%Y%m%d')
        amz_date = date.strftime('%Y%m%dT%H%M%SZ')

        canonical_querystring = urllib.parse.urlencode(collections.OrderedDict(sorted(parameters.items(), key = lambda item: item[0])))

        formatted_headers = \
        {
            key.lower(): headers.get(key).strip()
            for key in headers
        }

        ordered_headers = collections.OrderedDict(sorted(formatted_headers.items(), key = lambda item: item[0]))

        canonical_headers = '\n'.join \
        (
            f'{key}:{val}'
            for key, val in ordered_headers.items()
        ) + '\n'

        signed_headers = ';'.join(ordered_headers.keys())

        payload_hash = hashlib.sha256((body).encode('utf-8')).hexdigest()

        canonical_request = '\n'.join \
        ((
            method,
            uri,
            canonical_querystring,
            canonical_headers,
            signed_headers,
            payload_hash,
        ))

        credential_scope = '/'.join \
        ((
            date_stamp,
            region,
            service,
            request,
        ))

        string_to_sign = '\n'.join \
        ((
            algorithm,
            amz_date,
            credential_scope,
            hashlib.sha256(canonical_request.encode('utf-8')).hexdigest(),
        ))

        signing_key = cls._get_signature_key \
        (
            secret_key = secret_key,
            date_stamp = date_stamp,
            region = region,
            service = service,
            request = request,
        )

        signature = hmac.new(signing_key, string_to_sign.encode('utf-8'), hashlib.sha256).hexdigest()

        return signature

    @staticmethod
    def create_authorization \
            (
                *,
                access_key,
                signature,
                date = None,
                algorithm = 'AWS4-HMAC-SHA256',
                region = 'us-east-1',
                service = 's3',
                request = 'aws4_request',
                signed_headers = [],
            ):
        date_stamp = date.strftime('%Y%m%d')

        credential = '/'.join \
        ((
            date_stamp,
            region,
            service,
            request,
        ))

        signed_headers = ';'.join(signed_headers)

        return f'{algorithm} Credential={credential}, SignedHeaders={signed_headers}, Signature={signature}'
