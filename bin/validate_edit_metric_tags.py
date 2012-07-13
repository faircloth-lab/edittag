#!/usr/bin/env python
# encoding: utf-8

"""
check_levenshtein_distance.py

Created by Brant Faircloth on 16 January 2011 11:53 PDT (-0700).
Copyright (c) 2011 Brant C. Faircloth. All rights reserved.

PURPOSE:  Determines the edit distances between various groups of linkers in the 
input file passed via CLI. Can also compute Hamming distance in place of
Levenshtein.

USAGE:  validate_edit_metric_tags.py --input=tmp/tags.txt --section='6nt ed3' --verbose

INPUT: my_edit_metric_tags.txt looks something like any of the following three:

#name:sequence#edit_distance
[4nt ed3]
Tag0:GTCA#3
Tag1:AACC#3
Tag2:ACAG#3
Tag3:AGGA#3
Tag4:CCTA#3
Tag5:CGAT#3
Tag6:TGTG#3

#name:sequence
[4nt ed3]
Tag0:GTCA
Tag1:AACC
Tag2:ACAG
Tag3:AGGA
Tag4:CCTA
Tag5:CGAT
Tag6:TGTG

#name = sequence
[4nt ed3]
Tag0 = GTCA
Tag1 = AACC
Tag2 = ACAG
Tag3 = AGGA
Tag4 = CCTA
Tag5 = CGAT
Tag6 = TGTG

"""

import pdb

import os
import sys
import numpy
import optparse
import ConfigParser

from edittag.helpers import get_tag_array, get_name_array
try:
    from Levenshtein import distance
    from Levenshtein import hamming
except:
    from edittag.levenshtein import distance
    from edittag.levenshtein import hamming


def interface():
    """Command-line interface"""
    usage = "usage: %prog [options]"

    p = optparse.OptionParser(usage)

    p.add_option('--input', dest='input', action='store', \
        type='string', default=None, \
        help='The path to the configuration file.', \
        metavar='FILE')
    p.add_option('--section', dest='section', action='store',\
        type='string', default=None, \
        help='[Optional] The section of the config file to evaluate')
    p.add_option('--minimums', dest='minimums', action='store_true', default=True,
        help='[Default] Compute and return only the minimum edit distances in the set of tags')
    p.add_option('--all-distances', dest='distances', action='store_true', default=False,
        help='[Optional] Compute and return all pairwise distances between the membrs in a set of tags')
    p.add_option('--verbose', dest='verbose', action='store_true', default=False,
        help='[Optional] Print pairs of tags with either the minimum edit distance or all'
        + ' combinations of pairwise distances')
    p.add_option('--hamming', dest='hamming', action='store_true',
        default=False, help='[Optional] Use Hamming distance in place of Levenshtein distance.')
    (options, arg) = p.parse_args()
    if options.distances:
        options.minimums = False
    if not options.input or not os.path.isfile(os.path.expanduser(options.input)):
        print "You must provide a valid path to the configuration file."
        p.print_help()
        sys.exit(2)
    return options, arg


def levenshtein(a, b):
    """return the levenshtein/edit distance between a and b"""
    return distance(a, b)


def hammng(a, b):
    """return the hamming distance between a and b"""
    return hamming(a, b)


def get_minimum_tags(bad, section, tags, vector_distance, verbose=False):
    """return the minimum edit distance in the pairwise comparison of all
    sequence tags. if verbose, return all tags compared that are at the
    minimum edit distance"""
    bad[section]['minimum'] = 10000
    bad[section]['tags'] = []
    for key, tag in enumerate(tags):
        if key + 1 < len(tags):
            distances = vector_distance(tags[key + 1:], tag)
            if min(distances) < bad[section]['minimum']:
                bad[section]['minimum'] = min(distances)
                # reset the bad tags
                bad[section]['tags'] = []
            # get any tags < minimum edit distance
            below = numpy.where(distances == bad[section]['minimum'])[0] + (key + 1)
            if below.any() and verbose:
                bad[section]['tags'].append((key, below))
    return bad


