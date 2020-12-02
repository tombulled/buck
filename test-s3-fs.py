from buck.s3 import S3Fs, S3Mem
from buck import stack

import fs

s = stack.Stack('buck')

s.add_service('s3', S3Mem)

user = s.add_user(name = 'bob')

sess = s.session(user)

s3 = sess.service('s3')

# s3 = S3(fs.open_fs('/tmp/buck-store'))
