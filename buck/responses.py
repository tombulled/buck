import starlette.responses
import mimetypes
import xmltodict

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

        return xml.encode()

class AwsErrorResponse(AwsResponse):
    def __init__(self, *args, **kwargs):
        super().__init__('Error', *args, **kwargs)

    def render(self, content) -> bytes:
        return super().render \
        ({
            'Code': 'Some error code etc.'
        })
