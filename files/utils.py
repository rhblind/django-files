# -*- coding: utf-8 -*-

import hashlib
from StringIO import StringIO


def read_buffer(f, chunksize=65536):
    """
    Simple file reading buffer. Defaults to
    64 KB chunk size.
    """
    while True:
        c = f.read(chunksize)
        if not c:
            break
        yield c
        

def md5buffer(buf, chunksize=65536):
    """
    Simple buffer to calculate the md5 hash of
    a file by reading the file in chunks of the
    specified size. Defaults to 64 KB.
    """
    md5 = hashlib.md5()
    f = StringIO(buf)
    while True:
        c = f.read(chunksize)
        if not c:
            break
        md5.update(c)
    return u"%s" % md5.hexdigest()
