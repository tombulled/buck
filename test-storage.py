from buck import stack
from buck.s3 import entities
from pprint import pprint as pp

d = entities.Date()
r = entities.Region('us-east-2')
b = entities.Bucket('bucket')
o = entities.Object('a/b', bucket)
