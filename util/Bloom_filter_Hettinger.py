#! /usr/bin/env python2
# vim: set fileencoding=utf-8

## {{{ http://code.activestate.com/recipes/577684/ (r18)
##
## http://code.activestate.com/recipes/577684-bloom-filter/
## Created by Raymond Hettinger on Wed, 4 May 2011 (MIT)
## Copyright 2011 Raymond Hettinger
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
## See R. Hettinger's description after end of code.
##

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


##  Sample application  ##############################################

class SpellChecker(BloomFilter):

    def __init__(self, wordlistfiles, estimated_word_count=125000):
        num_probes = 14           # set higher for fewer false positives
        num_bytes = estimated_word_count * num_probes * 3 // 2 // 8
        wordlist = (w.strip() for f in wordlistfiles for w in open(f))
        BloomFilter.__init__(self, num_bytes, num_probes, wordlist)

    def find_misspellings(self, text):
        return [word for word in text.lower().split() if word not in self]


## Example of subclassing with faster probe functions ################

from hashlib import sha224, sha256

class BloomFilter_4k(BloomFilter):
    # 4Kb (2**15 bins) 13 probes. Holds 1,700 entries with 1 error per 10,000.

    def __init__(self, iterable=()):
        BloomFilter.__init__(self, 4 * 1024, 13, iterable)

    def get_probes(self, key):
        h = int(sha224(key.encode()).hexdigest(), 16)
        for _ in range(13):
            yield h & 32767     # 2 ** 15 - 1
            h >>= 15

class BloomFilter_32k(BloomFilter):
    # 32kb (2**18 bins), 13 probes. Holds 13,600 entries with 1 error per 10,000.

    def __init__(self, iterable=()):
        BloomFilter.__init__(self, 32 * 1024, 13, iterable)

    def get_probes(self, key):
        h = int(sha256(key.encode()).hexdigest(), 16)
        for _ in range(13):
            yield h & 262143    # 2 ** 18 - 1
            h >>= 18


if __name__ == '__main__':

    ## Compute effectiveness statistics for a 125 byte filter with 50 entries

    from random import sample
    from string import ascii_letters

    states = '''Alabama Alaska Arizona Arkansas California Colorado Connecticut
        Delaware Florida Georgia Hawaii Idaho Illinois Indiana Iowa Kansas
        Kentucky Louisiana Maine Maryland Massachusetts Michigan Minnesota
        Mississippi Missouri Montana Nebraska Nevada NewHampshire NewJersey
        NewMexico NewYork NorthCarolina NorthDakota Ohio Oklahoma Oregon
        Pennsylvania RhodeIsland SouthCarolina SouthDakota Tennessee Texas Utah
        Vermont Virginia Washington WestVirginia Wisconsin Wyoming'''.split()

    bf = BloomFilter(num_bytes=125, num_probes=14, iterable=states)

    m = sum(state in bf for state in states)
    print('%d true positives and %d false negatives out of %d positive trials'
          % (m, len(states)-m, len(states)))

    trials = 100000
    m = sum(''.join(sample(ascii_letters, 8)) in bf for i in range(trials))
    print('%d true negatives and %d false positives out of %d negative trials'
          % (trials-m, m, trials))

    c = ''.join(format(x, '08b') for x in bf.array)
    print('Bit density:', c.count('1') / float(len(c)))


    ## Demonstrate a simple spell checker using a 125,000 word English wordlist

    from glob import glob
    from pprint import pprint

    # Use the GNU ispell wordlist found at http://bit.ly/english_dictionary
    checker = SpellChecker(glob('/Users/raymondhettinger/dictionary/english.?'))
    pprint(checker.find_misspellings('''
        All the werldz a stage
        And all the mehn and wwomen merrely players
        They have their exits and their entrances
        And one man in his thaim pllays many parts
        His actts being sevven ages
    '''))
## end of http://code.activestate.com/recipes/577684/ }}}

# DESCRIPTION by R. Hettinger + 1 comment:
#
# The get_probes() method generates a series of hashed lookups into the
# bitarray. There are many ways to do this and it is possible to get a much
# faster hashing function. The seeded random number generator approach was
# chosen for this recipe because 1) it produces as many uncorrelated bits as
# needed, 2) it is easy to understand, and 3) it works in both Python2 and
# Python3.
#
# The example code shows the names of fifty US states stored in a 125-byte
# bloom filter using 14 probes. We verify that all 50 are found in the filter
# (guaranteed True Positives). We then try 100,000 random strings to see if
# they are in the filter. Typically, only a handful return a false positive.
#
# Bloom filters are much more impressive with larger datasets. The above
# example also shows a list of all correctly spelled words in the English
# language compressed into a 330Kb bloom filter so that the spell checker can
# be kept entirely in memory.
#
# For those interested in boosting performance, the above code includes
# example of BloomFilter subclasses with fast customized get_probes() methods.
# The first hardwires a 4Kb array, using 13 probes generated by the fast
# sha224 function. It performs well for up to 1,700 keys while keeping the
# false positive rate under 1 in 10,000. The second is a larger 32Kb array
# with 13 probes generated by sha256. It can hold up to 13,600 keys while
# keeping the false positive rate under 1 in 10,000. These arrays are compact
# enough to fit entirely in the L1 or L2 caches on modern processors (for
# example the Intel Sandy Bridge processors have a 32Kb L1 data cache and a
# 256Kb L2 cache).
#
# The customized get_probes() methods can be further sped-up with traditional
# Python optimization techniques -- localize the global lookup of sha256()
# function, localize the builtin lookup for int(), and replace the range(13)
# call with a precomputed constant (or unroll the loop entirely):
#
# def get_probes(self, key, sha256=sha256, int=int, range13=tuple(range(13))):
#     h = int(sha256(key.encode()).hexdigest(), 16)
#     for _ in range13:
#         yield h & 262143    # 2 ** 18 - 1
#         h >>= 18
#
# 1 comment
# Manuel Garcia (approx. May 2011):
# Very minor point for the paranoid, if the keys are mostly sequential:
# cryptohash_digest(key) :: from a python standard library cryptographic hash
# random = Random(cryptohash_digest(key)).random
#
#### END
