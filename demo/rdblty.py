#! /usr/bin/env python
# vim: set fileencoding=utf-8

# Python 2 or 3

"""rdblty.py

  Usage: rdblty.py -h -s -e encoding -n --sentences -w --syllables format files...
  Where
      -h, --help            This usage screen
      -e  encoding          input file encoding (default UTF-8)
      -S, --Spanish         assume input files are Spanish
      -w, --words           dump words
      -s, --sentences       display sentences
      -n                    show syllable counts (forces --sentences)
      --syllables format    format for syllable count (implies -n)
                              default is "%s{%d}"

This is a demo program for the Readability module.
"""

## Copyright © 2018 Raymond D. Gardner
## Licensed under the MIT License


from __future__ import division, print_function, unicode_literals


import sys
import os
import getopt
import glob
import zipfile

import readability


def printf(fmt, *args):
    sys.stdout.write(fmt % args)


def report_words(dwords):
    printf('====WORDS:==== %d\n', len(dwords))
    end_dot = []
    for s in end_dot:
        ss = s[:-1]
        dwords[ss] = dwords.get(ss, 0) + dwords[s]
        del dwords[s]

    def rep_del(label, testt):
        '''Report a class of keys in dwords and delete them.'''
        def test(s):
            try:
                return testt(s)
            except IndexError:
                sys.stderr.write('wtf? %r\n' % s)
                raise
        dd = [(key, val) for key, val in dwords.items() if test(key)]
        for key, val in dd:
            del dwords[key]
        dd.sort(key=lambda t: (-t[1], t[0].lower(), t[0]))
        printf('====( %s )==== %d\n', label, len(dd))
        for wd, k in dd:
            # TEMP! FIXME this assert should work
            assert ' ' not in wd
            printf('%6d %s\n', k, wd)

    rep_del('lower', lambda s: s.isalpha() and s.islower())
    rep_del('upper', lambda s: s.isalpha() and s.isupper())
    rep_del('cap', lambda s: s.isalpha() and len(s) > 1
            and s[0].isupper() and s[1:].islower())
    rep_del('apostrophed', lambda s: "'" in s and s.replace("'", '', 1).isalpha())
    # rep_del('hyphenated', lambda s: '-' in s and s.replace('-', '', 2).isalpha())
    rep_del('hyphenated', lambda s: '-' in s and s.replace('-', '').isalpha())
    rep_del('alpha', lambda s: s.isalpha())
    rep_del('number', lambda s: s.isdigit())
    rep_del('number+', lambda s: s[0].isdigit() or
            (s[0] == '.' and s[1:2].isdigit()))
    rep_del('URL', lambda s: s.startswith('http:') or s.startswith('https:'))
    rep_del('ends_dot', lambda s: s[-1] == '.')
    rep_del('leftovers', lambda s: True)


def report_separators(dseparators):
    printf('====( NONWORDS )==== %d\n', len(dseparators))
    dd = sorted(dseparators.items(), key=lambda t: (-t[1], t[0]))
    for wd, k in dd:
        def encr(s):
            assert isinstance(s, unicode if str is bytes else str)
            return '{%s}' % s
        printf('%6d %s\n', k, encr(wd))


def get_text_list(optns, fp):
    v, text_list = [], []
    for s in fp.read().decode(optns.enc).splitlines():
        v.append(s)
        # Break into chunks (probable paragraph breaks) on empty lines.
        if not s.strip():
            text_list.append(' '.join(v))
            v = []
    text_list.append(' '.join(v))
    return text_list


