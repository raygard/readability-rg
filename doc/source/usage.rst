.. .. Default format for syntax highlighting is python.
.. highlight:: python

.. _overview_toplevel:



===========
Quick start
===========

About the simplest example for the module may be:

.. code-block:: python

    import sys
    import re
    import readability

    r = readability.Readability()
    with open(sys.argv[1], encoding='UTF-8') as fp:
        a = r.read(re.split(r'\n(?:\s*\n)+', fp.read()))
    print('Flesh-Kincaid reading ease: %4.1f' % r.FRES())
    print('Flesh-Kincaid grade level:  %4.1f' % r.FK_grade())
    print('Gunning Fog index:          %4.1f' % r.Fog_index())
    print('SMOG index:                 %4.1f' % r.SMOG_index())
    print('%d sentences; %d words; %d syllables' % r.stats())

(Add ``import io`` and use ``io.open()`` if using Python 2.)

The ``re.split()`` is used to separate into chunks any text that is separated by one or more blank lines.
If this is not done, some text that spans paragraphs will be recognized as a single sentence.

Run against the Project Gutenberg text file for Sir Arthur Conan Doyle's "A Study in Scarlet", it produces this output:

.. code-block:: text

    Flesh-Kincaid reading ease: 74.4
    Flesh-Kincaid grade level:   6.9
    Gunning Fog index:           9.8
    SMOG index:                  9.7
    2738 sentences; 44132 words; 60559 syllables

(I used the text from http://www.gutenberg.org/files/244/244-0.txt dated 2016-09-30 and removed the front and end matter, including the transcriber's footnotes.)


============
Demo program
============

I have included a program ``rdblty.py`` in the source distribution and GitHub repo that demonstrates all or most of the features of the Readability class and its associated modules.
Its usage (command line) is:

.. code-block:: text

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


===================
Code files included
===================

|   readability.py - Main class module
|   syllable_count_eng.py - English syllable counter
|   syllable_count_eng_bf.py - English syllable counter with Bloom filter corrections
|   syllable_count_spa.py - Spanish syllable counter
|   Bloom_filter.py - Bloom filter code
|   Bloom_filter_data.py - Bloom filter data
|   
|   Bloom_filter_config.py - Bloom filter configuration
|   Bloom_filter_Hettinger.py - Raymond Hettinger's original Bloom filter (not used; included as documentation)
|   make_Bloom_filter.py - program to generate the Bloom filter data from the CMU Pronouncing Dictionary
|   make_cmudict_syllables.py - program to convert the CMU dictionary to JSON format

===============
Module contents
===============

Class
=====

readability()
-------------

.. #    class readability.Readability([get_sentences]
.. #            [, count_syllables] [, show_syllable_counts] [, dw] [, ds] [, language])

.. # This is a comment?
.. #   __init__(self, get_sentences=True,
                        count_syllables=True,
                        show_syllable_counts=False,
                        dw=None,
                        ds=None,
                        language="eng"):

The ``readability`` module defines a single class:

Readability([get_sentences_] [, count_syllables_] [, show_syllable_counts_] [, dw_] [, ds_] [, language_])

Use this to create a readability object to evaluate a single document.
The module may also be used to tokenize text into words and sentences without evaluating readability.

.. _get_sentences:

* get_sentences_ is a Boolean (default is ``True``).
  If True, the ``read()`` method will return the sentences it has tokenized from the text it is given, in the form of a list of lists of tokens, each list of tokens representing a sentence.

.. _count_syllables:

* count_syllables_ is a Boolean (default is ``True``).
  It must be ``True`` to get readability statistics.
  It may be ``False`` if, for example, you only need word and sentence counts.
  (But note that the word count will be differ depending on whether this is True or False; see below for more information.)

.. _show_syllable_counts:

* show_syllable_counts_ may be a boolean or a string; default is ``False``.
  This is only relevant if ``get_sentences`` is True.
  If ``show_syllable_counts`` is True, then the sentences returned by ``read()`` will have syllable counts embedded with each word, in the form "word{count}", e.g. "This{1} etext{2} is{1} prepared{2} directly{3}..."


    Alternatively, ``show_syllable_counts`` may be a format string.
    If it is a format string and it contains "word" and "count", the word and count will be formatted using::

        show_syllable_counts % dict(word=word, count=count)

    This may be used if you want to display the count in front of the word, e.g. ``"%(count)d|%(word)s"``.

    Otherwise the word and count will be formatted using::

        show_syllable_counts % (word, count)


