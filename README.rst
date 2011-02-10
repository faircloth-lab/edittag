edittag
=======

Copyright (c) 2009–2011 Brant C. Faircloth. All rights reserved.

-  See ``LICENSE.md`` for standard, 2-clause BSD license covering
   computer code.
-  Sequence tags available from
   `https://github.com/BadDNA/edittag/downloads`_ are licensed under
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

-  text_ - this file is in an appropriate format for
   ``check_levenshtien_distance.py``
-  csv_
-  `sqlite database`_

Citation
--------

::

    Faircloth BC, Glenn TC.  Large sets of edit-metric sequence identification 
    tags to facilitate large-scale multiplexing of reads from massively 
    parallel sequencing.  doi_

Dependencies
------------

-  `Python 2.7.x`_ (should work on 2.6.x)
-  `numpy`_ (tested with 1.5.1)
-  `py-levenshtein`_ [optional but strongly recommended]
-  `mod-primer3`_ [optional]
-  `nose >= 1.0.0`_ [optional - for unittests]

Availability
------------

-  tar.gz
-  repository
-  Amazon Machine Instance # (coming soon)

Installation
------------

easy_install
~~~~~~~~~~~~

.. code-block:: bash

    easy_install edittag

tar.gz
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    wget package.tar.gz
    tar -xzf package.tar.gz
    python setup.py install

repository
~~~~~~~~~~

.. code-block:: bash

    git clone git://github.com/baddna/edittag.git edittag


optional package (py-levenshtein)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    wget http://pylevenshtein.googlecode.com/files/python-Levenshtein-0.10.1.tar.bz2
    tar -xzvf python-Levenshtein-0.10.1.tar.bz2
    python setup.py install


optional package (primer3)
~~~~~~~~~~~~~~~~~~~~~~~~~~

If you wish to design primers incorporating edit metric sequence tags, you 
need to first install a modified version of primer3:

.. code-block:: bash

    git clone git://github.com/baddna/mod-primer3.git
    cd mod-primer3/src
    make
    make install

Ensure that you move the binaries from mod-primer3 to a location in your
path (move at least ``primer3-long`` and ``primer3_config`` into the
same directory in your path). You can then run

Testing
-------

.. code-block:: python

    # Testing requires numpy and nose
    import edittag
    edittag.test()


Alternatives sources
--------------------

Amazon Machine Instance (not yet implemented)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Create an account on Amazon EC2.
2. Start AMI # xxxxx

.. _`https://github.com/BadDNA/edittag/downloads`: https://github.com/BadDNA/edittag/downloads
.. _Creative Commons Attribution 3.0 United States License: http://creativecommons.org/licenses/by/3.0/us/
.. _text: https://github.com/downloads/BadDNA/edittag/edit_metric_tags.txt
.. _csv: https://github.com/downloads/BadDNA/edittag/edit_metric_tags.csv
.. _sqlite database: https://github.com/downloads/BadDNA/edittag/edit_metric_tags.sqlite.zip
.. _doi:  http://dx.doi.org/
.. _Python 2.7.x: http://www.python.org/
.. _numpy: http://numpy.scipy.org
.. _py-levenshtein: http://pylevenshtein.googlecode.com
.. _mod-primer3: https://github.com/BadDNA/mod-primer3