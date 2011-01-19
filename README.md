# edittag

Copyright (c) 2009-2011 Brant C. Faircloth.
All rights reserved.

See `LICENSE.md` for standard, 2-clause BSD license.

## Description

edittag is a software collection for designing sets of edit metric sequence tags, checking sequence tags for conformation to the edit metric, and integrating sequence tags to platform-specific sequencing adapters and PCR primers.  edittag differs from other approaches:

 * edittag generates arbitrary lengths of edit-metric sequence tags in reasonable time frames using multiprocessing
 * edittag produces edit metric sequence tag sets conform to the edit distance selected
 * edittag used primer3 to integrate sequence tags to PCR primers

## Citation

Cite.

## Dependencies

 * Python 2.7.x (should work on 2.6.x)
 * numpy (tested with 1.5.1)
 * py-levenshtein [optional but strongly recommended]
 * primer3-mod [optional]

## Availability

 * tar.gz
 * repository
 * Amazon Machine Instance #

## Installation

### tar.gz

 1. `tar -xzf package.tar.gz`
 1. `python setup.py install`

### repository

 1. git clone git://github.com/baddna/edittag.git edittag
 1. chmod 0755 edittag/*.py
 1. ensure edittag is in your path

The steps below are only necessary if you want to use primer3 to integrate sequence tags to PCR primers:

 1. cd git/edittag/edittag/lib/primer3
 1. git submodule init && git submodule update
 1. cd ../../../../
 1. git clone git://github.com/baddna/mod-primer3.git
 1. cd mod-primer3/src
 1. make
 1. make install
 
Ensure both `edittag` and `mod-primer3` are in your path.  Alternatively, move the binaries from mod-primer3 to a location in your path (move at least `primer3-long` and `primer3_config` into the same directory in your path).  You can then run

### Amazon Machine Instance

 1. Create an account on Amazon EC2.  
 1. Run our instance with
 