.. _dw:

* dw_ may be a dictionary in which "words" are returned with a count of their occurrences; default is ``None``.
  If provided, it should be empty initially.

.. _ds:

* ds_ may be a dictionary in which "separators" are returned with a count of their occurrences; default is ``None``.
  If provided, it should be empty initially.

.. _language:

* language_ may be "eng" for English or "spa" for Spanish; the default is English.


More about "words"
------------------

The module tokenizes "words" based on a regular expression.
A word is, roughly, one of the following:

* a URL beginning http:// and including legal URL characters, but not ending with a period or comma.
  This is a very naive URL recognizer and will not always scan a URL perfectly.

* a word beginning with a letter and including letters, dots, ampersands, apostrophes, and hyphens, but not ending with an ampersand, apostrophe, or hyphen, nor can it contain adjacent dots, ampersands, apostrophes, or hyphens.

* a number beginning with a decimal digit and including digits, dots, commas, and hyphens, but ending with a digit.

* one or more periods

* one or more exclamation points

* one or more question marks.

The tokenizer will return periods, exclamation points, and question marks as "words" because it simplifies the work for the sentence boundary detector.

When the syllable counter is enabled (as it is by default), the module will only count as words those "words" that have a non-zero syllable count.
When the syllable counter is disabled, the module counts all tokenized words.

Everything that's not a "word" is a separator.
The tokenizer can return the separators as a dictionary with counts.
There will be a separator between every pair of words, so if two words are adjacent, the separator will be the empty string.



Methods
=======

read()
------

Use ``read(string)`` or ``read(list_of_string)`` to pass text to the module.
You should invoke ``read()`` only once per instance of the class.
If you have the entire text in a string, use the first form.
You may also pass a list of strings to the ``read()`` method.
All text should be Unicode.
If you use a list, each string in the list should contain only whole sentences.
The module is not able to merge partial sentences between one string and the next.

stats()
-------

``stats()`` returns a tuple ``(sentence_count, word_count, syllable_count)``.

.. note:: The following methods all return floating-point values, except for ``Inflesz_scale()``, which returns a string.

FRES()
------

``FRES()`` returns the Flesch Reading Ease Score.
The score is computed as:

 |  206.835 - 84.6 * syllables / words - 1.015 * words / sentences


FK_grade()
----------

``FL_grade()`` returns the Flesch-Kincaid Grade Level.
The score is computed as:

 |  Flesch-Kincaid Grade Level: 0.39 * words / sentences + 11.8 * syllables / words - 15.59


Fog_index()
-----------

``Fog_index()`` returns the Gunning Fog index.
The index is computed as:

 |  Gunning Fog = 0.4 * ((words / sentences) + 100 * (complex_words / words))
 |  where complex_words are words of more than two syllables.

SMOG_index()
------------

``SMOG_index()`` returns the SMOG index.
The index is computed as:

 |  SMOG =1.043 * sqrt(30 * complex_words / sentences) + 3.1291
 |  where complex_words are words of more than two syllables.

There should be a minimum of 30 sentences for the text sample.
If the number of sentences is less than 30, ``SMOG_index()`` returns -1.0.


Huerta_ease()
---------------

``Huerta_ease()`` is for Spanish text only.
See :ref:`spanish_notes`.
The score is computed as:

 |  206.84 - 60 * (syllables / words) - 102 (sentences / words)

This is equivalent to the formula given in Huerta's original 1959 paper:

 |  Lect. = 206'84 - 0'60 P - 1'02 F.
 |  Where P is syllables per 100 words and F is sentences per 100 words.


Huerta_corrected()
------------------

``Huerta_corrected()`` is for Spanish text only.
See :ref:`spanish_notes`.
The score is computed as:

 |  206.84 - 60 * (syllables / words) - 1.02 (words / sentences)


IFSZ_index()
------------

``IFSZ_index()`` is for Spanish text only.
Its full name is "Formula de Perspicuidad (Clarity Formula) or Indice de Legibilidad de Flesch-Szigriszt (IFSZ, Flesch-Szigriszt Readability Index)".
See :ref:`spanish_notes`.
The score is computed as:

 |  IFSZ = 206.835 - (62.3 x syllables / words) - words / sentences.


Inflesz_scale()
---------------

``Inflesz_scale()`` is for Spanish text only.
See :ref:`spanish_notes`.
This method returns one of "UNDEFINED", "very easy", "quite easy", "normal", "somewhat difficult", and "very difficult", depending on the text's ``IFSZ_index()`` score.

