import fastapi
import xmltodict
import requests.structures

async def payload(request: fastapi.Request):
    return xmltodict.parse(await request.body())

def state(attr: str, default = None):
    def wrapper(request: fastapi.Request):
        return getattr(request.state, attr, default)

    return wrapper

def attr(name: str, default = None):
    def wrapper(request: fastapi.Request):
        return getattr(request.app, name, default)

    return wrapper

def header(name: str, default = None):
    def wrapper(request: fastapi.Request):
        return request.headers.get(name, default)

    return wrapper

def amz_header(name: str, default = None):
    return header(f'X-Amz-{name}', default)

def headers(request: fastapi.Request):
    return request.headers

def amz_headers(request: fastapi.Request):
    prefix = 'x-amz-'

    headers = {}

    for header_key in list(request.headers):
        header_val = request.headers[header_key]

        if header_key.lower().startswith(prefix):
            header_key = header_key[len(prefix):]

            headers[header_key] = header_val

    return requests.structures.CaseInsensitiveDict(headers)

def stack(request: fastapi.Request):
    return api.stack

def session(request: fastapi.Request):
    return state('session')(request)

def service(name):
    def wrapper(request: fastapi.Request):
        return session(request).service(name)

    return wrapper

def s3(request: fastapi.Request):
    return service('s3')(request)

def storage(request: fastapi.Request): # TEMP: DELETE ME
    return
