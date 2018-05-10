#! /usr/bin/env python
# vim: set fileencoding=utf-8

# Python 2 or 3

## Copyright © 2018 Raymond D. Gardner
## Licensed under the MIT License


"""readability.py -- compute readability measures on text.

Compute measures on English or Spanish text. These include:
    For English:
        Flesch reading ease
        Flesch-Kincaid grade level
        Gunning Fog
        SMOG
    For Spanish:
        Huerta ease
        Huerta ease corrected by me
        Flesch-Szigriszt (IFSZ, Flesch-Szigriszt Readability Index)
"""


from __future__ import division, print_function, unicode_literals

import re
import math


# from syllable_count_eng import syllable_count_eng
from .syllable_count_eng_bf import syllable_count_eng_bf as syllable_count_eng
from .syllable_count_spa import syllable_count_spa


# Regex to accept "words" including URLs and numbers.
# Sentences usually end with dot (.), bang (!), or question mark (?).
# We include these as "word" tokens to simplify sentence breaking.
# Anything that doesn't match this is a "nonword".
# Order of alternatives is significant!
words_re = re.compile(r'''(
# Naive, sloppy URL recognizer.
(?:https?://
# URL chars, incl. % escapes
(?:%[0-9a-fA-F]{2}|[A-Za-z0-9_~:/#\[\]@$&'*+;=\-(),.?!])*
# Don't accept [),.?!] as end of URL; probably part of the text.
(?:%[0-9a-fA-F]{2}|[A-Za-z0-9_~:/#\[\]@$&'*+;=\-(]     ))
|
# Words are letters, dots, ampersands, apostrophes, and hyphens.  Must begin
# with a letter.  Cannot have adjacent dots, ampersands, apostrophes, or
# hyphens.  Word cannot end with a dot, ampersand, apostrophe or hyphen.
# Maybe try using \w in place of [A-Za-z\xc0-\xf6\xf8-\xff]
(?:[A-Za-z\xc0-\xf6\xf8-\xff]+[.&'’-])*
[A-Za-z\xc0-\xf6\xf8-\xff]+
|
# Numbers are digits, dots, commas, and hyphens.
# Dot at end of a number is not consumed as part of the number.
#(?:[0-9]+[.,-])*[0-9]+
#(?:[.]?(?:[0-9]+[.,-])*[0-9]+)
\.?(?:[0-9]+[.,-])*[0-9]+
|
# Sentences usually end with dot (.), bang (!), or question mark (?).
# We include these as "word" tokens to simplify sentence breaking.
#
# We'll assume a sentence ends if it's a bang or question mark.
[!?]+["”'’)\]]?
|
# Dots are usually sentence enders but need to be checked for
# initials or abbreviations. There is no definitive way to tell.
\.\.\.+
| \.\.
# The next line is for possessive abbreviations, e.g. "Jr.'s".
| \.'s | \.’s
| \.["”'’)\]]*
)
''', re.VERBOSE)


spaces_re = re.compile(r'(\s+)')
sentence_end_chars = '!?'
maybe_sentence_end_chars = sentence_end_chars + '.'
enders_re = re.compile(r'[%s]+$' % maybe_sentence_end_chars)


# Sentence boundary detection is a somewhat tricky problem, not entirely solved.
# It is discussed at some length in several papers, including:
# Grefenstette, Gregory, and Pasi Tapanainen:
# What is a word, What is a sentence? Problems of Tokenization (1994)
# Retrieved 2018-03-02 from:
# http://www.dfki.de/~neumann/qa-course/grefenstette94what.pdf
# Referred to here as grefenstette94.

# The trickiest aspect may be deciding when a dot is a period after an
# abbreviation vs. a full stop at the end of a sentence, or if it is both.

# The abbreviation detection here is adapted from the first approach in
# grefenstette94. They use regex to match: a single letter followed by dot; a
# sequence of letter, dot, letter-or-digit, dot, ...; or an uppercase letter
# followed by one or more consonants followed by dot. The first case is
# subsumed by the second, so our regex needs only two alternatives.

