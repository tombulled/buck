import starlette.responses
import starlette.requests
import mimetypes
import xmltodict
import magic
import os
from typing import IO, Generator

class RangedStreamingResponse(starlette.responses.StreamingResponse):
    chunk_size = 8192

    def __init__(self, request: starlette.requests.Request, file: IO[bytes], **kwargs):
        if 'media_type' not in kwargs:
            kwargs['media_type'] = magic.from_buffer(file.read(2048), mime = True)

            file.seek(0)

        file_size = os.fstat(file.fileno()).st_size

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

    def __init__(self, root_node, *args, pretty=True, **kwargs):
        self.root_node = root_node
        self.pretty = pretty

        super().__init__(*args, **kwargs)

    def render(self, content: dict) -> bytes:
        data = \
        {
            self.root_node: \
            {
                '@xmlns': 'http://s3.amazonaws.com/doc/2006-03-01/',
                **content,
            },
        }

        xml = xmltodict.unparse(data, pretty = self.pretty)

        # Temp!
        print()
        print('Response:')
        print(xml)

        return xml.encode()

class AwsErrorResponse(AwsResponse):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('status_code', 404) # Just temporarily

        super().__init__('Error', *args, **kwargs)

    def render(self, content) -> bytes:
        return super().render \
        ({
            'Code': 'Some error code etc.'
        })
