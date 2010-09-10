#!/usr/bin/env python
# encoding: utf-8

"""
levenshtein.py

Created by Brant Faircloth on 10 September 2010 11:53 PDT (-0700).
Copyright (c) 2010 Brant C. Faircloth. All rights reserved.

PURPOSE:  Determines the edit distances between various groups of linkers in the 
configuration file passed on stdin.

USAGE:  python helpers/levenshtein.py --configuration=linker-py.conf \
        --section=MidLinkerGroups --verbose

"""

import pdb
import operator
import optparse
import os
import ConfigParser
import Levenshtein

def interface():
    '''Command-line interface'''
    usage = "usage: %prog [options]"

    p = optparse.OptionParser(usage)

    p.add_option('--configuration', '-c', dest = 'conf', action='store', \
        type='string', default = None, \
        help='The path to the configuration file.', \
        metavar='FILE')
    p.add_option('--section', '-s', dest = 'section', action = 'store',\
        type='string', default = None, \
        help='The section of the config file to evaluate', metavar='FILE')
    p.add_option('--verbose', dest = 'verbose', action='store_true', default=False, 
        help='Print edit distance of all combinations')
    
    (options,arg) = p.parse_args()
    if not options.conf:
        p.print_help()
        sys.exit(2)
    if not os.path.isfile(options.conf):
        print "You must provide a valid path to the configuration file."
        p.print_help()
        sys.exit(2)
    return options, arg

def hamming_distance(s1, s2):
    '''Find the Hamming distance btw. 2 strings.
    
    Substitutions only.
    
    From http://en.wikipedia.org/wiki/Hamming_distance
    
    '''
    assert len(s1) == len(s2)
    return sum([ch1 != ch2 for ch1, ch2 in zip(s1, s2)])

def levenshtein(a,b):
    '''Calculates the levenshtein distance between a and b.
    
    Insertions, deletions, substitutions
    
    From here:  http://hetland.org/coding/python/levenshtein.py
    
    '''
    n, m = len(a), len(b)
    if n > m:
        # Make sure n <= m, to use O(min(n,m)) space
        a,b = b,a
        n,m = m,n
    current = range(n+1)
    for i in range(1,m+1):
        previous, current = current, [i]+[0]*n
        for j in range(1,n+1):
            add, delete = previous[j]+1, current[j-1]+1
            change = previous[j-1]
            if a[j-1] != b[i-1]:
                change = change + 1
            current[j] = min(add, delete, change)
    return current[n]

def getDistanceC(linkers, *args, **kwargs):
    #pdb.set_trace()
    linker_dist = []
    for l1 in xrange(len(linkers)):
        s1 = linkers[l1]
        for s2 in linkers[l1+1:]:
            edit_distance = Levenshtein.distance(s1[1],s2[1])
            linker_dist.append((s1[0], s2[0], edit_distance))
    #pdb.set_trace()
    link_list = [i[0] for i in linkers]
    if len(linker_dist) == 0:
        min_dist = 'NA'
    else:
        min_dist = min([i[2] for i in linker_dist])
    if kwargs and kwargs['distances']:
        linker_sorted = sorted(linker_dist, key=operator.itemgetter(2))
        return linker_sorted
    else:
        return link_list, min_dist

def getDistance(linkers, *args, **kwargs):
    #pdb.set_trace()
    linker_dist = []
    for l1 in xrange(len(linkers)):
        s1 = linkers[l1]
        for s2 in linkers[l1+1:]:
            edit_distance = levenshtein(s1[1],s2[1])
            linker_dist.append((s1[0], s2[0], edit_distance))
    #pdb.set_trace()
    link_list = [i[0] for i in linkers]
    if len(linker_dist) == 0:
        min_dist = 'NA'
    else:
        min_dist = min([i[2] for i in linker_dist])
    if kwargs and kwargs['distances']:
        linker_sorted = sorted(linker_dist, key=operator.itemgetter(2))
        return linker_sorted
    else:
        return link_list, min_dist

def test():
    assert(levenshtein('shit','shat') == 1)
    assert(levenshtein('cool','bowl') == 2)
    assert(levenshtein('kitten','sitting') == 3)
    assert(levenshtein('bonjour','bougeoir') == 4)

def main():
    options, arg = interface()
    conf = ConfigParser.ConfigParser()
    conf.read(options.conf)
    groups = {}
    if options.section == 'MidLinkerGroups':
        clust = conf.items('MidLinkerGroups')
        links = dict(conf.items('Linker'))
        for c in clust:
            group = c[0].split(',')[0]
            linker = c[0].split(',')[1].strip()
            if group in groups.keys():
                groups[group] = groups[group] + ((linker,links[linker]),)
            else:
                groups[group] = ((linker,links[linker]),) 
    elif options.section == 'LinkerGroups':
        #pdb.set_trace()
        clust = conf.items('LinkerGroups')
        links = dict(conf.items('Linker'))
        g = ()
        for c in clust:
            g += ((c[0], links[c[0]]),)
        groups[1] = g
    elif options.section == 'Linker':
        #pdb.set_trace()
        g = conf.items('Linker')
        groups[1] = g
        #pdb.set_trace()
        
    for g in groups:
        #pdb.set_trace()
        ed = getDistance(groups[g], g, distances = True)
        #pdb.set_trace()
        if len(groups[g]) > 1:
            # get minimum distance
            min_dist = ed[0][2]
            print '{0} {1}\n\n\tminimum edit distance = {2}\n\n\tlinkers with minimum edit distance:'.format(options.section, g, min_dist)
            for l_set in ed:
                if l_set[2] == min_dist:
                    print '\t\t{0} <=> {1}'.format(l_set[0], l_set[1])
            if options.verbose:
                print '\n\tedit distances of other linker combinations:'
                for d in ed:
                    print '\t\t{0} <=> {1}; edit distance = {2}'.format(d[0],d[1],d[2])
            print '\n'
        else:
            print '{0} {1}\n\n\tthere is only 1 tag in this group'.format(options.section, g)

    
if __name__ == '__main__':
    main()