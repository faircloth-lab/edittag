.. _using_adapters:

*******************************************
Adding sequence tags to sequencing adapters
*******************************************

We provide an extremely simple program for integrating sequence tags, output by
``design_edit_metric_sequence_tags.py``, to sequencing adapters.  This program
is largely meant for cases where you need to consistently add many sequence
tags to a single adapter.  The program is invoked as follows and output is sent
to stdout:

.. code-block:: bash

        python add_tags_to_adapters.py \
            --input=test-data/edit_metric_tags.conf
            --5prime=CAAGCAGAAGACGGCATACGAGA 
            --3prime=TGACTGGAGTTC \
            --section='5nt ed3' 


Options
-------

--input=<FILE>  The input file to check.  The format must follow guidelines in
  :ref:`formatting`.

--5-prime=<string>  The adapter sequence 5' of the sequence tag.

--3-prime=<string>  The adapter sequence 3' of the sequence tag.

--section=<string>  The section of tags to apply to the adapter sequence.  Used
  when an input file contains many sections of tags, and you only want to check
  one.  When the input file contains multiple sections, and you do not pass this
  option, the program will output adapters with all the sequence tags in

--revcomp  Add the reverse complement of the sequence tag rather than the
  forward complement.

--suppress-orientation  Suppress pretty printing of the results to stdout and
  just return the adapter sequences.

Output
------

Results written to stdout have the following appearance.  Notice that the
integrated tag sequence is converted to lower-case:

.. code-block:: none

    [4nt ed3]
        5' - AAAAgtcaGGGG - 3'
        5' - AAAAaaccGGGG - 3'
        5' - AAAAacagGGGG - 3'
        5' - AAAAaggaGGGG - 3'
        5' - AAAAcctaGGGG - 3'
        5' - AAAAcgatGGGG - 3'
        5' - AAAAtgtgGGGG - 3'

To write results to an output file, you can just use redirection:

.. code-block:: bash

    python add_tags_to_adapters.py \
            --input=test-data/edit_metric_tags.conf
            --5prime=CAAGCAGAAGACGGCATACGAGA 
            --3prime=TGACTGGAGTTC \
            --section='5nt ed3' > my_output_file.txt


