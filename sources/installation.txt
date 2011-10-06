.. _installation:

*************
Installation
*************

easy_install
============

This is one of the easiest options to get up and running quickly::

    easy_install edittag


tar.gz format
=============

You can install edittag from tar.gz archive::

    tar -xzf edittag-0.5.tar.gz
    cd edittag-0.5/
    python setup.py build
    python setup.py test
    python setup.py install

zip format
==========

Similar to tar.gz::

    unzip edittag-0.5.zip
    cd edittag-0.5/
    python setup.py build
    python setup.py test
    python setup.py install

Amazon Machine Instance (AMI)
=============================

To provide a static environment for testing and running *edittag* and to enable users to easily run *edittag* on a multicore machine, we provide an Amazon Machine Instance (AMI) with all dependencies installed that is particularly useful when generating large (≥ 8 base pair) edit metric tag sets.  We maintain this AMI, to which we have installed several other packages that may be useful (more info)::

    # code here



