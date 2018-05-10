#! /usr/bin/env python
# vim: set fileencoding=utf-8

# Python 2 or 3

## Copyright © 2018 Raymond D. Gardner
## Licensed under the MIT License


from __future__ import division, print_function, unicode_literals

import sys
import json
import re
import io

from syllable_count_eng import syllable_count_eng as syllable_count
from syllable_count_eng_bf import syllable_count_eng_bf as syllable_count_bf


cmudict_fn = 'cmudict_dev.json'
Brown_words_fn = 'Brown_words.txt'


def test(nsyll, words):
    with open(cmudict_fn) as fp:
        cmud = json.load(fp)
    errcnt = 0
    neterr = 0
    errs = {}
    if not words:
        words = cmud.keys()
    nwords = 0
    for w in sorted(words):
        assert isinstance(w, unicode if str is bytes else str)
        if w not in cmud:
            continue
        if not re.match(r'[a-z][-\'a-z]*$', w):
            continue
        nwords += 1
        cs = cmud[w]
        try:
            ms = nsyll(w)
        except Exception:
            print(nsyll.__name__)
            raise
        if cs[0] == 0:
            if len(cs) == 1:
                cs[0] = 1
            else:
                del cs[0]
        err = 0
        if ms not in cs:
            if ms < cs[0]:
                err = ms - cs[0]
            elif cs[-1] < ms:
                err = ms - cs[-1]
            else:
                assert cs[0] < ms < cs[-1]
                err = ms - cs[0]
                err2 = cs[-1] - ms
                if err > err2:
                    err = -err2
        errcnt += (err != 0)
        neterr += err
        if err or 1:
            if err not in errs:
                errs[err] = set()
            errd = errs[err]
            errd.add(w)
    return errcnt, nwords, neterr, errs


def main():
    def run_test(hdr):
        print(hdr)
        errcnt, nwords, neterr, errs = test(scnt, words[:])
        print(sorted((k, len(errs[k])) for k in errs))
        print('%d errors in %d words (%.3f%%); net errors: %d (%.3f%%)\n' % (
                errcnt, nwords, 100.0 * errcnt / nwords, neterr, abs(100.0 * neterr / nwords)))
        print('Undercount by one:\n', len(errs[-1]))
        #print('\n'.join(errs[-1]))
        print('Overcount by one:\n', len(errs[1]))
        #print('\n'.join(errs[1]))
        #raise SystemExit
        if 1:
            for k in sorted(errs):
                if k:
                    for s in sorted(errs[k]):
                        print(k, s)
        if 0:
            for k in sorted(errs):
                if k < -1:
                    print(k, sorted(errs[k]))
            for k in sorted(errs):
                if k > 1:
                    print(k, sorted(errs[k]))

    #for scnt in (syllable_count, syllable_count_bf):
    for scnt in (syllable_count, ):
        print('Without' if scnt is syllable_count else '\nWith', 'Bloom filters')
        words = []
        run_test('All CMU dict words')
        with io.open(Brown_words_fn, encoding='utf8') as fp:
            words = fp.read().splitlines()
        run_test('CMU dict words intersect with Brown corpus words')
        words = words[:12000]
        run_test('CMU dict words intersect with top 12000 Brown corpus words')
    print('OK')


main()