# Abbreviations matching the regex are considered to be not and end of sentence
# (EOS) if followed by an uppercase. I'm not sure that grefenstette94 considers
# if the follower is uppercase. But they then enumerate the abbreviations in
# the Brown Corpus that do not match the regex. I find that their list is
# incomplete, and I handle numbers differently from them, so I have a somewhat
# different list of abbreviations which, if followed by an uppercase, will not
# be considered EOS. Also, I only accept a month abbreviation if followed by a
# digit.

abbr_re = re.compile(r'''(
[A-Za-z](\.[A-Za-z0-9])*$
|
[A-Z][bcdfghj-np-tvwxz]+$
)
''', re.VERBOSE)

# From Grefenstette 94. Not the copy cited above. Maybe a later version?
# "The abbreviations in Brown that do not match the above regular expressions
# are the following:"
# etc Fig No Co (Month-Names) Sen Gen Rev Gov (U.S.-State-Abbreviations) fig
# Rep Ave Corp figs Figs 24-hr lbs Capt yrs dia Stat Ref Prof Atty 6-hr sec
# eqn chap Messrs Dist Dept ex-Mrs Vol Tech Supt Rte Reps Prop Mmes 8-oz
# viz var seq prop pro-U.N.F.P nos mos min mil mEq ex-Gov eqns dept Yok
# USN Ter Shak Sha Sens SS Ry Rul Presbyterian-St P.-T.A Msec McN Maj
# Lond Jas Grev Gre Cir Cal Brig Aubr 42-degrees-F 400-lb 400-kc 36-in 3-hp
# 3-by-6-ft 29-Oct 27-in 25-ft 24-in 160-ml 15,500-lb 12-oz 100-million-lb 10-yr
# 1.0-mg 0.5-mv./m 0.1-mv./m 0.080-in 0.025-in

# These are mostly from Brown Corpus, NLTK version, redacted by me (rdg):
known_abbrs = {
    'etc', 'Fig', 'No', 'Co', 'Sen', 'Gen', 'Rev', 'Gov', 'lb', 'Sec', 'vs',
    'fig', 'Rep', 'Ave', 'cm', 'Corp', 'mg', 'mm', 'Figs', 'gm', 'ft',
    'figs', 'Col', 'cf', 'lbs', 'Capt', 'cu', 'Atty', 'Prof', 'pp', 'sq',
    'dia', 'cc', 'yrs', 'Hon', 'Stat', 'Ref', 'hr', 'Dist', 'Messrs',
    'Dept', 'sec', 'eqn', 'Reps', 'Supt', 'dept', 'Rte', 'oz', 'Vol', 'ca',
    'kc', 'hp', 'Prop', 'Mmes', 'Brig', 'USN', 'Cir', 'Bros', 'msec', 'viz',
    'var', 'seq', 'prop', 'nos', 'ml', 'eqns', 'yd', 'Spec', 'Maj',
    'Sr', 'Sra', 'Srta',    # Some Spanish forms of address.
    }


month_abbrs = {'Jan', 'Feb', 'Mar', 'Apr', 'Jun', 'Jul', 'Aug', 'Sep', 'Sept',
                'Oct', 'Nov', 'Dec'}


# A few words match abbr_re but are not often abbreviations.
non_abbrs = {'Act', 'Arts', 'End', 'Inn'}


def is_abbreviation(word, nx):
    return ((word in month_abbrs and nx[:1].isdigit()) or
            (word not in non_abbrs and
            (abbr_re.match(word) or word in known_abbrs)
            ))


