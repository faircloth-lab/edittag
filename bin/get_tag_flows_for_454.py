#!/usr/bin/env python
# encoding: utf-8

"""
get_tag_flows_for_454.py

Created by Brant Faircloth on 04 October 2010 11:02 PDT (-0700).
Copyright (c) 2010 Brant C. Faircloth. All rights reserved.

USAGE:  get_tag_flows_for_454.py --input='tags.txt' --section='6nt ed3'

"""
#import pdb
import os
import sys
import optparse
import ConfigParser
from operator import itemgetter
from edittag.helpers import get_tag_flows
from edittag.helpers import get_tag_dict

def interface():
    '''Command-line interface'''
    usage = "usage: %prog [options]"

    p = optparse.OptionParser(usage)

    p.add_option('--input', dest = 'input', action='store', 
        type='string', default = None, help='The path to the input file.', 
        metavar='FILE')

    p.add_option('--section', dest = 'section', action = 'store',\
        type='string', default = None, help='[Optional] The section of'
        +' the config file to evaluate')

    (options,arg) = p.parse_args()
    options.input = os.path.abspath(os.path.expanduser(options.input))
    #if options.output:
    #    options.output = os.path.abspath(os.path.expanduser(options.output))
    if not options.input:
        p.print_help()
        sys.exit(2)
    if not os.path.isfile(options.input):
        print "You must provide a valid path to the configuration file."
        p.print_help()
        sys.exit(2)
    return options, arg

def get_section_flows(section, flows, tags):
    """determine the number of flows per tag in a given section of the input file"""
    for name in tags:
        flows.setdefault(section, []).append([name, tags[name], get_tag_flows(tags[name])])
    return flows

def show_results(flows):
    """pretty print the flow result to stdout"""
    for sec in flows:
        print "{0}".format(sec)
        for item in sorted(flows[sec], key=itemgetter(2)):
            print "\t{0}\t{1}\t{2}".format(item[0], item[1], item[2])

def main():
    options, args = interface()
    conf = ConfigParser.ConfigParser()
    conf.read(options.input)
    flows = {}
    if not options.section:
        for section in conf.sections():
            tags = get_tag_dict(conf.items(section))
            flows = get_section_flows(section, flows, tags)
    elif options.section:
        tags = get_tag_dict(conf.items(options.section))
        flows = get_section_flows(options.section, flows, tags)
    show_results(flows)
    
if __name__ == '__main__':
    main()