from . import constants

class S3Error(Exception):
    def __init__(self, code):
        error = constants.ERRORS[code]

        self.code = code
        self.description = error['description']
        self.status_code = error['status_code']

    def __str__(self):
        return f'[{self.code}] {self.description}'
