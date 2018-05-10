#! /usr/bin/env python
# vim: set fileencoding=utf-8

import sys
import json


def main():
    args = sys.argv[1:]
    fn = args[0]
    with open(fn) as fp:
        d = json.load(fp)
    # Using sorted() to get same results in Python 2 and 3.
    for k, v in sorted(d.items()):
        assert isinstance(v, list)
        assert 0 < len(v) < 4
        # print(k, v)
        print('%-40s %s' % (k, ' '.join('%d' % n for n in v)))


main()
