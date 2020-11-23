from buck import storage
from pprint import pprint as pp

# s = storage.Storage('/tmp/buck-store')
s = storage.SimpleStorageService()

b = storage.FSBucket('/tmp/buck-store/hello')
