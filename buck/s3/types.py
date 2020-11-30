from .. import exceptions
from .. import constants

from . import entities

import collections
import string
import re
import datetime

class S3Type(collections.UserString):
    def __init__(self, value: str):
        error_message = self.validate(value)

        if error_message is not None:
            class_name = self.__class__.__name__
            sep = ' - ' if error_message else ''

            raise ValueError(f'Invalid {class_name}{sep}{error_message}')

        super().__init__(value)

    @staticmethod
    def validate(value: str):
        return

class RegionName(S3Type):
    @staticmethod
    def validate(value: str):
        value = str(value)

        if value not in constants.REGIONS.inverse:
            return repr(value)

class RegionCode(S3Type):
    @staticmethod
    def validate(value: str):
        value = str(value)

        if value not in constants.REGIONS:
            return repr(value)

class BucketName(S3Type):
    @staticmethod
    def validate(value: str):
        # Rules for s3 bucket naming: (https://docs.aws.amazon.com/AmazonS3/latest/dev/BucketRestrictions.html#bucketnamingrules)
        #   * Bucket names must be between 3 and 63 characters long.
        #   * Bucket names can consist only of lowercase letters, numbers, dots (.), and hyphens (-).
        #   * Bucket names must begin and end with a letter or number.
        #   * Bucket names must not be formatted as an IP address (for example, 192.168.5.4).
        #   * Bucket names can't begin with xn-- (for buckets created after February 2020).

        # print('BucketName.validate', repr(value))
        value = str(value)

        len_min = 3
        len_max = 63
        acceptable_chars = f'{string.ascii_lowercase}{string.digits}.-'
        acceptable_end_chars = f'{string.ascii_lowercase}{string.digits}'
        unacceptable_formats = \
        {
            'an IP address': r'(\d)\.(\d)\.(\d)\.(\d)',
        }
        unacceptable_starts = ('xn--',)

        if not len_min <= len(value) <= len_max:
            return f'must be between {len_min} and {len_max} characters long'

        for char in value:
            if char not in acceptable_chars:
                return f'can consist only of characters: {acceptable_chars!r}'

        for char in (value[0], value[-1]):
            if char not in acceptable_end_chars:
                return f'first and last char must be in: {acceptable_end_chars!r}'

        for format_name, format_pattern in unacceptable_formats.items():
            if re.match(format_pattern, value):
                return f'must not be formatted as {format_name}'

        for unacceptable_start in unacceptable_starts:
            if value.startswith(unacceptable_start):
                return f'can\'t begin with the character: {unacceptable_start!r}'

        return

class ObjectKey(S3Type):
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
