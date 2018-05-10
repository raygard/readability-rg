#! /usr/bin/env python
# vim: set fileencoding=utf-8

# Python 2 or 3

## Copyright © 2018 Raymond D. Gardner
## Licensed under the MIT License

"""make_Bloom_filter.py - make Bloom filter data file from dict data.

Usage: make_Bloom_filter.py syllable_counts.json Bloom_filter_data.py

The syllable_counts.json file must be created from the CMU pronouncing
dictionary with make_cmudict_syllables.py.
"""

from __future__ import division, print_function, unicode_literals


import sys
import json
import random
import string

import syllable_count_eng
import Bloom_filter
import Bloom_filter_config

FALSE_POSITIVE_PROBABILITY = 0.001
FALSE_POSITIVE_PROBABILITY = 0.0001

BLOOM_FILTER_TEST = True
BLOOM_FILTER_TEST = False

SAMPLE_TEST = True
SAMPLE_TEST = False


def printf(format_str, *args):
    sys.stdout.write(format_str % args)


def test(cmudict, syllable_count_function):
    """Check count from syllable_count_function against CMU dict count.

    For each word in CMU dict, get count from function. Track errors
    and return word count, total error count, net error count,
    and a dictionary of words keyed by error count.
    """
    errcnt = 0
    neterr = 0
    nwords = 0
    errs = {}
    for word in sorted(cmudict.keys()):
        # The JSON file has the keys forced lowercase.
        assert isinstance(word, unicode if str is bytes else str)
        nwords += 1
        syll_counts = cmudict[word]
        err = 0
        my_count = syllable_count_function(word)
        # Detect if my count is outside range of CMU counts.
        if my_count not in syll_counts:
            if my_count < syll_counts[0]:
                # Undercount (negative): below lowest CMU count.
                err = my_count - syll_counts[0]
            elif syll_counts[-1] < my_count:
                # Overcount (positive): above highest CMU count.
                err = my_count - syll_counts[-1]
            else:
                # Odd case: my count is not in CMU counts but is in its range.
                # This has never happened, but we're prepared.
                assert syll_counts[0] < my_count < syll_counts[-1]
                abserr = min(abs(my_count - cc) for cc in syll_counts)
                err = [my_count - cc for cc in syll_counts
                        if abs(my_count - cc) == abserr][0]
        errcnt += (err != 0)
        neterr += err
        if err not in errs:
            errs[err] = set()
        errs[err].add(word)
    return nwords, errcnt, neterr, errs


def create_write_Bloom_filter_data(fp, filter_name, prob, words):
    nbins, nprobes = Bloom_filter_config.num_bins_and_probes_for_false_pos_prob(
            len(words), prob)
    # print(type(words), len(words), type(sorted(words)[0]))
    bf = Bloom_filter.BloomFilter2(nbins, nprobes, words)
    assert all(wd in bf for wd in words)
    bf.dump_filter(fp, filter_name)
    return bf


def make_syl_count_bf(under_bf, over_bf):
    """Return a syllable count function using Bloom filters."""
    def syl_count_bf(word):
        n = syllable_count_eng.syllable_count_eng(word)
        if word in under_bf:
            n += 1
        elif word in over_bf:
            n -= 1
        if n <= 0:
            n = 1
        return n
    return syl_count_bf


def test_filter(cmudict, label, bf, keys):
    """Test filter with words under- or overcounted by one."""
    nkeys = len(keys)
    k = sum(int(word in bf) for word in cmudict)
    printf('%s in cmudict: %d hits  %d keys  '
            '%d non-key hits  %d dict words  %.5f errs\n',
            label, k, nkeys, k-nkeys, len(cmudict), float(k-nkeys) / len(cmudict))


def check_cmudict_for_under_over_counts(cmudict, under_bf, over_bf):
    false_overs = []
    false_under_cnt = 0
    for word in sorted(cmudict.keys()):
        syll_counts = cmudict[word]
        my_count = syllable_count_eng.syllable_count_eng(word)
        if my_count in syll_counts:
            if word in under_bf:
                false_under_cnt += 1
                print('CMU dict word has false undercount filter hit:',
                        word, my_count, syll_counts)
            elif word in over_bf:
                false_overs.append((word, my_count, syll_counts))
    for word, my_count, syll_counts in false_overs:
        print('CMU dict word has false overcount filter hit: ',
                word, my_count, syll_counts)
    printf('False undercount hits: %d  False overcount hits: %d\n',
            false_under_cnt, len(false_overs))


