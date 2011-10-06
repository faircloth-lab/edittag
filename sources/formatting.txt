.. _formatting:

*********************
Input file formatting
*********************

The input file **must** be formatted according to the following format, which is identical to the python `configuration file format <http://docs.python.org/library/configparser.html>`_, where each set of tags belongs to a particular *section*, denoted by square braces ``[]``.  

**All** file-based output from the process outlined in :ref:`design` follows these formatting conventions::

    [4nt ed3]
    Tag0:GTCA
    Tag1:AACC
    Tag2:ACAG
    Tag3:AGGA
    Tag4:CCTA
    Tag5:CGAT
    Tag6:TGTG

Input files may also be formatted using ``=`` in place of ``:``, lines starting with ``#`` or ``;`` are comments; and each tag can have trailing comments by appending a ``#`` ::

    [4nt ed3]
    # this is a comment
    Tag0 = GTCA
    Tag1 = AACC
    Tag2 = ACAG
    Tag3 = AGGA
    ; this is also a comment
    Tag4 = CCTA
    Tag5 = CGAT
    Tag6 = TGTG#this is a comment on a tag

Input files with several sections of tags look like the following - using a space to separate sections is optional::

    [4nt ed3]
    Tag0:GTCA
    Tag1:AACC
    Tag2:ACAG
    Tag3:AGGA
    Tag4:CCTA
    Tag5:CGAT
    Tag6:TGTG
    
    [5nt ed4]
    Tag0:TTGAC
    Tag1:AACAG
    Tag2:ACGCT
    Tag3:CAATC
    Tag4:CCTAA
    Tag5:GAGGA
    Tag6:GGTTG
    
    [6nt ed5]
    Tag0:TGTACG
    Tag1:AACAGC
    Tag2:AGGCTA
    Tag3:CCATTG
    Tag4:CTCGAA