.. .. Default format for syntax highlighting is plain text.
.. highlight:: text

====================
Notes on development
====================


Sentences, words, and syllables
===============================

I looked for some time for Python code to compute common readability measures, and was not satisfied with what little I found, so I wrote this module.

Readability measures are language specific, and I am primarily interested in scoring English and Spanish text, so these remarks address those languages.

Most readability scores are based on sentence length and word complexity, usually based on syllables per word, so we need to break text
into words and sentences and count the syllables in each word.


Word and sentence detection
===========================

Computational linguists have done some work on word and sentence breaking (or more formally, sentence boundary detection).
See e.g.

| Grefenstette, G. and Tapanainen, P.: What is a word, what is a sentence? problems of tokenization (1994)
| http://www.georgetown.edu/faculty/wilsong/IR/grefenstette94.pdf

| Kiss & Strunk: Unsupervised Multilingual Sentence Boundary Detection (2006)
| http://www.linguistics.ruhr-uni-bochum.de/~kiss/publications/compling2005_KS27.01final.pdf

For my application, I've found that regular expressions are satisfactory for
tokenizing text into words.
Finding suitable expressions was at least partly a
matter of trial and error.

The main difficulty in sentence breaking is the ambiguity of the period (dot) character.
It usually indicates the end of a sentence, at least when it follows a non-space and is followed by a space, especially when the next non-space is uppercase.
If the next non-space is lowercase, the period usually has followed an abbreviation.
If the next non-space is uppercase, the period may also have come after a form of address such as Mr., Mrs., or Dr.

The Python Natural Language Toolkit includes a sentence breaker called Punkt, which was the product of the research reported in the Kiss & Strunk paper cited above.
Punkt is considered a fairly good sentence breaker, and the NLTK is wonderful, but I wanted something lightweight that would not require using the NLTK.
I used Punkt as a standard of comparison as I developed my own sentence breaker, and I think my simple approach stands up pretty well against Punkt.


Developing an English syllable counter
======================================

Counting syllables in English words by means of an algorithm is difficult.
Looking around the Web, you'll find that most of the available code is based on a Perl module Syllable.pm by Greg Fast, last updated in 1998.
I started to write a Python adaptation of Syllable.pm, but wanted to use a different license.
I managed to contact Greg Fast and have his permission to release my Python code, modelled on his Perl code, with an MIT license.

The approach I've taken is similar to Greg's.
Note that most final "e"s don't contribute to a syllable count, so remove them before going farther.
Each syllable generally contains one or more vowels, so start by counting runs of vowels in the word.

The next step is to see what's wrong with the counts, and find ways to adjust them.
Nearly all the incorrect counts are off by one syllable.
Look for patterns prevalent in the incorrectly counted words and find regular expressions to indicate when a count should be incremented or decremented.

It's very useful to have a set of words with known correct syllable counts to use as a basis for development.

.. .. .. _posted some code: https://groups.google.com/group/nltk-users/msg/81e70cb6704dc01e
.. _posted some code: https://groups.google.com/forum/#!msg/nltk-users/mCOh_u7V8_I/HsBNcLYM54EJ

In September 2009, Jordan Boyd-Graber `posted some code`_ on the nltk-users Google group.
He observed that the The Carnegie Mellon Pronouncing Dictionary (cmudict) contains the information needed to count the syllables in its words.
Each vowel phoneme ends with a digit that indicates the stress, and counting the letter groups that end with digits gives an
accurate count of the syllables.
His code is:

.. code-block:: python

    import curses 
    from curses.ascii import isdigit 
    import nltk 
    from nltk.corpus import cmudict 
    d = cmudict.dict() 
    def nsyl(word): 
      return [len(list(y for y in x if isdigit(y[-1]))) for x in d[word.lower()]] 

Instead of nltk, I used the most recent cmudict.dict from https://github.com/cmusphinx/cmudict (dated 2018-01-29 at this writing) and used ``num_syllables = len(re.sub(r'[^0-9]', '', pronunciation))`` after separating the word and its pronunciation in the dictionary entry.

I used this to create a Python dict of words and syllable counts.
Then, running those words through the syllable counter, I wrote out lists of words that were counted correctly, over by 1 syllable, under by 1 syllable, over by 2 syllables, etc.
I examined the words in the error lists.
I first noticed that many of the overcounts were words ending in "ed" where the "ed" did not contribute to the count.
This was usually when the "ed" was preceded by certain letters and not others, such as the "ned" ending in "banned" or "frowned".
After decrementing the counts for words matching "[cfhklmnprsvwxz]ed$", I reduced the error counts significantly.

I found so few words off by more than one that I did not address those at all.

I continued to examine the lists of overcounts and undercounts, looking for patterns (usually vowel sequences) that occurred frequently, and comparing their contexts in the over/undercount lists with the contexts of the same patterns in the correctly-counted list.
By carefully adding patterns to the increment-pattern and decrement-pattern lists, I was able to reduce the errors on the CMU word list until it was under 10%.

I also made a list of words from the Brown corpus, sorted by frequency, and observed the error counts for those words that were also in the CMU dictionary.
I considered it more important to reduce the errors for these more common words, especially the top 10,000 or so, than for the CMU dictionary as a whole.
My syllable counter does quite a bit better on those than on the entire dictionary.

