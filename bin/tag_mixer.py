#!/usr/bin/env python
# encoding: utf-8
"""
File: compute_lazy_diversity.py
Author: Brant Faircloth

Created by Brant Faircloth on 11 July 2012 22:07 PDT (-0700)
Copyright (c) 2012 Brant C. Faircloth. All rights reserved.

Description:

"""


import sys
import random
import argparse
import ConfigParser
from collections import OrderedDict

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
    parser.add_argument(
            "output",
            type=argparse.FileType('w')
        )
    parser.add_argument(
        "--batches",
            type=int,
            default=12,
            help="The number of batches of each tag"
        )
    parser.add_argument(
        "--batch-size",
            type=int,
            default=12,
            help="The number tags per batch"
        )
    return parser.parse_args()


class Counts:
    def __init__(self):
        self.reset_tally()
        self.reset_good()
        self.reset_drop()

    def reset_tally(self):
        self.tally = {
                0:{'A':0,'C':0,'G':0,'T':0},
                1:{'A':0,'C':0,'G':0,'T':0},
                2:{'A':0,'C':0,'G':0,'T':0},
                3:{'A':0,'C':0,'G':0,'T':0},
                4:{'A':0,'C':0,'G':0,'T':0},
                5:{'A':0,'C':0,'G':0,'T':0},
                6:{'A':0,'C':0,'G':0,'T':0},
                7:{'A':0,'C':0,'G':0,'T':0}
            }

    def reset_good(self):
        self.good = []

    def reset_drop(self):
        self.drop = []

    def reset(self):
        self.reset_tally()
        self.reset_good()
        self.reset_drop()


def shuffle_tags(tags, tpg, grps, outf):
    """
    tpg = tags per group
    """
    if tpg == 8:
        max_bases = 3
    if tpg == 12:
        max_bases = 6
    counts = Counts()
    current_sets = 0
    while tags:
        for name, tag in tags.iteritems():
            okay = False
            for position, base in enumerate(tag):
                if counts.tally[position][base] < max_bases:
                    okay = True
                else:
                    okay = False
                    break
            if okay:
                for position, base in enumerate(tag):
                    counts.tally[position][base] += 1
                #print name, tag
                counts.good.append([name, tag])
                counts.drop.append(name)
            if len(counts.good) == tpg:
                #pdb.set_trace()
                break
        outf.write("[Group {0} of {1} tags]\n".format(current_sets, tpg))
        for tag in counts.good:
            outf.write("{0}:{1}\n".format(tag[0], tag[1]))
        outf.write("\n")
        for tag in counts.drop:
            try:
                del tags[tag]
            except IndexError:
                pass
        current_sets += 1
        if current_sets < grps:
            counts.reset()
        else:
            break
    return tags


def check_tags_are_unique(output):
    conf2 = ConfigParser.ConfigParser()
    conf2.read(output)
    all_tags = []
    for sec in conf2.sections():
        names = [item[0] for item in list(conf2.items(sec))]
        all_tags.extend(names)
    assert len(set(all_tags)) == len(all_tags), "There are duplicate tags in the output"


def main():
    args = get_args()
    conf = ConfigParser.ConfigParser()
    conf.read(args.conf)
    temp = list(conf.items(args.section))
    random.shuffle(temp)
    tags = OrderedDict(temp)
    #tags_left = shuffle_tags(tags, 8, args.batches, args.output)
    shuffle_tags(tags, args.batch_size, args.batches, args.output)
    args.output.close()
    check_tags_are_unique(args.output.name)

if __name__ == '__main__':
    main()
