import arrow

class DateTime(arrow.Arrow):
    def __str__(self):
        return super().__str__() + 'Z'
