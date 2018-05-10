.. .. Default format for syntax highlighting is plain text.
.. .. highlight:: text

.. _spanish_notes:


==============================
Notes on Spanish functionality
==============================


Syllabification
===============

I was able to develop a syllable counter for Spanish in a more straightforward manner than was the case for English.
Spanish follows regular rules for syllabification.
I count runs of vowels and then adjust for those runs that form two vowel sounds.
After counting vowels of several hundred frequent words in a small Spanish corpus, I had someone fluent in Spanish check the counts and she found that they were all correct.
The counter may not be perfect but it is good enough and quite a bit better than the English syllable counter.

My code is based on:

Humphries, Glenn: Syllabification: The Division of Words into Syllables. http://glenn.humphries.com/Notebook/toc.htm

But this page is no longer available.

This Web page is also referenced in:

Cuayáhuitl, Heriberto: A Syllabification Algorithm for Spanish, in Computational Linguistics and Intelligent Text Processing, 5th International Conference, CICLing 2004 Seoul, Korea, February 15-21, 2004 Proceedings, published as Lecture Notes in Computer Science (LNCS) vol. 2945 (Springer), pp. 412-415.

As of this writing, it can be found at https://pdfs.semanticscholar.org/51a1/5db989f4b62a2beb725d71e5db2d210d6141.pdf,
or you can read it via the "preview" at https://link.springer.com/chapter/10.1007%2F978-3-540-24630-5_49.

This is a more formal description of a Spanish syllabification algorithm that is based on that in the no-longer-existing page.
I have not compared it with the Humphries Web page or attempted to implement it.

Tokenization and sentence boundary detection
============================================

I use the same code for tokenization and sentence boundary detection for both English and Spanish.


Spanish readability measures
============================

The study of readability or legibility measures for Spanish apparently began with the 1959 paper of Jose Fernández Huerta, "Medidas sencillas de lecturabilidad" ("Simple Measures of Readability"), *Consigna* 214, 29-32.
Huerta adapted Flesch's formula by slightly changing the coefficients, and his formula was the most often used method of evaluating readability of Spanish text for many years.

But there are serious problems with Huerta's formula.
In 2007, Inés Mª Barrio Cantalejo produced her PhD thesis, "Legibilidad y salud: los métodos de medición de la legibilidad y su aplicación al diseño de folletos educativos sobre salud", in which she criticized Huerta's approach for not explaining his methodology for adjusting Flesch's formula and for not validating his table showing what scores correspond to what difficulty levels.
A more severe problem was noticed by Gwillim Law (see https://linguistlist.org/issues/22/22-2332.html), who observed that Huerta *inverted* the meaning of one of the terms of Flesch's formula.
Huerta cited the **F** term in Flesch, which is words per sentence, as sentences per 100 words.
This completely changes the direction of the readability score, from more words per sentence causing a lower readability to more words per sentence causing a higher readability, which is intuitively wrong.
Huerta also took liberties with the original Flesch values, rounding the original 206.835, 0.846, and 1.015 to 206.84, 0.85, and 1.02 respectively, but this is a minor change compared to inverting the meaning of the last term.
(One may also wonder whether there was ever any value of using terms precise to six significant figures, or five figures as in the SMOG index formula, when the resulting readability value can only be a rough guide in any case.)

So in addition to the ``Huerta_ease()`` method, I have also included ``Huerta_corrected()`` which uses 1.02 words per sentence in place of 102 sentences per word (same as 1.02 sentences per 100 words).

Barrio Cantalejo's thesis strongly supports the use (in place of Huerta) of the work of Francisco Szigriszt Pazos, who attempted to produce adjustments to Flesch's formula in a more scientific (rigorous?) manner.
Szigrist's "Perspicuity Formula" is 206.835 - 62.3 syllables/word - words/sentence.
This is referred to by Barrio Cantelejo as Formula de Perspicuidad (Clarity Formula) or Indice de Legibilidad de Flesch-Szigriszt (IFSZ, Flesch-Szigriszt Readability Index).
We implement this as the IFSZ_index() method in Readability().

Barrio Cantalejo's thesis also provides a difficulty scale she refers to as Inflesz Scale Grade (Grado en la escala INFLESZ).
The scale has five difficulty grades based on the IFSZ index: < 40 very difficult; 40-55 difficult; 55-65 difficult; 65-80 quite easy; > 80 very easy.
It is unclear which category borderline values 55 and 65 fall in.
I have implemented the Inflesz_scale() method as::

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

