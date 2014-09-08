#!/usr/bin/env python
# encoding: utf-8
"""
File: get_unused_tags.py
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
            "conf1",
            help="""Used tags"""
        )
    parser.add_argument(
            "conf2",
            help="""All tags"""
        )
    parser.add_argument(
            "output",
            help="""Output file for unused tags"""
        )
    return parser.parse_args()


def main():
    args = get_args()
    conf1 = ConfigParser.ConfigParser()
    conf2 = ConfigParser.ConfigParser()
    conf1.read(args.conf1)
    used_tags = []
    for sec in conf1.sections():
        #pdb.set_trace()
        tags = list(conf1.items(sec))
        names = [t[0] for t in tags]
        used_tags.extend(names)
    conf2.read(args.conf2)
    tags = dict(list(conf2.items('compatible with both i7 and i5')))
    outf = open(args.output, 'w')
    outf.write("[Batch 2: compatible with both i7 and i5]\n")
    sorted_tags = sorted(tags.keys())
    for name in sorted_tags:
        if not name in used_tags:
            outf.write("{0}:{1}\n".format(name, tags[name]))
    outf.close()



if __name__ == '__main__':
    main()