def check_cmudict_for_under_over_counts(cmudict, under_bf, over_bf):
    false_unders, false_overs = [], []
    for word in sorted(cmudict.keys()):
        syll_counts = cmudict[word]
        my_count = syllable_count_eng.syllable_count_eng(word)
        if my_count in syll_counts:
            if word in under_bf:
                # false_unders.append((word, my_count, syll_counts))
                false_unders.append(word)
            elif word in over_bf:
                # false_overs.append((word, my_count, syll_counts))
                false_overs.append(word)
    print('False undercount hits (%d):' % len(false_unders), ' '.join(false_unders))
    print('False overcount hits (%d):' % len(false_overs), ' '.join(false_overs))
    # FIXME
    # print('False overcount hits:', ' '.join(false_overs))
    # for word, my_count, syll_counts in false_overs:
    #    #print('!!!word is false over:', word, my_count, syll_counts)
    #    print('CMU dict word has false overcount filter hit: ', word, my_count, syll_counts)
    #            print('CMU dict word has false undercount filter hit:', word, my_count, syll_counts)
    # printf('False undercount hits: %d  False overcount hits: %d\n', false_under_cnt, len(false_overs))


def make_bf(cmudict_fn, filter_data_fn):
    with open(cmudict_fn) as f:
        cmudict = json.load(f)
    nwords, errcnt, neterr, errs = test(cmudict, syllable_count_eng.syllable_count_eng)
    printf('Syllable count errors without Bloom filter:\n')
    printf('%s\n', sorted((k, len(errs[k])) for k in errs))
    printf('%d errors in %d words (%.3f%%); net errors: %d (%.3f%%)\n',
        errcnt, nwords, 100.0 * errcnt / nwords, neterr, abs(100.0 * neterr / nwords))
    prob = FALSE_POSITIVE_PROBABILITY
    with open(filter_data_fn, 'wb') as fp:
        fp.write(b'#! /usr/bin/env python\n# vim: set fileencoding=utf-8\n\n')
        fp.write(b'# Python 2 or 3\n\n')
        fp.write(b'## Bloom filter data -- generated by Bloom_filter.py\n')
        under_bf = create_write_Bloom_filter_data(fp, 'undercount_filter',
                                                    prob, errs[-1])
        over_bf = create_write_Bloom_filter_data(fp, 'overcount_filter',
                                                    prob, errs[1])

    printf('Bloom filter stats:\n')
    under_bf.print_filter_stats('undercount_filter')
    test_filter(cmudict, 'undercount_filter', under_bf, errs[-1])
    over_bf.print_filter_stats('overcount_filter')
    test_filter(cmudict, 'overcount_filter', over_bf, errs[1])

    if BLOOM_FILTER_TEST:
        printf('Syllable count errors with Bloom filter:\n')
        nwords, errcnt, neterr, errs = test(cmudict,
                                        make_syl_count_bf(under_bf, over_bf))
        printf('%s\n', sorted((k, len(errs[k])) for k in errs))
        printf('%d errors in %d words (%.3f%%); net errors: %d (%.3f%%)\n',
                    errcnt, nwords, 100.0*errcnt / nwords,
                    neterr, abs(100.0*neterr / nwords))

    check_cmudict_for_under_over_counts(cmudict, under_bf, over_bf)

    if SAMPLE_TEST:
        # These counts may not be completely accurate, as it is possible
        # that the 8 letter random string is an actual word, but the
        # chance of that is vanishingly small.
        # Also note that Python 2 and 3 give different results on this
        # because their random.sample() algorithms are a bit different.
        trials = 100000
        random.seed('abc')  # Fixed seed for repeatability.
        m = sum(''.join(random.sample(string.ascii_letters, 8))
                in under_bf for _ in range(trials))
        printf('undercount false positives:%4d in %d trials (%.5f%%)\n',
                m, trials, float(m) / trials)
        m = sum(''.join(random.sample(string.ascii_letters, 8)) in over_bf
                for _ in range(trials))
        printf('overcount false positives:%5d in %d trials (%.5f%%)\n',
                m, trials, float(m) / trials)


def usage_exit(msg=""):
    if msg and not msg.endswith("\n"):
        msg += "\n"
    sys.exit("%s%s" % (msg, __doc__))


def main():
    args = sys.argv[1:]
    if len(args) != 2:
        usage_exit('Need exactly 2 args.')
    cmudict_fn, filter_data_fn = args
    make_bf(cmudict_fn, filter_data_fn)


if __name__ == '__main__':
    main()
