from ..types import BucketName, DateTime
# from ..types import BucketName
# from .datetime import DateTime
from .region import Region
from . import base
# from . import validation
from ....user import StackUser
from typing import Union

import datetime

class Bucket(base.BaseModel):
    name: str
    region: Region
    arn: str
    creation_date: DateTime
    owner: Union[StackUser, None]

    # @validation.validate_arguments
    def __init__ \
            (
                self,
                name: str,
                region: Region,
                creation_date: datetime.datetime,
                owner: Union[StackUser, None],
            ):
        super().__init__ \
        (
            name          = str(BucketName(name)),
            region        = region,
            arn           = f'arn:aws:s3::{name!s}',
            creation_date = DateTime.fromdatetime(creation_date),
            owner         = owner,
        )

    def __repr__(self):
        return super().__repr__ \
        (
            name   = self.name,
            region = self.region.code,
            owner  = self.owner.name
        )
