from . import base

import string

class ObjectKey(base.BaseType):
    @staticmethod
    def validate(value: str):
        # Safe object key chars: (https://docs.aws.amazon.com/AmazonS3/latest/dev/UsingMetadata.html#object-key-guidelines-safe-characters)
        #     * Alphanumeric characters:
        #         * 0-9
        #         * a-z
        #         * A-Z
        #     * Special characters:
        #         * Forward slash (/)
        #         * Exclamation point (!)
        #         * Hyphen (-)
        #         * Underscore (_)
        #         * Period (.)
        #         * Asterisk (*)
        #         * Single quote (')
        #         * Open parenthesis (()
        #         * Close parenthesis ())

        value = str(value)

        acceptable_chars = f'{string.ascii_letters}{string.digits}/!-_.*\'()'

        for char in value:
            if char not in acceptable_chars:
                return f'Unsafe character: {char!r}'
