#!/usr/bin/env python
# encoding: utf-8
"""
File: compute_lazy_diversity.py
Author: Brant Faircloth

Created by Brant Faircloth on 11 July 2012 22:07 PDT (-0700)
Copyright (c) 2012 Brant C. Faircloth. All rights reserved.

Description: 

"""



import entropy
import argparse
import ConfigParser

import pdb

def get_args():
    """Get arguments from CLI"""
    parser = argparse.ArgumentParser(
            description="""Program description""")
    parser.add_argument(
            "conf",
            help="""Help text"""
        )
    parser.add_argument(
            "section",
            type=str,
            help="""Help text"""
        )
    return parser.parse_args()

def main():
    args = get_args()
    conf = ConfigParser.ConfigParser()
    conf.read(args.conf)
    #pdb.set_trace()
    tags = conf.items(args.section)
    for row in tags:
        name, tag = row
        ent = entropy.entropy(tag)
        score = 0
        for position, base in enumerate(tag):
            if position == 0:
                score += 1
            else:
                if not base == tag[position - 1]:
                    score += 1
        for rep in ['ACAC', 'GTGT', 'CTCT', 'GCGC']:
            if rep in tag:
                score = 0
        print name, tag, float(score) + ent
        




if __name__ == '__main__':
    main()
