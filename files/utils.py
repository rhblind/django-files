# -*- coding: utf-8 -*-

import hashlib


def md5buffer(f, chunksize=65536):
    """
    Simple buffer to calculate the md5 hash of
    a file by reading the file in chunks of the
    specified size. Defaults to 64 KB.
    """
    md5 = hashlib.md5()
    f.seek(0)
    while True:
        c = f.read(chunksize)
        if not c:
            break
        md5.update(c)
    f.seek(0)
    return u"%s" % md5.hexdigest()
