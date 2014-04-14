# -*- coding: utf-8 -*-

"""Utility functions for creating memory-efficient generators.
"""

from json import JSONEncoder
from zlib import decompressobj, MAX_WBITS

def json_generator(obj):
    """Return generator that produces JSON strings for given obj.

    Example:
    >>> '|'.join(json_generator(dict(a=1,b=2)))
    '{|"a"|: |1|, |"b"|: |2|}'

    """
    for chunk in JSONEncoder().iterencode(obj):
        yield chunk


def gunzip_generator(fileobj, chunksize=1024):
    """Return generator for decompressing given file-like bytestream fileobj
    on the fly while using at most chunksize bytes in memory at a time.

    Example:
    >>> import zlib, StringIO
    >>> gzfile = StringIO.StringIO(zlib.compress('hello'))
    >>>
    >>> with open('test.txt.gz', 'rb') as gz:
    ...     [x for x in gunzip_generator(gz)]
    ['hello']

    """
    decoder = decompressobj(MAX_WBITS|32)

    while True:
        buffer = fileobj.read(chunksize)

        if not buffer:
            break

        yield decoder.decompress(buffer)

    lastchunk = decoder.flush()

    if lastchunk:
        yield lastchunk


def flat_string_generator(iterables, encoding='utf-8'):
    """Return generator which recursively produces flat strings in given
    encoding from given iterable object.

    Example:
    >>> [ x for x in flat_string_generator(['a', ['b', ['c', 'd']], u'e']) ]
    ['a', 'b', 'c', 'd', 'e']

    """

    for item in iterables:
        if isinstance(item, basestring):
            if isinstance(item, unicode):
                item = item.encode(encoding)
            yield item
        else: # it must be an iterable itself
            for subitem in flat_string_generator(item):
                yield subitem


if __name__ == "__main__":
    import doctest; doctest.testmod()

