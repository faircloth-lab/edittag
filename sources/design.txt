.. _design:

**************************
Designing edit metric tags
**************************

You can design sequence tags of arbitrary length by invoking
``design_edit_metric_tags.py`` using something similar to the
following:

.. code-block:: bash

    design_edit_metric_tags.py \
        --tag-length=6 \
        --edit-distance=3 \
        --no-polybase \
        --gc \
        --comp \
        --min-and-greater

We describe each option (``design_edit_metric_tags.py --help``) in
detail, below.  We have separated these options into those pertinent to
:ref:`tag-design` and those for :ref:`tag-rescanning`.

.. _tag-design:

Tag design options
******************

--output=<FILE>  Path to the output file, in which to store the results 
  of a particular run.  When not provided, results are written to stdout.

--tag-length=<int>  Length of the desired sequence tag.  The results
  output depend on the interaction of `--tag-length` **and**
  `--edit-distance`:  you cannot design tags of greater edit distance than
  their `tag-length - 1`.  By default, there is always only one tag in the
  set where `--edit-distance = --tag-length`.

--edit-distance=<int>  Edit distance of the desired tag set.

--multiprocessing   Use multiple processors.  The number of
  cores/processors used is set by default to the max(cores) - 2.  You can
  explicitly set this option using --processors.

--processors=<int>  The number of computing cores/processors to use.
  This defaults to max(cores) - 2.

--no-polybase  Filter those tags having greater than two adjacent,
  identical bases. Homopolymer bases are problematic on certain
  sequencing platforms, thus it is useful to avoid homopolymer runs longer
  than three.

--gc  Filter those tags having 40 < GC % < 60.

--comp  Filter those tags that are perfect self-complements.  Generally,
  this option removes tags likely to form hairpins.

--hamming  Use Hamming distance in place of edit (Levenshtein) distance.

--min-and-greater  Return all tags at the minimum edit distance
  requested, and subsets of those tags falling within consecutively
  greater edit distance categories.  Thus, if you design 8 nucleotide,
  edit distance 3 tags and pass this option, the program will return all
  subsets of these tags having edit distances in the ``set([3,4,5,6,7])``.


.. _tag-rescanning:

Tag rescanning options
**********************

Tag rescanning is an option that you can use to design nested sets of
edit metric sequence tags.  "Nested" is likely the wrong word without
some context.  Essentially the rescanning option allows you to:

1. design a set of tags of ``--tag-length=<int>`` and
   ``--edit-distance=<int>`` 

2. select the subset of those tags where the first `x` bases **also**
   have a particular edit distance from one another

As an example, we designed a set of 10 nucleotide, edit metric sequence
tags of edit distance five.  Then we selected the subset of these 10
nucleotide tags where the first six nucleotides where also edit distance
three from one another.

This allows us an additional layer of protection, in case the index
sequencing step on certain platforms is not run for sufficiently long
(and only gathers data from the first six bases of the index instead of
all 10).  You can rescan a sequence tag file, outputting those tags
where the first six nucleotides are edit distance three from one another
using:

.. code-block:: bash

    python design_edit_metric_tags.py \
        --rescan my_file_to_rescan.txt \
        --edit-distance=3 \
        --min-and-greater \
        --rescan-length=6

--rescan=<FILE>  Path to the input file, containing edit metric sequence
  tags, that you wish you rescan.

--rescan-length=<int>  The (subset) number of nucleotides over which you
  wish to determine the nested edit distance.
