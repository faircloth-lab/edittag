#!/usr/bin/env python
# encoding: utf-8
"""
File: compute_lazy_diversity.py
Author: Brant Faircloth

Created by Brant Faircloth on 11 July 2012 22:07 PDT (-0700)
Copyright (c) 2012 Brant C. Faircloth. All rights reserved.

Description: 

"""


import argparse
import ConfigParser
from seqtools.sequence import transform

import pdb

def get_args():
    """Get arguments from CLI"""
    parser = argparse.ArgumentParser(
            description="""Program description""")
    parser.add_argument(
            "conf",
            help="""Help text"""
        )
    return parser.parse_args()


def main():
    args = get_args()
    conf = ConfigParser.ConfigParser()
    conf.read(args.conf)
    print "bases in adapter,index name, bases for entry on sample sheet"
    for sec in conf.sections():
        print sec
        #pdb.set_trace()
        tags = list(conf.items(sec))
        for tag in tags:
            if "8 tags" in sec:
                print "{0},{1},{2}".format(tag[1], tag[0], tag[1])
            elif "12 tags" in sec:
                print "{0},{1},{2}".format(tag[1], tag[0], transform.DNA_reverse_complement(tag[1]))
if __name__ == '__main__':
    main()
