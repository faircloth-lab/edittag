#!/usr/bin/env python
# encoding: utf-8

"""
estimate_sequencing_error_effects.py

Created by Brant Faircloth on 20 November 2010 15:27 PST (-0800).
Copyright (c) 2010 Brant C. Faircloth. All rights reserved.
"""

import pdb
import os
import sys
import optparse
import numpy
import multiprocessing
from collections import defaultdict


def interface():
    '''Command-line interface'''
    usage = "usage: %prog [options]"

    p = optparse.OptionParser(usage)

    p.add_option('--error-rate', dest = 'error', action='store', 
type='float', default = 0.01, help='The error rate')

    p.add_option('--read-length', dest = 'read', action='store', 
type='int', default = 250, help='The read length')

    p.add_option('--read-count', dest = 'count', action='store', 
type='int', default = 500000, help='The read count')

    p.add_option('--barcode-length', dest = 'barcode', action='store', 
type='int', default = 10, help='The read count')

    p.add_option('--verbose', dest = 'verbose', action='store_true', default=False, 
help='Print iteration')

    (options,arg) = p.parse_args()
    return options, arg 

def sequence_generator(i, count, read, barcode, error_rate):
    error_dict = defaultdict(int)
    for i in xrange(count):
        #pdb.set_trace()
        read = numpy.random.binomial(1, error_rate, read)
        errors = sum(read[10:10 + barcode])
        error_dict[errors] += 1
    print error_dict

def main():
    options, args = interface()
    pool = multiprocessing.Pool(7)
    pool.map(sequence_generator, range(10), options.count, options.read, options.barcode, options.error) 

if __name__ == '__main__':
    main()