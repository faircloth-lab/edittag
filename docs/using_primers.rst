.. _using_primers:

***********************************
Adding sequence tags to PCR primers
***********************************

There are several ways to incorporate sequence tags to PCR primers.  In certain
cases, you may just add each sequence tag to the 5' end of the forward &
reverse primers.  However, this can introduce unintended secondary structure to
each primer (hairpins) or the combination of primers (complementarity),
particularly when integrating sequence tags longer than four to five
nucleotides.

We provide a program that integrates sequence tags to upper and lower PCR
primers using a `modified version of primer3 2.2.3
<https://github.com/BadDNA/mod-primer3>`_ (modified to evaluate longer
primers).  

.. note::

    To enable this functionality, you must download, build, and install a
    copy of ``mod-primer3``.  For instructions on doing this, see
    :ref:`mod-primer_installation`.

If requested, this program will also remove common bases between
tags and primers and integrate ``GTTT`` pigtails to the 5' ends of the upper
and lower primer to encourage ``+A`` addition by *Taq* polymerase, which may be
useful in certain contexts.

.. note::

    As part of the processing undertaken by this program, it will also
    compute a value, recorded in the ``values`` column of the
    output/database which reports the number of flows required to
    sequence a particular tag using the 454 platform.  We also include
    this functionality separate in :ref:`flows`.

Finally, this program stores all tagged primers in an `sqlite
<http://www.sqlite.org>`_ database (and csv output file), with which you
can easily sort output primers and from which you can easily select sets
of primers meeting certain criteria, including random sets of primers
for testing purposes.

You can invoke ``add_tags_to_primers.py`` using a command similar to the
following:

.. code-block:: bash

    python add_tags_to_primers.py --input 10_nt_ed_5_tags.txt \
        --left-primer=GTTATGCATGAACGTAATGCTC 
        --right-primer=CGCGCATGGTGGATTCACAATCC \
        --output trnH_tagged_with_10_nt_ed_5_tags.csv \
        --sort=pair_hairpin_either,pair_penalty,cycles 
        --remove-common --keep-database

Options
*******

--input=FILE  The input file to check.  The format must follow
  guidelines in :ref:`formatting`.

--section=<string>  The section of tags to check.  Used when
  an input file contains many sections of tags, and you only want to check
  one.  When the input file contains multiple sections, and you do not
  pass this option, the program will check all sections.  This may cause
  slow responses.

--left-primer=<string>  The left primer sequence to tag.

--right-primer=<string>  The right primer sequence to tag.

--output=<string>  The path and name of an output file.  If you do not
  pass ``--keep-database``, this will be the path to the output file in
  CSV format.  If you do pass ``--keep-database``, this will become the
  name of and path to your database, to which the program will append
  ``.sqlite``.

--pigtail  Add a "pigtail" to each tagged primer sequence.

--pigtail-sequence=<string>  The pigtail sequence to add.  Defaults to
  ``GTTT`` [Brownstein:1996]_.

--sort=<string>  Comma-separated list of columns on which to sort the
  contents of ``--output=<FILE>``, if passed as an option.  The string
  should be formatted as above::

    --sort=pair_hairpin_either,pair_penalty,cycles

  and valid options include one or more of the following::

    id, unmodified, tag, cycles, left_tag_common, left_tag, left_sequence, 
    left_tm, left_gc, left_self_end, left_self_any, left_hairpin, 
    left_end_stability, left_penalty, left_problems, right_tag_common, 
    right_tag, right_sequence, right_tm, right_gc, right_self_end, 
    right_self_any, right_hairpin, right_end_stability, right_penalty, 
    right_problems, pair_compl_end, pair_compl_any, pair_hairpin_either, 
    pair_penalty

--remove-common  Remove common bases btw. pigtail and tag

--keep-database  Keep the sqlite database produced in the current
  directory.  Useful for sorting and selecting large groups of tagged
  primers.

Output
******

