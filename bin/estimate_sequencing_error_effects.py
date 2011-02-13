#!/usr/bin/env python
# encoding: utf-8

"""
estimate_sequencing_error_effects.py

Created by Brant Faircloth on 20 November 2010 15:27 PST (-0800).
Copyright (c) 2010 Brant C. Faircloth. All rights reserved.

USAGE:  estimate_sequencing_error_effects.py \
            --read-count=1000000 --output=test.out \
            --barcode-length=8 --iterations=1000
"""

#import pdb
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

    p.add_option('--output', dest = 'output', action='store', 
type='string', default = None, help='The path to the output file.', 
metavar='FILE')

    p.add_option('--read-count', dest = 'count', action='store', 
type='int', default = 500000, help='The read count')

    p.add_option('--barcode-length', dest = 'barcode', action='store', 
type='int', default = 10, help='The read count')

    p.add_option('--iterations', dest = 'iterations', action='store', 
type='int', default = 100, help='The read count')

    (options,arg) = p.parse_args()
    
    if not options.output:
        sys.exit(2)
    
    return options, arg
    
def runner(_):
    counts = numpy.histogram(numpy.random.binomial(options.barcode, options.error, options.count), bins = [0,1,2,3,4,5,6,7,8,9,10])[0]
    sys.stdout.write(".")
    sys.stdout.flush()
    return counts

options, args = interface()
pool = multiprocessing.Pool(7)
outf = open(options.output, 'w')
sys.stdout.write("Processing")
sys.stdout.flush()
result = pool.map(runner, range(options.iterations))
#pdb.set_trace()
pool.close()
pool.join()
for r in result:
    outf.write("{0}\n".format(','.join(r.astype('|S20'))))
print "\n"
outf.close()
