#! /usr/bin/env python
# vim: set fileencoding=utf-8

# Python 2 or 3

from __future__ import division, print_function, unicode_literals

from zlib import adler32, crc32
import base64


## {{{ http://code.activestate.com/recipes/577684/ (r18)
##
## http://code.activestate.com/recipes/577684-bloom-filter/
## Created by Raymond Hettinger on Wed, 4 May 2011 (MIT)
## Licensed under the MIT License:
## Copyright 2011 Raymond Hettinger
## 
## Permission is hereby granted, free of charge, to any person obtaining a copy
## of this software and associated documentation files (the "Software"), to deal
## in the Software without restriction, including without limitation the rights
## to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
## copies of the Software, and to permit persons to whom the Software is
## furnished to do so, subject to the following conditions:
## 
## The above copyright notice and this permission notice shall be included in
## all copies or substantial portions of the Software.
## 
## THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
## IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
## FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
## AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
## LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
## OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
## SOFTWARE.
##
## Copied from activestate.com 2012-05-20 by rdg
##
## Modified by Raymond D. Gardner
## Modifications are:
## Copyright © 2018 Raymond D. Gardner
## Modifications are licensed under the MIT License.

from random import Random


class BloomFilter:
    # http://en.wikipedia.org/wiki/Bloom_filter

    def __init__(self, num_bytes, num_probes, iterable=()):
        self.array = bytearray(num_bytes)
        self.num_probes = num_probes
        self.num_bins = num_bytes * 8
        self.update(iterable)

    def get_probes(self, key):
        random = Random(key).random
        return (int(random() * self.num_bins) for _ in range(self.num_probes))

    def update(self, keys):
        for key in keys:
            for i in self.get_probes(key):
                self.array[i//8] |= 2 ** (i%8)

    def __contains__(self, key):
        return all(self.array[i//8] & (2 ** (i%8)) for i in self.get_probes(key))


# Remainder of Hettinger's Activestate recipe elided by rdg ...

## Following modifications are:
## © 2018 Raymond D. Gardner
## Modifications are licensed under the MIT License.


# Multiply crc32() and adler32() "hashes" by primes chosen to reduce the number
# of false undercount/overcount filter hits for words in the CMU dictionary,
# and try to get those hits to be not-too-common words. This is done by trial
# and error, and needs to be redone if syllable_count_eng.py or the syllable
# dictionary (or the Bloom filter config) is changed.
# False undercount hits (6): algy ardella gourlay leamon petterson pseudonym
# False overcount hits (10): cama car damsel evaded macromedia quintela
#                                       semolina spohr wayne winokur
# But note that car, spohr, and wayne are still 1 (OK) after adjusting.
PRIME1 = 13
PRIME2 = 11


class BloomFilter2(BloomFilter):
    def __init__(self, num_bins, num_probes, iterable=()):
        num_bytes = (num_bins + 7) // 8
        self.array = bytearray(num_bytes)
        self.num_probes = num_probes
        self.num_bins = num_bins
        self.update(iterable)

    def get_probes(self, key):
        # FIXME TEMP for test/dev
        assert isinstance(key, unicode if str is bytes else str)
        key = key.encode('utf8')
        h = ((crc32(key) & 0xffffffff) * PRIME1) % self.num_bins
        # For use only with twin prime num_bins:
        # h2 = (adler32(key) & 0xffffffff) % (self.num_bins - 2) + 2
        h2 = ((adler32(key) & 0xffffffff) * PRIME2) % self.num_bins
        for _ in range(self.num_probes):
            yield h
            h -= h2
            if h < 0:
                h += self.num_bins

    def dump_filter(self, fp, filter_name):
        fp.write(b'\n%s = (%d, %d, """\\\n%s""")\n' %
                (filter_name.encode('ascii'), self.num_bins, self.num_probes,
                base64.b64encode(self.array)))

    def print_filter_stats(self, filter_name):
        num_bins_set = ''.join(format(x, '08b') for x in self.array).count('1')
        print('Bloom filter %s: num_probes: %d  num_bins: %d  '
                'num_bins_set: %d (density: %.2f%%)'
                % (filter_name, self.num_probes, self.num_bins, num_bins_set,
                100.0 * num_bins_set / self.num_bins))


def create_and_load_Bloom_filter(filtr):
    bf = BloomFilter2(filtr[0], filtr[1])
    bf.array = bytearray(base64.b64decode(filtr[2]))
    return bf
