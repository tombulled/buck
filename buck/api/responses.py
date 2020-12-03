import starlette.responses
import starlette.requests
import mimetypes
import xmltodict
import magic
import os
from typing import IO, Generator
import io

class Response(starlette.responses.Response): pass

class StatusResponse(starlette.responses.Response):
    def __init__(self, **kwargs):
        status_code = kwargs.get('content')

        super().__init__(status_code = status_code)

    def render(self, content: dict) -> bytes:
        return b''

class RedirectResponse(starlette.responses.RedirectResponse):
    def __init__(self, **kwargs):
        url = kwargs.get('content')

        super().__init__(url, status_code = 307)

    def render(self, content: dict) -> bytes:
        return b''

class RangedStreamingResponse(starlette.responses.StreamingResponse):
    chunk_size = 8192

    def __init__(self, request: starlette.requests.Request, file: IO[bytes], **kwargs):
        if 'media_type' not in kwargs:
            kwargs['media_type'] = magic.from_buffer(file.read(2048), mime = True)

            file.seek(0)

        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0, os.SEEK_SET)

        content_range = request.headers.get('range')

        content_length = file_size
        status_code = 200
        headers = {}

        if content_range is not None:
            content_range = content_range.strip().lower()

            content_ranges = content_range.split('=')[-1]

            range_start, range_end, *_ = map(str.strip, (content_ranges + '-').split('-'))

            range_start = max(0, int(range_start)) if range_start else 0
            range_end   = min(file_size - 1, int(range_end)) if range_end else file_size - 1

            content_length = (range_end - range_start) + 1

            file = self.ranged(file, start = range_start, end = range_end + 1)

            status_code = 206

            headers['Content-Range'] = f'bytes {range_start}-{range_end}/{file_size}'

        kwargs['status_code'] = status_code

        super().__init__(file, **kwargs)

        self.headers.update \
        ({
            'Accept-Ranges': 'bytes',
            'Content-Length': str(content_length),
            **headers,
        })

    @staticmethod
    def ranged \
            (
                file: IO[bytes],
                start: int = 0,
                end: int = None,
                block_size: int = 8192,
            ) -> Generator[bytes, None, None]:
        consumed = 0

        file.seek(start)

        while True:
            data_length = min(block_size, end - start - consumed) if end else block_size

            if data_length <= 0:
                break

            data = file.read(data_length)

            if not data:
                break

            consumed += data_length

            yield data

        if hasattr(file, 'close'):
            file.close()

class AwsResponse(starlette.responses.Response):
    media_type = mimetypes.types_map['.xml']

    def render(self, content: dict) -> bytes:
        root_node = next(iter(content))

        content[root_node]['@xmlns'] = 'http://s3.amazonaws.com/doc/2006-03-01/'

        xml = xmltodict.unparse(content, pretty = True)

        return xml.encode()

class AwsErrorResponse(AwsResponse): # TODO: Update me!
    # def __init__(self, *args, **kwargs):
        # print('raising aws error response')

        # super().__init__('Error', *args, **kwargs)

    def render(self, error: dict) -> bytes:
        return super().render \
        ({
            'Error': \
            {
                'Code':      error.get('code', ''),
                'Message':   error.get('message', ''),
                'Resource':  '', # Temp
                'RequestId': '', # Temp
            },
        })
