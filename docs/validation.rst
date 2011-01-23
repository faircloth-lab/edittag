.. validating:

***************************
Validating edit metric tags
***************************

Validating a set of sequence tags takes an easily formatted file as input and returns the edit distances between sets of tags within the input.  You can validate a set of sequence tags by invoking ``validate_edit_metric_tags.py`` as follows::

    python validate_edit_metric_tags.py --input test-data/edit_metric_tags.txt \
        --section '5nt ed3'

Options
*******

``--input=<FILE>`` : The input file to check.  The format must follow guidelines in :ref:`formatting`.

``--section=<string>`` : The section of tags to check.  Used when an input file contains many sections of tags, and you only want to check one.  When the input file contains multiple sections, and you do not pass this option, the program will check all sections.  This may cause slow responses.

``--minimums`` : Default behavior.  Computes and returns the minimum edit distance in each set of tags.

``--all-distances`` : Compute and return minimum, mode, and maximum edit distance in each set of tags.  Also returns a table denoting the distribution of sequence tags into edit distance categories.

``--verbose`` : When used with ``--minimums``, returns the pairwise comparisons of tags having the minimum edit distance from one another.  When used with ``--all-distances``, returns the pairwise comparisons of tags having any edit distance.  When used alone, defaults to returning the pairwise comparisons of tags having the minimum edit distance.