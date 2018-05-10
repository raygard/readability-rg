#! /usr/bin/env python
# vim: set fileencoding=utf-8

# Python 2 or 3

## Copyright © 2018 Raymond D. Gardner
## Licensed under the MIT License

"""make_cmudict_syllables.py - make dict of syllable counts of CMU dict words.

Usage:
    make_cmudict_syllables.py CMUdict_file json_out_file
where:
    CMUdict_file is cmudict.0.7a or cmudict-0.7b or later.
    json_out_file is (for example) cmudict_syllables.json

Thanks to Jordan Boyd-Graber, who observed that we can use cmudict to count
syllables by counting the digits in each pronunciation.
https://groups.google.com/forum/#!msg/nltk-users/mCOh_u7V8_I/HsBNcLYM54EJ
"""

from __future__ import division, print_function, unicode_literals


import sys
import io
import re
import collections
import json


word_re = re.compile(r'[a-z][-\'a-z]*$')


def make_cmudict_syllables_json(infn, outfn):
    pronunc_dict = {}
    with io.open(infn, encoding='latin1') as fp:
        for s in fp:
            s = s.strip()
            # Hack for cmudict-0.7b: The only entry with non-ASCII.
            # cmudict.0.7a and cmudict.dict are all ASCII.
            s = s.replace('DÉJÀ', 'DEJA')
            if not s or s.startswith(';;') or s.startswith('##'):
                continue
            word, pronunciation = s.split(' ', 1)
            k = word.find('(', 1)
            if k > 0:
                word = word[:k]
            word = word.lower()
            if not word_re.match(word):
                # print('Not a word:', word)
                continue
            assert '(' not in pronunciation     # Defend against format error.
            pronunciation = pronunciation.strip()
            if word not in pronunc_dict or pronunciation not in pronunc_dict[word]:
                pronunc_dict.setdefault(word, []).append(pronunciation)

    syll_count_dict = collections.OrderedDict()
    for word, pronunciations in sorted(pronunc_dict.items()):
        for pronunciation in pronunciations:
            # Count of digits is number of syllables.
            num_syllables = len(re.sub(r'[^0-9]', '', pronunciation))
            syll_count_dict.setdefault(word, []).append(num_syllables)

    for word in syll_count_dict.keys():
        syll_counts = sorted(set(syll_count_dict[word]))
        # Hack to adjust if syllable count is 0.
        assert len(syll_counts)
        if syll_counts[0] == 0:
            print('Has syllable count of 0:', word, syll_counts)
            if len(syll_counts) == 1:
                syll_counts[0] = 1
            else:
                del syll_counts[0]
            print('Fixed count:', word, syll_counts)
        syll_count_dict[word] = syll_counts

    # To make .json w/ Unix line endings in Python 2 or 3.
    with (open(outfn, 'wb') if bytes is str
            else open(outfn, 'w', newline='\n')) as fp:
        json.dump(syll_count_dict, fp, indent=2)


def usage_exit(msg=''):
    if msg and not msg.endswith('\n'):
        msg += '\n'
    sys.exit('%s%s' % (msg, __doc__))


def main():
    args = sys.argv[1:]
    if len(args) != 2:
        usage_exit('Need exactly 2 args.')
    infn, outfn = args
    make_cmudict_syllables_json(infn, outfn)


main()
