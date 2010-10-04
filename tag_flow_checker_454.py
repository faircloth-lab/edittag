#!/usr/bin/env python
# encoding: utf-8

"""


Created by Brant Faircloth on 04 October 2010 11:02 PDT (-0700).
Copyright (c) 2010 Brant C. Faircloth. All rights reserved.
"""

import os
import sys
import pdb
import optparse
from operator import itemgetter

def interface():
    '''Command-line interface'''
    usage = "usage: %prog [options]"

    p = optparse.OptionParser(usage)

    p.add_option('--input', dest = 'input', action='store', 
type='string', default = None, help='The path to the input file.', 
metavar='FILE')
    p.add_option('--output', dest = 'output', action='store', 
type='string', default = None, help='The path to the output file.', 
metavar='FILE')

    (options,arg) = p.parse_args()
    options.input = os.path.abspath(os.path.expanduser(options.input))
    if options.output:
        options.output = os.path.abspath(os.path.expanduser(options.output))
    if not options.input:
        p.print_help()
        sys.exit(2)
    if not os.path.isfile(options.input):
        print "You must provide a valid path to the configuration file."
        p.print_help()
        sys.exit(2)
    return options, arg 


def main():
    options, args = interface()
    f = open(options.input, 'rU')
    header = f.next()
    data = []
    for line in f:
        name, tag = line.strip().split(',')
        flows = []
        for base in tag:
            for count, flow in enumerate(['T', 'A', 'C', 'G']):
                if base == flow:
                    flows.append(count+1)
                    break
        data.append([name, tag, sum(flows)])
    if options.output:
        o = open(options.output, 'w')
    # sort all the tags by the number of flows required
    for tag in sorted(data, key=itemgetter(2)):
        # there's an integer in the list, so we have to stringify it
        result = ','.join(['{0}'.format(i) for i in tag])
        if not options.output:
            print result
        else:
            o.write('{0}\n'.format(result))
    
if __name__ == '__main__':
    main()