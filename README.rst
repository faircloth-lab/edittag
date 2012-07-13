Copyright (c) 2009-2012 Brant C. Faircloth. All rights reserved.

-  See **LICENSE.md** for standard computer code.

- Sequence tags available from
  https://github.com/faircloth-lab/edittag/downloads are licensed under
  `Creative Commons Attribution 3.0 United States License`_.

Description
-----------

edittag is a software collection for designing sets of edit metric
sequence tags, checking sequence tags for conformation to the edit
metric, and integrating sequence tags to platform-specific sequencing
adapters and PCR primers. edittag differs from other approaches:

-  edittag generates arbitrary lengths of edit-metric sequence tags in
   reasonable time frames using multiprocessing
-  edittag produces edit metric sequence tag sets conform to the edit
   distance selected
-  edittag used primer3 to integrate sequence tags to PCR primers

We provide several large sets of edit metric sequence tags designed
using edittag in the following formats:

-  text_ - this file is in an appropriate format for `check_levenshtien_distance.py`
-  csv_
-  `sqlite database`_

Documentation
-------------
You can find documentation here:

http://faircloth-lab.github.com/edittag/

Citation
--------

Faircloth BC, Glenn TC.  Large sets of edit-metric sequence identification 
tags to facilitate large-scale multiplexing of reads from massively 
parallel sequencing.  `http://precedings.nature.com/documents/5672/version/1`_

Dependencies
------------

-  `Python 2.7.x`_      (should work on 2.6.x)
-  `numpy`_             (tested with 1.5.1)
-  `py-levenshtein`_    [optional - strongly recommended]
-  `mod-primer3`_       [optional - needed for amplicon tagging]
-  `nose`_              [optional - for unittests]

Availability
------------

-  tar.gz
-  repository

Installation
------------

easy_install
~~~~~~~~~~~~
::

    easy_install edittag


tar.gz
~~~~~~~
::

    wget package.tar.gz
    tar -xzf package.tar.gz
    python setup.py install


repository
~~~~~~~~~~~~
::

    git clone git://github.com/faircloth-lab/edittag.git edittag


optional package (py-levenshtein)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
::

    wget http://pylevenshtein.googlecode.com/files/python-Levenshtein-0.10.1.tar.bz2
    tar -xzvf python-Levenshtein-0.10.1.tar.bz2
    python setup.py install


optional package (primer3)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you wish to design primers incorporating edit metric sequence tags, you 
need to first install a modified version of primer3:::

    git clone git://github.com/baddna/mod-primer3.git
    cd mod-primer3/src
    make

Ensure that you move the binaries from mod-primer3 to a location in your
path (move at least ``primer3-long`` and ``primer3_config`` into identical 
directories in your path).

Testing
--------

::

    # Testing requires numpy and nose
    import edittag
    edittag.test()


Using edittag
---------------

::

    # generate some tags
    % design_edit_metric_tags.py --tag-length=6 --edit-distance=3 \
        --no-polybase --gc --comp --min-and-greater --output tmp/tags.txt

    # validate the 6 nucleotide, edit distance 3 tag set
    % validate_edit_metric_tags.py 
        --input=tmp/tags.txt
        --section='6nt ed3'
        --verbose

    # add those tags to a primer set
    % add_tags_to_primers.py --left-primer=GTTATGCATGAACGTAATGCTC 
        --right-primer=CGCGCATGGTGGATTCACAATCC \
        --input tmp/tags.txt --section='6nt ed3'
        --sort=pair_hairpin_either,pair_penalty,cycles \
        --remove-common --keep-database \
        --output tmp/trnH_tagged_with_10_nt_ed_5_tags.csv



.. _`https://github.com/BadDNA/edittag/downloads`: https://github.com/BadDNA/edittag/downloads
.. _`http://precedings.nature.com/documents/5672/version/1`: http://precedings.nature.com/documents/5672/version/1
.. _Creative Commons Attribution 3.0 United States License: http://creativecommons.org/licenses/by/3.0/us/
.. _text: https://github.com/downloads/faircloth-lab/edittag/edit_metric_tags.txt
.. _csv: https://github.com/downloads/faircloth-lab/edittag/edit_metric_tags.csv
.. _sqlite database: https://github.com/downloads/faircloth-lab/edittag/edit_metric_tags.sqlite.zip
.. _Python 2.7.x: http://www.python.org/
.. _numpy: http://numpy.scipy.org
.. _py-levenshtein: http://pylevenshtein.googlecode.com
.. _mod-primer3: https://github.com/BadDNA/mod-primer3
.. _nose: http://somethingaboutorange.com/mrl/projects/nose/1.0.0/