class Readability(object):

    def __init__(self, get_sentences=True,
                        count_syllables=True,
                        show_syllable_counts=False,
                        dwords=None,
                        dseparators=None,
                        language='eng'):
        self.nsentences = 0
        self.nwords = 0
        self.hard_words = 0
        self.nsyllables = 0
        self.language = language
        self.nsyl = None
        if count_syllables:
            self.nsyl = self.nsyl_eng if language == 'eng' else self.nsyl_spa
        self.show_syllable_counts = show_syllable_counts
        self.get_sentences = get_sentences
        self.dwords = dwords
        self.dseparators = dseparators

    def nsyl_eng(self, wd):
        if wd == '' or enders_re.match(wd):
            return 0
        return syllable_count_eng(wd)

    def nsyl_spa(self, wd):
        if wd == '' or enders_re.match(wd):
            return 0
        return syllable_count_spa(wd)

    def sentence_breaker(self, text):
        tokens = words_re.split(text)
        assert tokens
        num_tokens = len(tokens)
        assert num_tokens & 1   # Odd
        # A list of tokens.
        sentence = []
        # A list of sentences.
        sentences = []
        k = 1
        while k < num_tokens:
            while k < num_tokens:
                sentence.extend(tokens[k-1:k+1])
                token = tokens[k]
                k += 2
                if token[0] not in maybe_sentence_end_chars:
                    continue
                if k >= num_tokens:
                    break
                if token[0] in sentence_end_chars:
                    break
                assert token[0] == '.'
                # Don't end with a number.
                if token[1:2].isdigit():
                    continue
                # Don't end with an ellipsis.
                if token.startswith('...'):
                    continue
                # Not sure what two dots means, but consider it EOS.
                # It may be an abbreviation period followed by full stop.
                if token == '..':
                    break
                # If not standalone dot, consider it EOS.
                if token != '.':
                    # This assert must be true due to regex used:
                        # \.\.\.+ | \.\. | \.'s | \.’s | \.["”'’)\]]*
                    assert len(token) > 1 and token[1] in '"”\'’)]'
                    if token[1] in '\'’':
                        # Maybe possessive abbreviation, e.g. "Jr.'s"
                        continue
                    if token not in ('.', '.)'):
                        break
                # Dot may be EOS or end of abbreviation (or both).
                # Get following text.
                nx = tokens[k-1] + tokens[k]
                assert len(nx)
                # Not EOS if followed by nonspace.
                if not nx[:1].isspace():
                    continue
                nx = nx.lstrip()
                # Not EOS if followed by space(s) then lowercase.
                if nx[:1].islower():
                    continue
                if not (nx[:1].isupper() or nx[:1].isdigit()):
                    break
                # At beginning; can't look back!
                if k - 4 < 0:
                    break
                # EOS if there is any separator before the dot:
                if tokens[k - 3]:
                    break
                # Not EOS if preceding "word" is an abbreviation.
                if is_abbreviation(tokens[k - 4], nx):
                    continue
                break
            # End of sentence
            assert (len(sentence) & 1) == 0       # Even
            sentence.append('')
            sentences.append(sentence)
            sentence = []
        sentence.append(tokens[num_tokens - 1])
        sentences.append(sentence)

        if len(sentences[-1]) == 1 and len(sentences) > 1:
            # Last "sentence" is a single token; merge it into previous.
            assert sentences[-2][-1] == ''
            if sentences[-2][-1] != sentences[-1][0]:
                sentences[-2][-1] = sentences[-1][0]
            del sentences[-1]

        # Whitespace after a sentence is now in the first element of the
        # next sentence. Here, we move it to the end of the sentence it
        # follows, so each sentence begins with non-whitespace.
        # Some sentences begin with 'nonwords' with no whitespace;
        # we leave those nonwords alone.
        for k, sentence in enumerate(sentences):
            if k < len(sentences) - 1:
                assert len(sentence) & 1    # Odd
                assert sentence[-1] == ''
                next_sentence = sentences[k+1]
                assert len(next_sentence) > 0
                assert len(next_sentence) > 1
                first_word_next_sent = next_sentence[0]
                if spaces_re.search(first_word_next_sent) is not None:
                    first_word_split = spaces_re.split(first_word_next_sent)
                    sentence[-1] = ''.join(first_word_split[:-1])
                    next_sentence[0] = first_word_split[-1]
            elif (len(sentence) & 1) == 0:      # Even
                # Can this ever happen?
                raise Exception('sentence length is even! {%s}' % sentence)
                sentence.append('')
        return sentences

    def read(self, text_list):
        nsyl = self.nsyl
        dwords, dseparators = self.dwords, self.dseparators
        show = self.show_syllable_counts
        all_sentences = []
        if isinstance(text_list, unicode if str is bytes else str):
            text_list = [text_list]
        if not isinstance(text_list, list):
            raise TypeError('Expected list or Unicode string; got %s' %
                            type(text_list))
        for text in text_list:
            if not isinstance(text, unicode if str is bytes else str):
                raise TypeError('Expected list of Unicode string; got %s' %
                                type(text))
            sentences = self.sentence_breaker(text)
            if self.get_sentences:
                all_sentences.extend(sentences)
            for sentence in sentences:
                slen = len(sentence)
                assert slen & 1     # Odd
                hold_nwords = self.nwords
                for k, wd in enumerate(sentence):
                    if (k & 1) == 0:
                        if dseparators is not None:
                            dseparators[wd] = dseparators.get(wd, 0) + 1
                    else:
                        if dwords is not None:
                            dwords[wd] = dwords.get(wd, 0) + 1
                        if nsyl is None:
                            self.nwords += 1  # Count words if not counting syl.
                        else:
                            nsylk = nsyl(wd)
                            if nsylk != 0:
                                self.nsyllables += nsylk
                                self.nwords += 1    # Only count words w/ syllables.
                                if nsylk > 2:
                                    self.hard_words += 1
                                if isinstance(show, str):
                                    if 'word' in show and 'count' in show:
                                        sentence[k] = show % dict(
                                                word=sentence[k], count=nsylk)
                                    else:
                                        sentence[k] = show % (sentence[k], nsylk)
                                elif show:
                                    sentence[k] = '%s{%d}' % (sentence[k], nsylk)
                if self.nwords > hold_nwords:
                    self.nsentences += 1     # Only count sentences with words.
        return all_sentences

    def get_dw_ds(self):
        return dwords, dseparators

    def stats(self):
        return self.nsentences, self.nwords, self.nsyllables

    def FRES(self):
        if self.nsyllables == 0:
            return 0.0
        # Flesch Reading Ease Score:  206.835 - 84.6 * ASW - 1.015 * ASL
        # ASW (avg. syl. per word) = #syllables / #words
        # ASL (avg. sentence length) = #words / #sentences
        return (206.835 - 84.6 * self.nsyllables / self.nwords
                - 1.015 * self.nwords / self.nsentences)

    def FK_grade(self):
        if self.nsyllables == 0:
            return 0.0
        # Flesch-Kincaid Grade Level: 0.39 * ASL + 11.8 * ASW - 15.59
        # ASL (avg. sentence length) = #words / #sentences
        # ASW (avg. syl. per word) = #syllables / #words
        return (0.39 * self.nwords / self.nsentences
                + 11.8 * self.nsyllables / self.nwords - 15.59)

    def Fog_index(self):
        if self.nsyllables == 0:
            return 0.0
        # Gunning Fog = 0.4 * ((words / sentence) + 100 (complex_words / words))
        # complex_words are words with more than two syllables.
        return 0.4 * (self.nwords / self.nsentences
                + 100 * self.hard_words / self.nwords)

    def SMOG_index(self):
        if self.nsyllables == 0:
            return 0.0
        # SMOG =1.043 * sqrt(30 * complex_words / sentences) + 3.1291
        # complex_words are words with more than two syllables.
        # (Note: use at least 30 sentences)
        if self.nsentences < 30:
            return -1.0
        return 1.043 * math.sqrt(30.0 * self.hard_words / self.nsentences) + 3.1291

    def Huerta_ease(self):
        if self.nsyllables == 0:
            return 0.0
        # From Huerta's original 1959 paper:
        #     Lect. = 206'84 - 0'60 P - 1'02 F.
        # Here, P is syllables per 100 words and F is sentences per 100 words.
        # This is equivalent to:
        # 206.84 - 60 * (syllables per word) - 102 (sentences per word)
        return (206.84 - 60.0 * self.nsyllables / self.nwords
                - 102.0 * self.nsentences / self.nwords)

    def Huerta_corrected(self):
        if self.nsyllables == 0:
            return 0.0
        # Huerta's original 1959 paper gives Flesch's Ease formula as:
        #     Lect. = 206'84 - 0,85 P - 1'02 F.
        # He then defines F as sentences per 100 words. This is a misstatement
        # (and rounding) of Flesch, for whom F is words per sentence.  (Note
        # Huerta's original formula favors longer sentences! That's the
        # opposite of Flesch's.) Correcting Huerta's formula to correspond to
        # Flesch (which Huerta obviously intended), we get (for Huerta):
        # 206.84 - 60 * (syllables per word) - 1.02 (words per sentence)
        return (206.84 - 60.0 * self.nsyllables / self.nwords
                - 1.02 * self.nwords / self.nsentences)

    def IFSZ_index(self):
        if self.nsyllables == 0:
            return 0.0
        # Formula de Perspicuidad (Clarity Formula) or Indice de Legibilidad de
        #   Flesch-Szigriszt (IFSZ, Flesch-Szigriszt Readability Index):

        # IFSZ = 206.835 - (62.3 x syllables / words) - words / sentences.
        # (This changes Flesch's coefficients from 84.6 to 62.3 and 1.015 to 1.)

        # From http://www.revespcardiol.org/en/the-quality-of-information-available/articulo/90027148/ :

        # Flesch-Szigriszt Index

        # The first formulas designed to analyze readability in the Spanish
        # language appeared in the 1950s. Several attempts have been made to
        # validate or adapt Flesch's original RES formula, such as the
        # Fernández-Huerta readability formula and the Szigriszt-Pazos clarity
        # formula. Without a doubt, the validation of the Flesch RES formula by
        # Szigriszt-Pazos should be considered the current reference for the
        # Spanish language. It is known as the Fórmula de Perspicuidad (Clarity
        # Formula) or Índice de Legibilidad de Flesch-Szigriszt (IFSZ,
        # Flesch-Szigriszt Readability Index):

        # IFSZ = 206.835 - (62.3 x syllables / words) - words / sentences.

        # As evaluated with this scale, the readability of a text with a score
        # of 50 to 65 is considered average, and as the score approaches 0,
        # where scientific literature is situated, texts become progressively
        # more difficult.

        return 206.835 - 62.3 * self.nsyllables / self.nwords - self.nwords / self.nsentences


    def Inflesz_scale(self):
        if self.nsyllables == 0:
            return 'UNDEFINED'
        # From http://www.revespcardiol.org/en/the-quality-of-information-available/articulo/90027148/ :

        # Inflesz Scale Grade

        # As was reported in the study by Barrio-Cantalejo et al.20 in 2008,
        # the Szigriszt Clarity Scale and the Flesch RES scale are not
        # appropriate for the reading habits of the Spanish population. The
        # authors of this study proposed the use of the new Inflesz scale,
        # which is a modification of both these scales for a more appropriate
        # assessment of texts in Spanish. On this scale, a score of 55 marks
        # the cut-off between a text that is accessible or not to an average
        # person. `Normal' is placed at a score of between 55 and 65, `very
        # difficult', between 0 and 40, and `somewhat difficult', between 40
        # and 55. Among the higher scores, `quite easy' is indicated by a score
        # of 65 to 80 and `very easy' by a score above 80.

        n = self.IFSZ_index()
        if n < 40:
            return 'very difficult'
        elif n <= 55:
            return 'somehwat difficult'
        elif n <= 65:
            return 'normal'
        elif n <= 80:
            return 'quite easy'
        else:
            return 'very easy'