def get_all_distances(bad, section, tags, vector_distance, verbose=False):
    """compute and return the levenshtein distances between all pairwise
    combinations of tags"""
    bad[section]['tags'] = []
    for key, tag in enumerate(tags):
        if key + 1 < len(tags):
            distances = vector_distance(tags[key + 1:], tag)
            if not verbose:
                bad[section]['tags'].extend(distances)
            else:
                # generate tag index list
                idx = range(key + 1, len(tags))
                distance_dict = dict(zip(idx, distances))
                bad[section]['tags'].append((key, distance_dict))
    return bad


def get_section_results(options, bad, tags, section, vector_distance):
    """helper function that runs comparisons on a per section basis"""
    bad[section] = {'minimum': None}
    if options.minimums:
        bad = get_minimum_tags(bad, section, tags, vector_distance, options.verbose)
    elif options.distances:
        bad = get_all_distances(bad, section, tags, vector_distance, options.verbose)
    return bad


def print_minimums(conf, names, tags, bad, verbose=True):
    """pretty print results from our bad tag dictionary"""
    sections = bad.keys()
    sections.sort()
    if verbose:
        for sec in sections:
            print "[{0}]\n\tMinimum edit distance of set = {1}".format(sec, bad[sec]['minimum'])
            print "\tTag pairs at the minimum distance:"
            for base, compare in bad[sec]['tags']:
                for idx in compare:
                    print "\t\t{0},{1} :: {2},{3} - Edit Distance = {4}".format(
                            names[base],
                            tags[base],
                            names[idx],
                            tags[idx],
                            bad[sec]['minimum']
                        )
    else:
        for sec in sections:
            print "[{0}]\n\tminimum edit distance = {1}".format(sec, bad[sec]['minimum'])


def print_distances(conf, options, names, tags, bad, verbose=True):
    """pretty print results from our bad tag dictionary"""
    sections = bad.keys()
    sections.sort()
    for sec in sections:
        if options.verbose:
            comparisons = bad[sec]['tags']
            distances = []
            for c in comparisons:
                distances.extend(c[1].values())
            distances = numpy.array(distances)
        else:
            distances = numpy.array(bad[sec]['tags'])
        summary = numpy.bincount(distances)
        mode = [i for i in numpy.where(summary == max(summary))[0]]
        print "[{0}]\n\tMinimum edit distance:\t\t{1}".format(sec, min(distances))
        print "\tModal edit distance:\t\t{0}".format(mode)
        print "\tMax edit distance:\t\t{0}".format(max(distances))
        print "\n\tDistribution of edit distance comparisons:\n"
        print "\t\t  Edit Distance  Count "
        print "\t\t|--------------|------|"
        for k, v in enumerate(summary):
            fh = ' ' * (14 - len(str(k)))
            bh = ' ' * (6 - len(str(v)))
            print "\t\t|{0}{1}|{2}{3}|".format(fh, k, bh, v)
        print "\t\t-----------------------\n\n"
    if options.verbose:
        for sec in sections:
            print "[{0}]".format(sec)
            print "\tTag comparisons:"
            for base, compare in bad[sec]['tags']:
                for idx, distance in compare.iteritems():
                    print "\t\t{0},{1} :: {2},{3} - Edit Distance = {4}".format(
                            names[base],
                            tags[base],
                            names[idx],
                            tags[idx],
                            distance
                        )


def main():
    """main loop"""
    options, arg = interface()
    conf = ConfigParser.ConfigParser()
    conf.read(options.input)
    if options.hamming:
        vector_distance = numpy.vectorize(hammng)
    else:
        vector_distance = numpy.vectorize(levenshtein)
    bad = {}
    if not options.section:
        for section in conf.sections():
            tags = get_tag_array(conf.items(section))
            names = get_name_array(conf.items(section))
            bad = get_section_results(options, bad, tags, section, vector_distance)
    elif options.section:
        tags = get_tag_array(conf.items(options.section))
        names = get_name_array(conf.items(options.section))
        bad = get_section_results(options, bad, tags, options.section, vector_distance)
    if options.minimums:
        print_minimums(conf, names, tags, bad, options.verbose)
    elif options.distances:
        print_distances(conf, options, names, tags, bad, options.verbose)


if __name__ == '__main__':
    main()
