import bidict

REGIONS = bidict.bidict \
({
    'us-east-1':      'US East (N. Virginia)',
    'us-east-2':      'US East (Ohio)',
    'us-west-1':      'US West (N. California)',
    'us-west-2':      'US West (Oregon)',
    'ca-central-1':   'Canada (Central)',
    'eu-central-1':   'Europe (Frankfurt)',
    'eu-north-1':     'Europe (Stockholm)',
    'eu-south-1':     'Europe (Milan)',
    'eu-west-1':      'Europe (Ireland)',
    'eu-west-2':      'Europe (London)',
    'eu-west-3':      'Europe (Paris)',
    'ap-east-1':      'Asia Pacific (Hong Kong)',
    'ap-northeast-1': 'Asia Pacific (Tokyo)',
    'ap-northeast-2': 'Asia Pacific (Seoul)',
    'ap-south-1':     'Asia Pacific (Mumbai)',
    'ap-southeast-1': 'Asia Pacific (Singapore)',
    'ap-southeast-2': 'Asia Pacific (Sydney)',
    'af-south-1':     'Africa (Cape Town)',
    'me-south-1':     'Middle East (Bahrain)',
    'sa-east-1':      'South America (Sao Paulo)',
})

ERRORS = \
{
    'AccessDenied': \
    {
        'description': 'Access Denied',
        'status_code': 403,
    },
    'AccountProblem': \
    {
        'description': \
        (
            'There is a problem with your AWS account that prevents the operation'
            ' from completing successfully'
        ),
        'status_code': 403,
    },
    'AllAccessDisabled': \
    {
        'description': 'All access to this Amazon S3 resource has been disabled',
        'status_code': 403,
    },
    'AmbiguousGrantByEmailAddress': \
    {
        'description': \
        (
            'The email address you provided is associated with more than'
            ' one account'
        ),
        'status_code': 400,
    },
    'AuthorizationHeaderMalformed': \
    {
        'description': 'The authorization header you provided is not valid',
        'status_code': 400,
    },
    'BadDigest': \
    {
        'description': \
        (
            'The Content-MD5 you specified did not match what we received'
        ),
        'status_code': 400,
    },
    'BucketAlreadyExists': \
    {
        'description': \
        (
            'The requested bucket name is not available. The bucket namespace is'
            ' shared by all users of the system. Select a different name and'
            ' try again.'
        ),
        'status_code': 409,
    },
    'BucketAlreadyOwnedByYou': \
    {
        'description': \
        (
            'The bucket you tried to create already exists, and you own it'
        ),
        'status_code': 409,
    },
    'BucketNotEmpty': \
    {
        'description': 'The bucket you tried to delete is not empty',
        'status_code': 409,
    },
    'CredentialsNotSupported': \
    {
        'description': 'This request does not support credentials',
        'status_code': 400,
    },
    'CrossLocationLoggingProhibited': \
    {
        'description': \
        (
            'Cross-location logging not allowed. Buckets in one geographic'
            ' location cannot log information to a bucket in another location.'
        ),
        'status_code': 403,
    },
    'EntityTooSmall': \
    {
        'description': \
        (
            'Your proposed upload is smaller than the minimum allowed object'
            ' size'
        ),
        'status_code': 400,
    },
    'EntityTooLarge': \
    {
        'description': \
        (
            'Your proposed upload exceeds the maximum allowed object size'
        ),
        'status_code': 400,
    },
    'ExpiredToken': \
    {
        'description': 'The provided token has expired',
        'status_code': 400,
    },
    'IllegalLocationConstraintException': \
    {
        'description': \
        (
            'You are trying to access a bucket from a different region than'
            ' where the bucket exists'
        ),
        'status_code': 400,
    },
    'IllegalVersioningConfigurationException': \
    {
        'description': \
        (
            'The versioning configuration specified in the request is invalid'
        ),
        'status_code': 400,
    },
    'IncompleteBody': \
    {
        'description': \
        (
            'You did not provide the number of bytes specified by the'
            ' Content-Length HTTP header'
        ),
        'status_code': 400,
    },
    'IncorrectNumberOfFilesInPostRequest': \
    {
        'description': 'POST requires exactly one file upload per request',
        'status_code': 400,
    },
    'InlineDataTooLarge': \
    {
        'description': 'Inline data exceeds the maximum allowed size',
        'status_code': 400,
    },
    'InternalError': \
    {
        'description': 'We encountered an internal error. Please try again.',
        'status_code': 500,
    },
    'InvalidAccessKeyId': \
    {
        'description': \
        (
            'The AWS access key ID you provided does not exist in our records'
        ),
        'status_code': 403,
    },
    'InvalidAccessPoint': \
    {
        'description': 'The specified access point name or account is not valid',
        'status_code': 400,
    },
    'InvalidAddressingHeader': \
    {
        'description': 'You must specify the Anonymous role',
        'status_code': None,
    },
    'InvalidArgument': \
    {
        'description': \
        (
            'This error might occur for the following reasons: The specified'
            ' argument was invalid, The request was missing a required header,'
            ' The specified argument was incomplete or in the wrong format, Must'
            ' have length greater than or equal to 3.'
        ),
        'status_code': 400,
    },
    'InvalidBucketName': \
    {
        'description': 'The specified bucket is not valid',
        'status_code': 400,
    },
    'InvalidBucketState': \
    {
        'description': \
        (
            'The request is not valid with the current state of the bucket'
        ),
        'status_code': 409,
    },
    'InvalidDigest': \
    {
        'description': 'The Content-MD5 you specified is not valid',
        'status_code': 400,
    },
    'InvalidEncryptionAlgorithmError': \
    {
        'description': 'The encryption request that you specified is not valid',
        'status_code': 400,
    },
    'InvalidLocationConstraint': \
    {
        'description': 'The specified location constraint is not valid',
        'status_code': 400,
    },
    'InvalidObjectState': \
    {
        'description': \
        (
            'The operation is not valid for the current state of the object'
        ),
        'status_code': 403,
    },
    'InvalidPart': \
    {
        'description': \
        (
            'One or more of the specified parts could not be found. The part'
            ' might not have been uploaded, or the specified entity tag might'
            ' not have matched the part\'s entity tag.'
        ),
        'status_code': 400,
    },
    'InvalidPartOrder': \
    {
        'description': \
        (
            'The list of parts was not in ascending order. Parts list must be'
            ' specified in order by part number'
        ),
        'status_code': 400,
    },
    'InvalidPayer': \
    {
        'description': 'All access to this object has been disabled',
        'status_code': 403,
    },
    'InvalidPolicyDocument': \
    {
        'description': \
        (
            'The content of the form does not meet the conditions specified in'
            ' the policy document'
        ),
        'status_code': 400,
    },
    'InvalidRange': \
    {
        'description': 'The requested range cannot be satisfied',
        'status_code': 416,
    },
    'InvalidRequest': \
    {
        'description': 'The request was invalid',
        'status_code': 400,
    },
    'InvalidSecurity': \
    {
        'description': 'The provided security credentials are not valid',
        'status_code': 403,
    },
    'InvalidSOAPRequest': \
    {
        'description': 'The SOAP request body is invalid',
        'status_code': 400,
    },
    'InvalidStorageClass': \
    {
        'description': 'The storage class you specified is not valid',
        'status_code': 400,
    },
    'InvalidTargetBucketForLogging': \
    {
        'description': \
        (
            'The target bucket for logging does not exist, is not owned by you,'
            ' or does not have the appropriate grants for the log-delivery group'
        ),
        'status_code': 400,
    },
    'InvalidToken': \
    {
        'description': 'The provided token is malformed or otherwise invalid',
        'status_code': 400,
    },
    'InvalidURI': \
    {
        'description': 'Couldn\'t parse the specified URI',
        'status_code': 400,
    },
    'KeyTooLongError': \
    {
        'description': 'Your key is too long',
        'status_code': 400,
    },
    'MalformedACLError': \
    {
        'description': \
        (
            'The XML you provided was not well formed or did not validate'
            ' against our published schema'
        ),
        'status_code': 400,
    },
    'MalformedPOSTRequest': \
    {
        'description': \
        (
            'The body of your POST request is not well-formed'
            ' multipart/form-data'
        ),
        'status_code': 400,
    },
    'MalformedXML': \
    {
        'description': \
        (
            'The XML you provided was not well formed or did not validate'
            ' against our published schema'
        ),
        'status_code': 400,
    },
    'MaxMessageLengthExceeded': \
    {
        'description': 'Your request was too big',
        'status_code': 400,
    },
    'MaxPostPreDataLengthExceededError': \
    {
        'description': \
        (
            'Your POST request fields preceding the upload file were too large'
        ),
        'status_code': 400,
    },
    'MetadataTooLarge': \
    {
        'description': \
        (
            'Your metadata headers exceed the maximum allowed metadata size'
        ),
        'status_code': 400,
    },
    'MethodNotAllowed': \
    {
        'description': 'The specified method is not allowed against this resource',
        'status_code': 405,
    },
    'MissingAttachment': \
    {
        'description': 'A SOAP attachment was expected, but none were found',
        'status_code': None,
    },
    'MissingContentLength': \
    {
        'description': 'You must provide the Content-Length HTTP header',
        'status_code': 411,
    },
    'MissingRequestBodyError': \
    {
        'description': 'Request body is empty',
        'status_code': 400,
    },
    'MissingSecurityElement': \
    {
        'description': 'The SOAP 1.1 request is missing a security element',
        'status_code': 400,
    },
    'MissingSecurityHeader': \
    {
        'description': 'Your request is missing a required header',
        'status_code': 400,
    },
    'NoLoggingStatusForKey': \
    {
        'description': \
        (
            'There is no such thing as a logging status subresource for a key'
        ),
        'status_code': 400,
    },
    'NoSuchBucket': \
    {
        'description': 'The specified bucket does not exist',
        'status_code': 404,
    },
    'NoSuchBucketPolicy': \
    {
        'description': 'The specified bucket does not have a bucket policy',
        'status_code': 404,
    },
    'NoSuchKey': \
    {
        'description': 'The specified key does not exist',
        'status_code': 404,
    },
    'NoSuchLifecycleConfiguration': \
    {
        'description': 'The lifecycle configuration does not exist',
        'status_code': 404,
    },
    'NoSuchUpload': \
    {
        'description': \
        (
            'The specified multipart upload does not exist. The upload ID might'
            ' be invalid, or the multipart upload might have been aborted or'
            ' completed.'
        ),
        'status_code': 404,
    },
    'NoSuchVersion': \
    {
        'description': \
        (
            'The version ID specified in the request does not match an existing'
            ' version'
        ),
        'status_code': 404,
    },
    'NotImplemented': \
    {
        'description': \
        (
            'A header you provided implies functionality that is not implemented'
        ),
        'status_code': 501,
    },
    'NotSignedUp': \
    {
        'description': \
        (
            'Your account is not signed up for the Amazon S3 service. You must'
            ' signup before you can use Amazon S3.'
        ),
        'status_code': 403,
    },
    'OperationAborted': \
    {
        'description': \
        (
            'A conflicting conditional operation is currently in progress'
            ' against this resource. Try again.'
        ),
        'status_code': 409,
    },
    'PermanentRedirect': \
    {
        'description': \
        (
            'The bucket you are attempting to access must be addressed using'
            ' the specified endpoint. Send all future requests to this endpoint.'
        ),
        'status_code': 301,
    },
    'PreconditionFailed': \
    {
        'description': 'At least one of the preconditions you specified did not hold',
        'status_code': 412,
    },
    'Redirect': \
    {
        'description': 'Temporary redirect',
        'status_code': 307,
    },
    'RestoreAlreadyInProgress': \
    {
        'description': 'Object restore is already in progress',
        'status_code': 409,
    },
    'RequestIsNotMultiPartContent': \
    {
        'description': \
        (
            'Bucket POST must be of the enclosure-type multipart/form-data'
        ),
        'status_code': 400,
    },
    'RequestTimeout': \
    {
        'description': \
        (
            'Your socket connection to the server was not read from or written'
            ' to within the timeout period'
        ),
        'status_code': 400,
    },
    'RequestTimeTooSkewed': \
    {
        'description': \
        (
            'The difference between the request time and the server\'s'
            ' time is too large'
        ),
        'status_code': 403,
    },
    'RequestTorrentOfBucketError': \
    {
        'description': 'Requesting the torrent file of a bucket is not permitted',
        'status_code': 400,
    },
    'ServerSideEncryptionConfigurationNotFoundError': \
    {
        'description': 'The server-side encryption configuration was not found',
        'status_code': 400,
    },
    'ServiceUnavailable': \
    {
        'description': 'Reduce your request rate',
        'status_code': 503,
    },
    'SignatureDoesNotMatch': \
    {
        'description': \
        (
            'The request signature that we calculated does not match the'
            ' signature you provided. Check your AWS secret access key and'
            ' signing method.'
        ),
        'status_code': 403,
    },
    'SlowDown': \
    {
        'description': 'Reduce your request rate',
        'status_code': 503,
    },
    'TemporaryRedirect': \
    {
        'description': 'You are being redirected to the bucket while DNS updates',
        'status_code': 307,
    },
    'TokenRefreshRequired': \
    {
        'description': 'The provided token must be refreshed',
        'status_code': 400,
    },
    'TooManyAccessPoints': \
    {
        'description': 'You have attempted to create more access point than allowed',
        'status_code': 400,
    },
    'TooManyBuckets': \
    {
        'description': 'You have attempted to create more buckets than allowed',
        'status_code': 400,
    },
    'UnexpectedContent': \
    {
        'description': 'This request does not support content',
        'status_code': 400,
    },
    'UnresolvableGrantByEmailAddress': \
    {
        'description': \
        (
            'The email address you provided does not match any account on record'
        ),
        'status_code': 400,
    },
    'UserKeyMustBeSpecified': \
    {
        'description': \
        (
            'The bucket POST must contain the specified field name. If it is'
            ' specified, check the order of the fields.'
        ),
        'status_code': 400,
    },
    'NoSuchAccessPoint': \
    {
        'description': 'The specified access point does not exist',
        'status_code': 400,
    },
    'InvalidTag': \
    {
        'description': \
        (
            'You have passed bad tag input - duplicate keys, key/values are too'
            ' long, system tags were sent.'
        ),
        'status_code': 400,
    },
    'MalformedPolicy': \
    {
        'description': 'You have an invalid principal in policy',
        'status_code': 400,
    },
}
