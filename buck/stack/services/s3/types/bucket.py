from . import base

import string
import re


class BucketName(base.BaseType):
    @staticmethod
    def validate(value: str):
        # Rules for s3 bucket naming: (https://docs.aws.amazon.com/AmazonS3/latest/dev/BucketRestrictions.html#bucketnamingrules)
        #   * Bucket names must be between 3 and 63 characters long.
        #   * Bucket names can consist only of lowercase letters, numbers, dots (.), and hyphens (-).
        #   * Bucket names must begin and end with a letter or number.
        #   * Bucket names must not be formatted as an IP address (for example, 192.168.5.4).
        #   * Bucket names can't begin with xn-- (for buckets created after February 2020).

        len_min = 3
        len_max = 63
        acceptable_chars = f"{string.ascii_lowercase}{string.digits}.-"
        acceptable_end_chars = f"{string.ascii_lowercase}{string.digits}"
        unacceptable_formats = {
            "an IP address": r"(\d)\.(\d)\.(\d)\.(\d)",
        }
        unacceptable_starts = ("xn--",)

        if not len_min <= len(value) <= len_max:
            return f"must be between {len_min} and {len_max} characters long"

        for char in value:
            if char not in acceptable_chars:
                return f"can consist only of characters: {acceptable_chars!r}"

        for char in (value[0], value[-1]):
            if char not in acceptable_end_chars:
                return f"first and last char must be in: {acceptable_end_chars!r}"

        for format_name, format_pattern in unacceptable_formats.items():
            if re.match(format_pattern, value):
                return f"must not be formatted as {format_name}"

        for unacceptable_start in unacceptable_starts:
            if value.startswith(unacceptable_start):
                return f"can't begin with the character: {unacceptable_start!r}"
