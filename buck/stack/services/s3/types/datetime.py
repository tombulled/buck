import arrow
import datetime

class DateTime(arrow.Arrow, datetime.datetime):
    def __repr__(self):
        return f'<{self.__class__.__name__}: {self!s}>'

    def __str__(self):
        return self.isoformat()

    def isoformat(self):
        return f'{super().isoformat()}Z'
