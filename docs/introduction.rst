************
Introduction
************

Purpose
=======

edittag_ is a suite of programs for designing, checking, and using sets
of sequence tags that conform to the edit metric.  Here, we define these
sets as the groups of sequence tags of a particular length where all
tags within the set are **at least** the select edit (Levenshtein)
distance [Levenshtein:1966]_, [Gusfield:1999]_ from one another.  

At a more general level, edittag_ contains tools facilitating high
levels of plexity during massively parallel DNA sequencing runs.

Using edittag_, we have generated several large sets of edit metric
sequence tags from four to 10 nucleotides in length and ranging from
edit distance three to nine.  We provide these pre-generated tag sets
under a `Creative Commons Attribution 3.0 United States
<http://creativecommons.org/licenses/by/3.0/us/>`_ license in several
forms:

* `CSV file <https://github.com/downloads/faircloth-lab/edittag/edit_metric_tags.csv>`_
* `TXT file <https://github.com/downloads/faircloth-lab/edittag/edit_metric_tags.txt>`_
* `MS Excel xls file <https://github.com/downloads/faircloth-lab/edittag/edit_metric_tags.xls.zip>`_
* `sqlite database <https://github.com/downloads/faircloth-lab/edittag/edit_metric_tags.sqlite.zip>`_

Features
========

* edittag_ correctly designs sequence tag sets conforming to the edit metric

* edittag_ contains a method to test designed sets (from edittag_ or
  elsewhere) for conformance to the edit metric (and/or the Hamming
  distance [Hamming:1950]_ between sequence tags)

* edittag_ provides several programs for integrating sequence tags to
  primers and sequencing adapters

* edittag_ uses multiprocessing to speed computation, particularly when
  designing sequence tags of arbitrary length

* edittag_ provides unittests of critical code (edit distance
  computation) and output to ensure underlying methods return expected
  results

Availability
============

We provide several methods of installing eddittag, see
:ref:`installation` for additional details:

Dependencies
============

* `python 2.7.x <http://www.python.org>`_
* `numpy 1.5.x <http://numpy.scipy.org>`_

Optional
--------

* `py-levenshtein <http://pypi.python.org/pypi/python-Levenshtein/>`_
* `mod-primer3 <https://github.com/faircloth-lab/mod-primer3>`_

Although optional, we **strongly** recommend installation of
py-levenshtein, which is a C-module for python that speeds computation
of the Levenshtein distance between strings.

.. _edittag: https://github.com/faircloth-lab/edittag/
