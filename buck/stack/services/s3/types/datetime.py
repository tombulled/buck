import arrow
import datetime


class DateTime(arrow.Arrow, datetime.datetime):
    def __repr__(self):
        return f"<{self.__class__.__name__}: {self!s}>"
