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

#import pdb

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
    i5tags = dict(conf.items('i5'))
    i7tags = dict(conf.items('i7'))
    i7names = sorted(i7tags.keys())
    for k in i7names:
        if k in i5tags.keys():
            print "{0}:{1}".format(k, i7tags[k])

if __name__ == '__main__':
    main()
