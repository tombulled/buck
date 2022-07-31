from .... import constants
from ..types import RegionCode, RegionName
from . import base

from typing import Union


class Region(base.BaseModel):
    code: str
    name: str

    def __init__(
        self,
        code: Union[str, None] = None,
        name: Union[str, None] = None,
    ):
        if code is not None:
            code = RegionCode(code)
            name = RegionName(constants.REGIONS.get(code))
        elif name is not None:
            name = RegionName(name)
            code = RegionCode(constants.REGIONS.inverse.get(name))

        super().__init__(
            code=str(code),
            name=str(name),
        )

    def __repr__(self):
        return super().__repr__(
            {
                "code": self.code,
                "name": self.name,
            }
        )