def do_file(optns, fp, fn, dwords, dseparators, stats):
    text_list = get_text_list(optns, fp)
    rb = readability.Readability(get_sentences=optns.get_sentences,
                            show_syllable_counts=optns.show_syllable_counts,
                            dwords=dwords, dseparators=dseparators,
                            language=optns.language)
    basefn = os.path.basename(fn)
    if optns.get_sentences and not optns.show_syllable_counts:
        # For later sanity check.
        text_list_copy = text_list[:]
    sentences = rb.read(text_list)
    if optns.get_FK:
        nsentences, nwords, nsyllables = rb.stats()
        stats.tot_level += rb.FK_grade()
        stats.tot_words += nwords
        stats.tot_level_words += nwords * rb.FK_grade()
        if optns.language == 'eng':
            printf('%-24.24s:%7d:%6.1f:%6.1f  '
                    '%9.1f  %5.1f (%4d sentences; %6d syllables)\n',
                    basefn, nwords, rb.FK_grade(), rb.FRES(), rb.Fog_index(),
                    rb.SMOG_index(), nsentences, nsyllables)
        elif optns.language == 'spa':
            printf('%-24.24s:%7d:%6.1f:%6.1f  '
                    '%5.1f %-15s (%3d sentences;%6d syllables)\n',
                    basefn, nwords, rb.Huerta_ease(), rb.Huerta_corrected(),
                    rb.IFSZ_index(), rb.Inflesz_scale(), nsentences,
                    nsyllables)
        else:
            printf('!! We only process English and Spanish!\n')
    if optns.get_sentences:
        printf('File: %s\n', basefn)
        alls = []
        for j, sentence in enumerate(sentences):
            if not optns.show_syllable_counts:
                alls.extend(sentence)
            if ''.join(sentence):
                # Use this for sentence numbering:
                # printf('%3d %s\n', j+1, ''.join(sentence))
                printf('%s\n', ''.join(sentence))
        # Sanity check: if not showing syllable counts, then sentences
        # returned from readability should match original text.
        assert optns.show_syllable_counts or ''.join(text_list_copy) == ''.join(alls)


def do_zip(optns, zfn, dwords, dseparators, stats):
    with zipfile.ZipFile(zfn) as zf:
        for fn in zf.namelist():
            if not fn.endswith('/'):
                with zf.open(fn) as fp:
                    do_file(optns, fp, fn, dwords, dseparators, stats)
                    stats.num_files += 1
                    sys.stderr.write('%6d\r' % stats.num_files)


def do_files(optns, fns):
    printf('%d files.\n', len(fns))
    stats = type(str('stats'), (), {})()
    stats.tot_level = 0
    stats.tot_words = 0
    stats.tot_level_words = 0
    stats.num_files = 0
    if optns.language == 'eng':
        print('File:                      Words: Level:  Ease        Fog   Smog')
    else:
        print('File:                      Words:  Ease:  Corr  IFSZx IFSZscale:')

    dwords = {}
    dseparators = {}
    for fn in fns:
        if fn.endswith('.zip') or fn.endswith('.zip.exe'):
            do_zip(optns, fn, dwords, dseparators, stats)
        else:
            with open(fn, 'rb') as fp:
                # We read binary because do_file() also has to handle zipped
                # elements, which always read as binary.
                do_file(optns, fp, fn, dwords, dseparators, stats)
                stats.num_files += 1

    if stats.num_files == 0:
        usage_exit('NO FILES?')

    print('Files:', stats.num_files, 'words:', stats.tot_words,
            'average word count:',
            '%.1f' % (stats.tot_words * 1.0 / stats.num_files))
    print('Average reading level:', '%.1f' % (stats.tot_level / stats.num_files))
    if stats.tot_words:
        print('Average reading level weighted by word count:',
                '%.1f' % (stats.tot_level_words / stats.tot_words))
    if optns.words:
        report_words(dwords)
        report_separators(dseparators)


def usage_exit(msg=''):
    if msg and not msg.endswith('\n'):
        msg += '\n'
    sys.exit('%s%s' % (msg, __doc__))


def main():
    args = sys.argv[1:]
    if len(args) == 0:
        usage_exit('No args given.')
    try:
        (opts, args) = getopt.gnu_getopt(args, 'he:Swsn',
                ['help', 'Spanish', 'words', 'sentences', 'syllables='])
    except getopt.GetoptError as e:
        usage_exit(e.msg)
    optns = type(str('optns'), (), {})()
    optns.enc = 'utf8'
    optns.language = 'eng'
    optns.words = False
    optns.get_sentences = False
    optns.show_syllable_counts = False
    optns.get_FK = True
    for optflag, optval in opts:
        if optflag == '-h' or optflag == '--help':
            usage_exit()
        elif optflag == '-e':
            optns.enc = optval
        elif optflag == '-S':
            optns.language = 'spa'
        elif optflag == '-w' or optflag == '--words':
            optns.words = True
        elif optflag == '-s' or optflag == '--sentences':
            optns.get_sentences = True
        elif optflag == '-n':
            optns.show_syllable_counts = True
            optns.get_sentences = True
        elif optflag == '--syllables':
            optns.show_syllable_counts = optval
        else:
            usage_exit()
    fns = []
    for fn in args:
        fns += glob.glob(fn)
    do_files(optns, fns)


main()
