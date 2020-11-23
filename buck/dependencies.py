import fastapi
import xmltodict
import requests.structures

import hashlib

class User(object):
    def __init__(self, access_key):
        self.access_key = access_key

    @property
    def id(self) -> str:
        if self.access_key:
            return hashlib.md5(self.access_key.encode()).hexdigest()

        return ''

    @property
    def display_name(self) -> str:
        if self.access_key:
            return self.access_key

        return ''

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

def storage(request: fastapi.Request):
    return attr('storage')(request)

def user(request: fastapi.Request):
    access_key = state('access_key')(request)

    if access_key:
        return User(access_key)

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
