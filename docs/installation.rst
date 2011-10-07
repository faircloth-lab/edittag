.. _installation:

*************
Installation
*************

edittag_ has several dependencies.  At a minimum, you must install
numpy_.  Optional installs include:

- python-levenshtein_
- mod-primer3_
- nose_

Installing numpy
================

You first need to install numpy_.  Barring platform-specific options, you can 
accomplish this by running::

    easy_install numpy

Sometimes on OSX, this is problematic.  There is a `binary installer
<http://sourceforge.net/projects/numpy/files/NumPy/1.6.1/numpy-1.6.1-py2.6-python.org-macosx10.3.dmg/download>`_
that you can use in this case.

Installing python-levenshtein and edittag
=========================================

The easiest option to get up and running quickly is to use easy_install:

.. code-block:: bash

    easy_install python-Levenshtein
    easy_install edittag

You can also install both by download the tarballs (edittag_ and
python-levenshtein_) and running:

.. code-block:: bash

    python setup.py install

In the unzipped directory of each package.

.. _mod-primer_installation:

Installing mod-primer3
======================

If you would like to design primers with integrated tags, you need to
build and install a modified version of the primer3 source code.  To do
that, download the source_, build it, and place both primer3_long and
primer3_config somewhere, in the same directory, within your path (here,
I use /usr/local/bin, because it is usually already in your $PATH:

.. code-block:: bash

    wget https://github.com/faircloth-lab/mod-primer3/zipball/v2.2.3
    unzip v2.2.3
    rm v2.2.3
    cd faircloth-lab-mod-primer3-*/src && make
    cp primer3_{config,bin} /usr/local/bin/


.. _edittag: https://github.com/faircloth-lab/edittag/zipball/v1.0rc1
.. _python-levenshtein: https://github.com/faircloth-lab/python-levenshtein/zipball/v0.10.2
.. _numpy: http://www.scipy.org/Download
.. _mod-primer3: https://github.com/faircloth-lab/mod-primer3
.. _source: https://github.com/faircloth-lab/mod-primer3
.. _nose: http://code.google.com/p/python-nose/
