# -*- coding: utf-8 -*-

"""Utility functions for creating memory-efficient generators.
"""
from sys import maxsize
from json import JSONEncoder
from zlib import decompressobj, MAX_WBITS
from StringIO import StringIO

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
    >>> [x for x in gunzip_generator(gzfile)]
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

class StringGenStream:
    """File-like stream created from string generator.

    Example:
    >>> stream = StringGenStream(iter(['hello', ',', ' ', 'world']))
    >>> print stream.read(3)
    hel
    >>> print stream.read()
    lo, world
    """

    def __init__(self, string_generator):
        self._string_generator = string_generator
        self._accumulator = None

    def read(self, n=-1):
        """Read at most size bytes from the file (less if the read hits EOF
        before obtaining size bytes).

        If the size argument is negative or omitted, read all data until
        EOF is reached. The bytes are returned as a string object. An empty
        string is returned when EOF is encountered immediately.
        """
        if self._accumulator is None:
            self._accumulator = StringIO()

        if n is None or n < 0: # exhaustive read
            n = maxsize

        buffer = []

        while n > 0:
            nextstr = self._accumulator.read(n)

            if nextstr:
                buffer.append(nextstr)
                n = n - len(nextstr)
            else:
                # accumulator exhausted, generate next string
                try:
                    nextstr = next(self._string_generator)
                    self._accumulator = StringIO(nextstr)
                except StopIteration:
                    n = 0 # stop

        return ''.join(buffer)

if __name__ == "__main__":
    import doctest; doctest.testmod()

