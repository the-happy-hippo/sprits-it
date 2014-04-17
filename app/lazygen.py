# -*- coding: utf-8 -*-

"""Utility functions for creating memory-efficient generators.

In this module, *string generator* denotes any python generator or iterator
that yields string objects when calling ``next()``.
"""

from sys import maxsize
from json import JSONEncoder
from zlib import compressobj, decompressobj, MAX_WBITS
from gzip import GzipFile
from StringIO import StringIO

def json_generator(obj):
    """Return generator that produces JSON strings for given obj.

    Example::

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

def deflate_generator(string_generator):
    """Return generator for compressing given string generator with zlib.

    Example:

        >>> import zlib
        >>> z = ''.join(deflate_generator(iter(['hello,', ' ', 'world!'])))
        >>> zlib.decompress(z)
        'hello, world!'

    """
    encoder = compressobj()

    for string in string_generator:
        yield encoder.compress(string)

    yield encoder.flush()

def gzip_generator(string_generator):
    """Return generator for gzipping given string generator.

    Example:

        >>> import StringIO
        >>> z = ''.join(gzip_generator(iter(['hello,', ' ', 'world!'])))
        >>> ''.join(gunzip_generator(StringIO.StringIO(z)))
        'hello, world!'

    """
    # Use gzip and not zlib to make proper gzip header.
    buffer = StringIO()
    gzip = GzipFile(fileobj=buffer, mode='w')

    # Yield header
    yield buffer.getvalue()
    buffer.truncate(0)

    for string in string_generator:

        gzip.write(string)
        gzip.flush()

        yield buffer.getvalue()
        buffer.truncate(0)

    # Flush
    gzip.close()

    yield buffer.getvalue()

def compression_generator(string_generator, method):
    """Return generator for deflating/gzipping given string generator.
    ``method`` can be either ``'deflate'`` or ``'gzip'``.
    """
    if method == 'deflate':
        return deflate_generator(string_generator)
    elif method == 'gzip':
        return gzip_generator(string_generator)
    else:
        raise ValueError('Invalid compression method "%s"' % method)

def flat_string_generator(iterables, encoding='utf-8'):
    """Return generator which recursively produces flat strings in given
    encoding from given iterable object.

    Example::

        >>> [ x for x in flat_string_generator(['a', ['b', ['c', 'd']], u'e'])]
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
    """Create a file-like stream created from string generator.

    Example::

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
        """Read at most ``n`` bytes from the file (less if the ```read``` hits
        end-of-file before obtaining size bytes).

        If ``n`` argument is negative or omitted, read all data until end of
        file is reached. The bytes are returned as a string object. An empty
        string is returned when end of file is encountered immediately.
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

