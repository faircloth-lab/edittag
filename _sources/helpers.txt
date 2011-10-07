.. _helpers:

**************************
Additional helper programs
**************************

Estimating the effects of sequencing error
==========================================

We provide a program that we used to generate the simulation results presented
in Figure 1 of [Faircloth:2011]_.  This program makes the simplifying
assumption that sequencing errors are uniformly distributed and that they also
follow a Bernoulli process.  Thus one can think of modeling sequencing error
across a sequence tag of particular length as a binomial trial.  We use
multiprocessing to speed individual runs, such that we can generate thousands
of iterations of sequencing runs returning millions of reads.  To invoke the
program:

.. code-block:: bash

    python estimate_sequencing_error_effects.py \
        --read-count=1000000 \
        --output=1M_reads_error_5_barcode_8nt_1000_iter.out \
        --barcode-length=8 \
        --iterations=1000 \
        --error-rate=0.05

Options
-------

--error-rate=<float>  The error rate to simulate.

--output=FILE  The path to the output file.

--read-count=<int>  The read count to simulate.

--barcode-length=<int>  The barcode length to simulate.

--iterations=<int>  The number of sequencing runs to simulate.  Typically 1000.

Output
------

Output files are sparsely formatted with no header (added below as a comment to
illustrate the column content). The values returned are number of reads in each
category:

.. code-block:: none

    #0 error, 1 error, 2 error, 3 error, 4 error, 5 error, 6 error, 7 error
    941471,57167,1345,17,0,0,0,0
    941547,56940,1491,22,0,0,0,0
    941633,56969,1383,15,0,0,0,0
    941610,56946,1423,21,0,0,0,0
    941433,57123,1419,25,0,0,0,0
    941684,56816,1485,15,0,0,0,0
    941674,56889,1422,15,0,0,0,0
    941641,56923,1422,14,0,0,0,0

.. _flows:

Determining the number of flows per sequence tag
================================================

This program returns the number of flows required to sequence input sequence
tags:

.. code-block:: bash

    python get_tag_flows_for_454.py \
        --input edittag/test-data/edit_metric_tags.txt \
        --section '4nt ed3'

Options
-------

--input=<FILE>  The input file to check.  The format must follow guidelines in
  :ref:`formatting`.

--section=<string>  The section of tags to apply to the adapter sequence.  Used
  when an input file contains many sections of tags, and you only want to check
  one.  When the input file contains multiple sections, and you do not pass this
  option, the program will output adapters with all the sequence tags in
  ``--input``.

Output
------

Output is sent to standard out, and reports the tag name, tag sequence, and
number of flows for the section(s) passed as options:

.. code-block:: none

        tag4	CCTA	9
        tag5	CGAT	10
        tag6	TGTG	10
        tag0	GTCA	10
        tag1	AACC	10
        tag2	ACAG	11
        tag3	AGGA	12

