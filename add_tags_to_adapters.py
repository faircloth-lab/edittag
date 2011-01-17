#!/usr/bin/env python
# encoding: utf-8

"""
barcode_inserter.py

Created by Brant Faircloth on 09 November 2010 10:16 PST (-0800).
Copyright (c) 2010 Brant C. Faircloth. All rights reserved.
"""

import pdb
import os
import sys
import optparse
import string


def interface():
    '''Command-line interface'''
    usage = "usage: %prog [options]"

    p = optparse.OptionParser(usage)

    p.add_option('--input', dest = 'input', action='store', 
type='string', default = None, help='The path to the input barcodes file.', 
metavar='FILE')
    p.add_option('--5-prime', dest = 'head', action='store', 
type='string', default = None, help='The sequence 5-prime of the barcode.', 
metavar='FILE')
    p.add_option('--3-prime', dest = 'tail', action='store', 
type='string', default = None, help='The sequence 3-prime of the barcode.', 
metavar='FILE')


    (options,arg) = p.parse_args()
    if not options.input:
        p.print_help()
        sys.exit(2)
    if not os.path.isfile(options.input):
        print "You must provide a valid path to the configuration file."
        p.print_help()
        sys.exit(2)
    return options, arg 

def rev_comp(seq):
   '''Return reverse complement of seq'''
   bases = string.maketrans('AGCTagct','TCGAtcga')
   # translate it, reverse, return
   return seq.translate(bases)[::-1]

def main():
    options, args = interface()
    for line in open(options.input, 'rU'):
        if not line.startswith('#'):
            if '\t' in line:
                barcode, name = line.strip('\n').split('\t')
            elif '=' in line:
                pieces = line.strip().split('=')
                pieces = [i.strip(' ') for i in pieces]
                name, barcode = pieces
            else:
                name, barcode = line.strip('\n').split(' ')
            primer = options.head + rev_comp(barcode).lower() + options.tail
            print 'Index Primer {0}: 5\' - {1} ===>'.format(name, primer)


if __name__ == '__main__':
    main()