If you pass the ``--output=my_output_file.txt``, the result of the run
will be saved in a CSV-formatted text file.  You can open this text file
with many spreadsheet and database programs.

Querying the database
*********************

Here follows a (very) brief introduction to `sqlite <http://www.sqlite.org>`_
and constructing queries of the output data.  For more information, see
`sqlite.org <http://www.sqlite.org/sqlite.html>`_.

.. note::

    Below, I have used the convention, in `Structured Query Language (SQL)
    <http://en.wikipedia.org/wiki/SQL>`_, of capitalizing statements (e.g.
    SELECT, ORDER BY, LIMIT, ASC, etc.).  This is **not** required to construct
    a valid query.


Start sqlite from your command-line interface:

.. code-block:: bash

    [~] sqlite my_very_first_database.sqlite
    SQLite version 3.7.3
    Enter ".help" for instructions
    Enter SQL statements terminated with a ";"

Look at help, then set some helpful output parameters.  Feel free
to play around with options here:

.. code-block:: sql

    sqlite> .help
    sqlite> .mode column
    sqlite> .headers on
    /* see what tables we have */
    sqlite> .tables
    primers
    /* show the columns in `primers` table */
    sqlite> .schema primers

Now that we know what columns are in the ``primers`` table, we can query data from the database.
For instance, get the first 5 primers in the table:

.. code-block:: sql

    sqlite> SELECT id, tag, left_sequence, right_sequence, 
       ...> pair_penalty AS pp FROM primers LIMIT 5;
    
    id          tag         left_sequence           right_sequence        pp        
    ----------  ----------  ----------------------  --------------------  ----------
    1                       GTTATGCATGAACGTAATGCTC  CGCATGGTGGATTCACAATC  6.777033  
    2           TTCTCCTTCA  GTTTCTCCTTCAGTTATGCATG  GTTTCTCCTTCACGCATGGT  41.657069 
    3           ACCTTACCTT  GTTTACCTTACCTTGTTATGCA  GTTTACCTTACCTTCGCATG  45.328737 
    4           CATTCCTCTA  GTTTCATTCCTCTAGTTATGCA  GTTTCATTCCTCTACGCATG  45.076019 
    5           TGTCATTCCT  GTTTGTCATTCCTGTTATGCAT  GTTTGTCATTCCTCGCATGG  44.361076 
    

You may notice the primer having ``id = 1`` has no tag.  That is because
this is the *untagged* primer sequence, which we include for the sake
of comparison with derived metrics for each tagged primer.

.. warning::

    sqlite will often truncate primer sequences in ``.mode column``
    because of the default column width settings (``.width``).  You
    should notice, above, that the values in ``left_sequence`` and
    ``right_sequence`` are **not** the entire primer sequences - *they
    have been truncated*.  One way to fix this problem is to make sure
    you run ``.mode csv`` before you copy and paste **any** primer
    sequences for ordering.  Another way to fix that problem is to write
    the query results to a file, after switching to CSV mode.  See below
    for examples.

Now, let's get some more primer sequences...

In the first example, we are going to grab two primer sequences (for the
sake of minimal output).  However, before we grab those two, we are
going to:

1. ignore those primers with hairpins ``pair_hairpin_either = 0``.
   Primers with potential hairpins are assigned a value of ``1`` (TRUE)
   in this column.  Primers without hairpins are assigned a ``0``
   (FALSE).

2. sort on ``pair_penalty`` (this is the ``ORDER BY
   pair_penalty ASC`` portion of the query).  ``pair_penalty`` is a bad
   thing, and as the value for this column gets higher, the primers are
   "worse".  So, we want primers with the lowest ``pair_penalty``
   possible - thus we sort on this column, and grab those primers within
   minimal values for ``pair_penalty``.

So, select 2 primer sequences from table where there are no hairpins and
with the lowest total penalties (i,e. from best to worst):

