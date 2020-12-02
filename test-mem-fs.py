# import fs.memoryfs
# import fs.osfs.OSFS
import fs

# mem_fs = fs.memoryfs.MemoryFS()
# os_fs = fs.osfs.OSFS('/tmp')

mem_fs = fs.open_fs('mem://')
os_fs = fs.open_fs('/tmp')
