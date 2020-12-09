from . import utils
from . import user

import secrets

class Stack(object):
    __ticker = 0
    __users = {}
    __services = {}

    name = None
    anonymous_access = False

    def __init__(self, name = 'stack', *, anonymous_access: bool = False):
        self.name = name
        self.anonymous_access = anonymous_access

    def __repr__(self):
        stack_name = self.name
        total_users = len(self.__users)
        total_services = len(self.__services)

        return f'<Stack: name={stack_name!r} users={total_users} services={total_services}>'

    @staticmethod
    def _gen_key():
        return utils.hex_token(15)

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
        return utils.md5(self._tick())

    def get_user(self, access_key):
        return self.__users.get(access_key)

    def add_user(self, **kwargs): # Check if already exists etc.
        kwargs = \
        {
            'name': self._gen_user_name(),
            'access_key': self._gen_access_key(),
            'secret_key': self._gen_key(),
            'id': self._gen_user_id(),
            **kwargs,
        }

        stack_user = user.StackUser(**kwargs)

        self.__users[stack_user.access_key] = stack_user

        return stack_user

    def add_service(self, service):
        self.__services[service.name] = service

    def head_service(self, name):
        return name in self.__services

    def delete_service(self, name):
        if self.head_service(name):
            del self.__services[name]

    def list_services(self):
        for service in self.__services.values():
            yield service

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

    def service(self, name: str, user: user.StackUser = None):
        return self.__services.get(name).session(user)

    # def session(self, user: user.StackUser = None):
    #     return session.StackSession \
    #     (
    #         stack = self,
    #         user  = user,
    #     )
