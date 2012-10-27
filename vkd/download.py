import urllib2
import os

from hurry.filesize import size, alternative

def download(url, target_dir, filename=None, title=None):
    filename = filename or url.split('/')[-1]
    file_name = os.path.join(target_dir, filename)
    u = urllib2.urlopen(url)

    meta = u.info()
    file_size = int(meta.getheaders("Content-Length")[0])
    print "%s (%s)" % ((title or url), filename)

    if os.path.exists(file_name):
        if os.path.getsize(file_name) == file_size:
            print '    Already downloaded'
            return
        else:
            os.unlink(file_name)

    f = open(file_name, 'wb')

    file_size_dl = 0
    block_sz = 8192
    while True:
        buffer = u.read(block_sz)
        if not buffer:
            break

        file_size_dl += len(buffer)
        f.write(buffer)
        status = r"%10s  [%3.2f%%]" % (size(file_size_dl, system=alternative), file_size_dl * 100. / file_size)
        status = status + chr(8)*(len(status)+1)
        print status,
    print
    f.close()