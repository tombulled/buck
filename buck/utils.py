def iso_datetime(dt):
    return dt.isoformat() + 'Z'

def generator(iterable):
    for item in iterable:
        yield item