.. code-block:: sql
    
    sqlite> SELECT id, tag, left_sequence, right_sequence FROM primers WHERE
       ...> pair_hairpin_either = 0 ORDER BY pair_penalty ASC LIMIT 2;
    
    id          tag         left_sequence                         right_sequence                   
    ----------  ----------  ------------------------------------  ---------------------------------
    35          CCATATGAAC  GTTTCCATATGAACGTTATGCATGAACGTAATGCTC  GTTTCCATATGAACGCATGGTGGATTCACAATC
    36          CGGAACTTAT  GTTTCGGAACTTATGTTATGCATGAACGTAATGCTC  GTTTCGGAACTTATCGCATGGTGGATTCACAAT


Now, we're just going to grab some random primers that do not have
hairpins for testing.  After testing, we may remove the ``ORDER BY
RANDOM() LIMIT 5`` portion of the query to grab all those primers with
no hairpins (e.g. for ordering):

.. code-block:: sql
    
    /* select a random set of 5 primers having no hairpins */
    
    sqlite> SELECT id, tag, left_sequence, right_sequence FROM primers WHERE
       ...> pair_hairpin_either = 0 ORDER BY RANDOM() LIMIT 5;
    
    id          tag         left_sequence                         right_sequence                   
    ----------  ----------  ------------------------------------  ---------------------------------
    35          CCATATGAAC  GTTTCCATATGAACGTTATGCATGAACGTAATGCTC  GTTTCCATATGAACGCATGGTGGATTCACAATC
    147         CCGGTGGAAT  GTTTCCGGTGGAATGTTATGCATGAACGTAATGCTC  GTTTCCGGTGGAATCGCATGGTGGATTCACAAT
    146         CCGAACAGTG  GTTTCCGAACAGTGTTATGCATGAACGTAATGCTC   GTTTCCGAACAGTGCGCATGGTGGATTCACAAT
    151         GGAAGACCTC  GTTTGGAAGACCTCGTTATGCATGAACGTAATGCTC  GTTTGGAAGACCTCGCATGGTGGATTCACAATC
    36          CGGAACTTAT  GTTTCGGAACTTATGTTATGCATGAACGTAATGCTC  GTTTCGGAACTTATCGCATGGTGGATTCACAAT
    
    /* Before we order these primers for testing, ensure we have no truncation issues.  
    Set mode to CSV, and re-run query before copying and pasting */
    
    sqlite> .mode csv
    sqlite> SELECT id, tag, left_sequence, right_sequence FROM primers WHERE
       ...> pair_hairpin_either = 0 ORDER BY RANDOM() LIMIT 5;
    
    id,tag,left_sequence,right_sequence
    133,GCCTTCAGGA,GTTTGCCTTCAGGAGTTATGCATGAACGTAATGCTC,GTTTGCCTTCAGGACGCATGGTGGATTCACAATC
    36,CGGAACTTAT,GTTTCGGAACTTATGTTATGCATGAACGTAATGCTC,GTTTCGGAACTTATCGCATGGTGGATTCACAATC
    147,CCGGTGGAAT,GTTTCCGGTGGAATGTTATGCATGAACGTAATGCTC,GTTTCCGGTGGAATCGCATGGTGGATTCACAATC
    130,CGTCAAGAAG,GTTTCGTCAAGAAGTTATGCATGAACGTAATGCTC,GTTTCGTCAAGAAGCGCATGGTGGATTCACAATC
    146,CCGAACAGTG,GTTTCCGAACAGTGTTATGCATGAACGTAATGCTC,GTTTCCGAACAGTGCGCATGGTGGATTCACAATC
    
    /* Or, save these query results to a file */
    
    sqlite> .mode csv
    sqlite> .output my_first_output_file.csv
    sqlite> SELECT id, tag, left_sequence, right_sequence FROM primers WHERE
       ...> pair_hairpin_either = 0 ORDER BY RANDOM() LIMIT 5;
    sqlite> .quit
