#!/usr/bin/env python
# encoding: utf-8

"""
add_tags_to_adapters.py

Created by Brant Faircloth on 09 November 2010 10:16 PST (-0800).
Copyright (c) 2010 Brant C. Faircloth. All rights reserved.

USAGE:  add_tags_to_adapters.py \
            --5-prime CAAGCAGAAGACGGCATACGAGA --3-prime TGACTGGAGTTC \
            --input tags.conf

"""

#import pdb
import os
import sys
import optparse
import string
import ConfigParser
from edittag.helpers import get_tag_array
from edittag.helpers import get_rev_comp


def interface():
    '''Command-line interface'''
    usage = "usage: %prog [options]"

    p = optparse.OptionParser(usage)

    p.add_option('--input', dest = 'input', action='store', 
type='string', default = None, help='The path to the sequence tag file.', 
metavar='FILE')
    p.add_option('--5-prime', dest = 'fprime', action='store', 
type='string', default = None, help='The sequence 5-prime of the barcode.', 
metavar='FILE')
    p.add_option('--3-prime', dest = 'tprime', action='store', 
type='string', default = None, help='The sequence 3-prime of the barcode.', 
metavar='FILE')
    p.add_option('--section', dest = 'section', action = 'store',\
type='string', default = None, help='[Optional] The section of'
+' the config file to evaluate')
    p.add_option('--revcomp', dest = 'revcomp', action='store_true', 
default=False, help='[Optional] Add reverse complement of tag instead'
+' of sequence.')
    p.add_option('--suppress-orientation', dest = 'suppress', action='store_true', 
default=False, help='[Optional] Just print adapter sequences')

    (options,arg) = p.parse_args()
    if not options.input:
        p.print_help()
        sys.exit(2)
    if not os.path.isfile(options.input):
        print "You must provide a valid path to the configuration file."
        p.print_help()
        sys.exit(2)
    return options, arg 

def add_tags_to_adapters(adapters, section, fprime, tprime, tags, revcomp=False):
    """insert the sequence tags between the fprime and tprime adapter sequences
    and return a dictionary indexed by seq"""
    for tag in tags:
        if not revcomp:
            adapter = fprime + tag.lower() + tprime
        else:
            adapter = fprime + get_rev_comp(tag).lower() + tprime
        adapters.setdefault(section, []).append(adapter)
    return adapters

def show_results(adapters, suppress):
    """pretty print the adapter + index sequences"""
    for sec in adapters:
        print "[{0}]".format(sec)
        for adap in adapters[sec]:
            if not suppress:
                print "\t5' - {0} - 3'".format(adap)
            else:
                print "\t{0}".format(adap)

def main():
    options, args = interface()
    conf = ConfigParser.ConfigParser()
    conf.read(options.input)
    adapters = {}
    if not options.section:
        for section in conf.sections():
            tags = get_tag_array(conf.items(section))
            adapters = add_tags_to_adapters(adapters, section, options.fprime, options.tprime, tags, options.revcomp)
    elif options.section:
        tags = get_tag_array(conf.items(options.section))
        adapters = add_tags_to_adapters(adapters, options.section, options.fprime, options.tprime, tags, options.revcomp)
    show_results(adapters, options.suppress)


if __name__ == '__main__':
    main()