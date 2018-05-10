#! /usr/bin/env python2
# vim: set fileencoding=utf-8

## Copyright © 2018 Raymond D. Gardner
## Licensed under the MIT License

from __future__ import division, print_function, unicode_literals

import re

gue_etc_re = re.compile(r'([gq])u([ei])')
consonants_re = re.compile(
        r'(ch|ll|rr|b|c|d|f|g|j|k|l|m|n|p|q|r|s|t|v|w|x|z|\xf1|\xd1)')


def syllable_count_spa(word):
    """Return number of syllables in a Spanish word.

    Spanish syllables each have one or more vowels. Split the word
    on consonants. Examine the intervening vowels. Each string of
    consecutive vowels will be part of one or more syllables.
    Single vowels count for one syllable. Double vowels will count
    as one or two depending on whether they form a dipthong, which
    is one strong (aeo) and one weak (iuy) or two weak vowels. A
    dipthong counts as one, otherwise as two. If one of the "weak"
    vowels is accented, it's not a dipthong and counts as two.
    Ignore h. Ignore u in gue, gui, que, qui.
    Consider ch, ll, rr as single consonants.
    """
# See:
# http://www.spanishdict.com/answers/100865/syllables-how-to-divide-a-word-in-spanish-by-lazarus
# http://glennhumphries.com/Notebook/chart3.htm
    # assert isinstance(word, unicode if str is bytes else str)
    vs = u'aeo'                  # Strong
    vsa = u'aeoáéó'             # Strong + strong accented: a/e/o acute
    vwa = u'íú'                 # Weak but accented: i acute, u acute
    word = word.lower().replace('h', '')
    word = gue_etc_re.sub(r'\1\2', word)
    a = consonants_re.split(word)
    n = 0
    for k in range(0, len(a), 2):
        v = a[k]
        if len(v) == 1:
            n += 1
        elif len(v) == 2:
            v0, v1 = v[0], v[1]
            if v0 in vsa and v1 in vsa:
                n += 2
            elif (v0 in vs and v1 in vwa) or (v0 in vwa and v1 in vs):
                n += 2
            else:
                n += 1
        elif len(v) == 3:
            n += 2
        elif len(v) > 3:
            n += 2
    return n


if __name__ == '__main__':
    import io
    with io.open('spanish_words') as fp:
        for word in fp.read().splitlines():
            k = syllable_count_spa(word)
            print(k, word)
