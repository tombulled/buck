from .... import constants
from . import base

class RegionName(base.BaseType):
    @staticmethod
    def validate(value: str):
        value = str(value)

        if value not in constants.REGIONS.inverse:
            return repr(value)

class RegionCode(base.BaseType):
    @staticmethod
    def validate(value: str):
        value = str(value)

        if value not in constants.REGIONS:
            return repr(value)
