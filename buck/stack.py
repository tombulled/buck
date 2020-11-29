"""
Anyone can access service, but limits start from bucket

access control: bucket policy, bucket acl, object acl
"""

import secrets
import hashlib

# utils
def md5(data):
    return hashlib.md5(str(data).encode()).hexdigest()

class StackUser(object):
    def __init__(self, access_key, secret_key, name, id):
        self.access_key = access_key
        self.secret_key = secret_key
        self.name = name
        self.id = id

    def __repr__(self):
        return f'<StackUser: name={self.name!r}>'

    def __iter__(self):
        return (item for item in self.__dict__.items())

class StackService(object):
    def __init__(self, name, session):
        self.name = name
        self.session = session

    def __repr__(self):
        return f'<StackService: name={self.name!r} stack={self.session.stack.name!r}>'

class StackSession(object):
    def __init__(self, stack, user):
        self.stack = stack
        self.user = user

    def __repr__(self):
        return f'<StackSession: stack={self.stack.name!r} user={self.user.name!r}>'

    def service(self, name, *args, **kwargs):
        return self.stack.get_service(name)(name, self, *args, **kwargs)

class Stack(object):
    __ticker = 0
    __users = {}
    __services = {}
    name = None

    def __init__(self, name = 'stack'):
        self.name = name

    def __repr__(self):
        stack_name = self.name
        total_users = len(self.__users)
        total_services = len(self.__services)

        return f'<Stack: name={stack_name!r} users={total_users} services={total_services}>'

    @staticmethod
    def _gen_key():
        return secrets.token_hex(15)

    def _gen_access_key(self):
        while True:
            access_key = self._gen_key()

            if access_key not in self.__users:
                return access_key

    def _gen_user_id(self):
        return self._hash()

    def _gen_user_name(self):
        return f'User-{self._hash()[-5:]}'

    def _tick(self):
        self.__ticker += 1

        return self.__ticker

    def _hash(self):
        return md5(self._tick())

    def get_user(self, access_key):
        return self.__users.get(access_key)

    def add_user(self, name = None): # Check if already exists etc.
        user_data = \
        {
            'name': name or self._gen_user_name(),
            'access_key': self._gen_access_key(),
            'secret_key': self._gen_key(),
            'id': self._gen_user_id(),
        }

        user = StackUser(**user_data)

        self.__users[user.access_key] = user

        return user

    def add_service(self, name, cls):
        self.__services[name] = cls

    def head_service(self, name):
        return name in self.__services

    def delete_service(self, name):
        if self.head_service(name):
            del self.__services[name]

    def list_services(self):
        for service_name, service_cls in self.__services.items():
            service_data = \
            {
                'name': service_name,
                'class': service_cls,
            }

            yield service_data

    def get_service(self, name):
        return self.__services.get(name)

    def list_users(self):
        for user in self.__users.values():
            yield user

    def delete_user(self, access_key):
        if self.head_user(access_key):
            del self.__users[access_key]

    def head_user(self, access_key):
        return access_key in self.__users

    def session(self, user):
        return StackSession(self, user)
