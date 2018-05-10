#! /usr/bin/env python
# vim: set fileencoding=utf-8

# Python 2 or 3

## Copyright © 2018 Raymond D. Gardner
## Licensed under the MIT License

"""Bloom_filter_config.py -- find best parameters for a Bloom filter.

"""

from __future__ import division, print_function, unicode_literals


# m is number of bins; n is number of keys; k is number of probes.
# Optimal k is ln(2) * (m / n) = approx. 0.7 * (m / n)
#   giving false positive prob. of 2^^-k = approx 0.6185 ^^ (m / n).
# Given n and desired false prob. p (assuming optimal k), choose m:
#   m = - n * ln(p) / (ln(2)^^ 2)

from math import log as ln


TWINPRIMES = True
TWINPRIMES = False
PRIME = False
PRIME = True


def isprime(n):
    if n % 2 == 0:
        return n == 2
    k = 3
    while k * k <= n:
        if n % k == 0:
            return False
        k += 2
    return True


def nextprime(n):
    if n < 2:
        n = 2
    n += 1
    if n % 2 == 0:
        n += 1
    while not isprime(n):
        n += 2
    return n


def nexttwinprime(n):
    if n < 5:
        n = 4
    n += 1
    if n % 2 == 0:
        n += 1
    while not isprime(n-2) or not isprime(n):
        n += 2
    return n


def optimal_num_probes(num_bins, num_keys):
    return int(round(ln(2) * num_bins / num_keys))


def num_bins_and_probes_for_false_pos_prob(num_keys, p):
    num_bins = int(round(- num_keys * ln(p) / ln(2) ** 2))
    if PRIME:
        num_bins = nextprime(num_bins)
    if TWINPRIMES:
        num_bins = nexttwinprime(num_bins)
    return num_bins, optimal_num_probes(num_bins, num_keys)


if __name__ == '__main__':
    import sys
    args = sys.argv[1:]
    if len(args) != 2:
        sys.exit('Usage: Bloom_filter_config num_keys, false_positive_probability')
    num_keys, p = args
    num_keys, p = int(num_keys), float(p)
    num_bins, num_probes = num_bins_and_probes_for_false_pos_prob(num_keys, p)
    print('For %d keys and false pos. prob. %f, use %d bins and %d probes.' % (
            num_keys, p, num_bins, num_probes))