I also considered it useful to try to keep the overcounts and undercounts as balanced as I reasonably could.
The idea is that for words that are not in my test set, I want to get the overcounts and undercounts to even out.

Finally, I used Raymond Hettinger's Bloom filter recipe to make :ref:`Bloom_filters` for the words in the CMU dictionary that were still overcounted or undercounted by one.
After setting up the Bloom filters, all those words are now counted correctly.
Since the Bloom filters have a predictable percentage of false positives, I am also now incorrectly correcting a tiny percentage (less than 0.1%) of words that come into the syllable counter.

The Bloom filters add about 27 kb space overhead for the data and a bit for the code as well.
They also add a bit of processing time for each word, but I think the performance hit is worthwhile.
In any case, I have included versions of the syllable counter both with and without the Bloom filters.

.. _Bloom_filters:

Bloom filters
=============

A Bloom filter is a data structure and algorithm that supports a probabilistic test for set membership.
Keys are hashed into a bit table using several hash functions.
The table is initially empty (all bits 0).
For each key entered into the table, each bit it hashes to with each of the hash functions is set to 1.
To see if a key is in the set, hash the key with each hash function and see if all the corresponding bits are 1.
If not, the key is definitely not in the set; there can be no false negatives.
If they are all 1, then the key may be in the set.
If the key is in the set, this is a true positive, otherwise it's a false positive.

The probability of a false positive can be made arbitrarily small by choosing the table size and number of hash functions properly.
The hash functions must also be independent of one another and of high quality (uniform "random" distribution over the bit table) to achieve the best performance.

The table size can be relatively small compared with the number of keys in the set to be queried, because the keys are not stored.
Only a few bits per key need to be set in the table to achieve good performance, and the table size in bits needs to be only a small multiple of the number of keys to get a reasonably low probability of false positives.

A typical application is one where you may want to see if a key is probably in a set before doing a more expensive lookup, such as a disk read or a query over a network.
In the present application, we are looking to see if a word should have its syllable count adjusted up or down.
A few errors are acceptable here.

Raymond Hettinger posted a very compact Bloom filter implementation in pure
Python to the ActiveState Python Cookbook
(http://code.activestate.com/recipes/577684-bloom-filter/).

Rather than using several separate hash functions, Hettinger's code uses the Python library pseudorandom number generator to create several probes from a single initial hash.
The Python library uses the Mersenne Twister PRNG and so gets excellent independence of the probes for each key.
Hettinger achieves results about as good as one can expect theoretically.

I wanted to adapt this to the (English) syllable counter, but also wanted to be able to distribute the code and the tables pre-built in a way that would work across Python implementations.
Hettinger uses the poorly documented ``random.Random()`` class to seed the PRNG, which has a different implementation between Python 2.7.14 and Python 3.6.4, and I am not sure it will not change again with later versions or different implementations.
I'm also not clear on whether the Mersenne Twister implementation (generating floating point values in [0.0, 1.0)) will generate the same sequence from a seed in all implementations.

So I needed to find a way to use the filter with some hashes that would be consistent across implementations.
According to a paper by Kirsh and Mitzenmacher, a Bloom filter should work well with only two hash functions g() and h(), making the probes at g(k)+i*h(k) mod m for i in [0, k-1], m bits in the table.

I needed two fast hash functions, and I wanted something that was available in the Python standard library.
Though the Python documentation says its crc32() and adler32() "is not suitable for use as a general hash algorithm", I found they gives acceptable results for this application.
If you want something better at the cost of filter table portability, you could use Hettinger's original ``get_probes()``, or use some other hash functions in the Python Package Index and elsewhere.

Note that we need to mask the crc32() and adler32() values with 0xffffffff to guarantee the same results across implementations.
I multiplied the results of each hash by a couple of primes that resulted in fewer false positives on words from the CMU dictionary.
These primes were determined by trial and error and are probably not optimal.

I also experimented with an approach using only crc32(), making the table size m be the larger of twin primes.
The initial probe is made at crc32(key) mod m, and subsequent probes are made at intervals of (crc32(key) mod (m-2) + 1) away from the initial probe.
This also seems to give acceptable results in this application, but I have not retained this implementation.
But I did keep the twin prime calculation in the ``Bloom_filter_config.py`` program, though it is not necessary to use twin primes in the current implementation.

These approaches may not be good enough for general use however.
I did some further experiments with these probe protocols and a number of other similar versions.
Though the two methods above usually performed pretty well, the Mersenne Twister based method performed very well in nearly all cases, and almost always better than the two-hash and one-hash-twinprime approaches.
And the latter two approaches performed quite a bit worse than the Mersenne Twister method with a small number of keys in an optimally loaded (50%) table.

References:

Burton H. Bloom: Space/Time Trade-offs in Hash Coding with Allowable Errors, Communications of the ACM, Vol. 13 No. 7, July, 1970, pp. 422-426. Accessed 2018-04-22 from http://www.ece.cmu.edu/~ece447/s13/lib/exe/fetch.php?media=p422-bloom.pdf.

Kirsch and Mitzenmacher: Less Hashing, Same Performance: Building a Better Bloom Filter (2006). Accessed 2018-04-22 from http://astrometry.net/svn/trunk/documents/papers/dstn-review/papers/kirsch2006.pdf.


