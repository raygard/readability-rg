#! /usr/bin/env python
# vim: set fileencoding=utf-8

# Python 2 or 3


"""syllable_count_eng.py -- count syllables in English word.

"""

## Copyright © 2018 Raymond D. Gardner
## Licensed under the MIT License

## Modelled on Greg Fast's Perl code syllable.pl (Lingua::EN::Syllable).

from __future__ import division, print_function, unicode_literals

import re


##  All CMU dict words
##  [(-5, 1), (-4, 6), (-3, 28), (-2, 289), (-1, 6822), (0, 114146), (1, 4520), (2, 54)]
##  11720 errors in 125866 words (9.311%); net errors: -2885 (2.292%)
##
##  CMU dict words intersect with Brown corpus words
##  [(-3, 2), (-2, 14), (-1, 1162), (0, 25180), (1, 1290), (2, 10)]
##  2478 errors in 27658 words (8.959%); net errors: 114 (0.412%)
##
##  CMU dict words intersect with top 12000 Brown corpus words
##  [(-3, 1), (-2, 2), (-1, 337), (0, 8741), (1, 388), (2, 2)]
##  730 errors in 9471 words (7.708%); net errors: 48 (0.507%)


decr_syl_cntr = [
    r'[cfhklmnprsvwxz]ed$',
    r'[ct]ia[ln]',
    r'[tvrd]es$',
  ]


incr_syl_cntr = [
    r'.yi[^aeiou]',
    r'[bgpt]led$',
    r'[bgpt]l$',
    r'ia',
    r'ios?$',
    r'isms?$',
    r'[ntdlrhxco]ua',
    r'[erl]ier',
    r'quie',
    r'[lrngdhtmpfs]eo',
    # r'^re[aeiouy]',     # reduces errors overall but decreases balance.
    r'^mc',
  ]


for k, rx in enumerate(decr_syl_cntr):
    decr_syl_cntr[k] = re.compile(rx)
for k, rx in enumerate(incr_syl_cntr):
    incr_syl_cntr[k] = re.compile(rx)


trailing_e_re = re.compile(r'e$')
vowels_re = re.compile(r'([aeiouy]+)')


def syllable_count_eng(word):
    # assert isinstance(word, unicode if str is bytes else str)
    w = word.lower().replace("'", '')
    w = trailing_e_re.sub('', w)
    n = len(vowels_re.split(w)) // 2
    for rx in decr_syl_cntr:
        if rx.search(w):
            n -= 1
    for rx in incr_syl_cntr:
        if rx.search(w):
            n += 1
    if n <= 0:
        n = 1
    return n


if __name__ == '__main__':
    import sys, io
    with io.open(sys.argv[1], encoding='utf8') as fp:
        for word in fp.read().split():
            k = syllable_count_eng(word)
            print(k, word)
