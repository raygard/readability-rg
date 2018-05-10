.. .. Default format for syntax highlighting is plain text.
.. highlight:: text

============
Introduction
============

Readability: A module for computing some readability metrics for English and Spanish text
-----------------------------------------------------------------------------------------

Several years ago I wanted to run some common readability measures on a large number of English and Spanish documents.
These measures, such as Flesch reading ease, Flesch-Kincaid grade level, SMOG, etc. have been used for years to gauge the approximate difficulty of reading text.
Most of the measures are quite old, dating to 1948 for Flesch reading ease, but are still in use.
Some have questioned the value of even attempting to evaluate readability in a mechanical fashion.
(See e.g. Geoffrey Marnell: Measuring Readability, retrieved 2018-04-20 at https://www.abelard.com.au/readability%20statistics.pdf.)

Nevertheless, there were people wanting to know the Flesch-Kincaid grade level of some documents in question.
We found that at least in the early days of Microsoft Word, the implementation of Flesch-Kincaid changed from one release of Word to the next, leaving us wondering how accurate any of them are.
Also, with Word it is unclear exactly what was considered a "sentence" for this purpose, or how accurately syllables were counted, etc.
I was unable to find suitable Python code to compute these measures, so I started to develop my own.
For various reasons this project was sidetracked before it was complete.
I recently have had some time to work on it again, at least to the point I feel ready to release it.

I also wanted to compute readability measures for Spanish text, so I also implemented the Fernandez Huerta measure, the Flesch-Szigriszt Readability Index, and the Inflesz Scale Grade.

.. note:: I have included PDF copies of most of the materials used or referenced in developing this project.

What it does
------------

The readability module can tokenize a document of Unicode text into words and sentences, and also count the syllables of the words, as needed for most common readability measures.
It can then report some common readability measures such as Flesch Reading Ease, Flesh-Kincaid grade level, SMOG, etc.

It can also show its work! It will return a list of sentences it has tokenized, optionally showing the syllable count for each word.

Another option is to have it return dictionaries of words and separators with frequency counts.

How it works
------------

The module defines a class ``Readability``.
To use it, you must create an instance for each document you want to process, then pass the text to its ``read()`` method.
The module uses a regular expression to tokenize the text into "words" and "separators".
The definition of a "word" includes numbers and URLs, and also includes some punctuation that may indicate the end of a sentence, such as ".", "?", and "!".
The module uses a heuristic routine to break the words and separators into sentences, and then uses a separate module to count the syllables in each word.
These functions are explained in more detail in the "Notes on development" section.
