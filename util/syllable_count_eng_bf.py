#! /usr/bin/env python
# vim: set fileencoding=utf-8

# Python 2 or 3

# TODO: handle encoding/decoding in main()

"""syllable_count_eng_bf.py -- count syllables in English word.

This version uses Bloom filters to fix up counts that the
basic version gets wrong.
"""

## Copyright © 2018 Raymond D. Gardner
## Licensed under the MIT License

from __future__ import division, print_function, unicode_literals

import syllable_count_eng
import Bloom_filter
from Bloom_filter_data import undercount_filter, overcount_filter


undercount_bf = Bloom_filter.create_and_load_Bloom_filter(undercount_filter)
overcount_bf = Bloom_filter.create_and_load_Bloom_filter(overcount_filter)


def syllable_count_eng_bf(word):
    n = syllable_count_eng.syllable_count_eng(word)
    word = word.lower()
    if word in undercount_bf:
        n += 1
    elif word in overcount_bf:
        n -= 1
    if n <= 0:
        n = 1
    return n


if __name__ == '__main__':
    import sys, io
    with io.open(sys.argv[1], encoding='utf8') as fp:
        for word in fp.read().split():
            k = syllable_count_eng_bf(word)
            print(k, word)
