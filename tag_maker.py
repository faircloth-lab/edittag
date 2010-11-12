#!/usr/bin/env python
# encoding: utf-8

"""
tag_maker.py

Created by Brant Faircloth on 28 May 2010 23:27 PDT (-0700).
Copyright (c) 2010 Brant C. Faircloth. All rights reserved.
"""

import pdb
import os
import re
import sys
import string
import itertools
import optparse
import numpy
import multiprocessing
import Levenshtein
import operator
import tempfile
import cPickle
from operator import itemgetter
#from levenshtein import getDistance
#from levenshtein import getDistanceC


def interface():
    '''Command-line interface'''
    usage = "usage: %prog [options]"

    p = optparse.OptionParser(usage)

    p.add_option('--tag-length', dest = 'tl', action='store', 
type='int', default = 6, help='The desired tag length')
    
    p.add_option('--edit-distance', dest = 'ed', action='store', 
type='int', default = 3, help='The desired edit distance')

    p.add_option('--no-polybase', dest = 'polybase', action='store_true', default=False, 
help='Remove tags with > 2 identical nucleotides in a row')

    p.add_option('--gc', dest = 'gc', action='store_true', default=False, 
help='Remove tags with GC content (%) 40 > x > 60')

    p.add_option('--comp', dest = 'comp', action='store_true', default=False, 
help='Remove tags that are perfect self-complements')
    
    p.add_option('--use-c', dest = 'clev', action='store_true', default=False, 
help='Use the C version of Levenshtein (faster)')


    (options,arg) = p.parse_args()
    if not options.tl:
        p.print_help()
        sys.exit(2)
    return options, arg


def getDistanceC1(chunk_index, chunk_values, good_tags, temp_array, *args, **kwargs):
    #pdb.set_trace()
    #linker_dist = []
    for p1, s1 in enumerate(chunk_values):
        #new_chunk_index = chunk_index
        p2 = p1 + 1
        for s2 in chunk_values[p2:]:
            edit_distance = Levenshtein.distance(s1[1],s2[1])
            try:
                temp_array[p1, p2] = edit_distance
            except IndexError:
                pdb.set_trace()
            p2 += 1
        #chunk_index += 1
    #return sorted(linker_dist, key=operator.itemgetter(2))
    #pdb.set_trace()
    return temp_array


def getDistanceC(chunk_index, chunk_values, good_tags, temp_array, *args, **kwargs):
    #pdb.set_trace()
    #linker_dist = []
    for p1, s1 in enumerate(chunk_values):
        new_chunk_index = chunk_index
        for p2, s2 in enumerate(good_tags[new_chunk_index + 1:]):
            new_chunk_index += p2
            #print '\t', s1, new_chunk_index + 1
            edit_distance = Levenshtein.distance(s1[1],s2[1])
            temp_array[int(s1[0]),int(s2[0])] = int(edit_distance)
            #if edit_distance >= 5:
            #    p_file.write('{0},{1},{2}\n'.format(s1[0], s2[0], edit_distance))
        #print chunk_index
        chunk_index += 1
        #pdb.set_trace()
    #return sorted(linker_dist, key=operator.itemgetter(2))
    #pdb.set_trace()
    return temp_array
        

def worker(tasks, results):
    for chunk, good_tag, count in iter(tasks.get, 'STOP'):
        # create an array for the data
        chunk_index = chunk[0][0]
        chunk_values = chunk[1]
        temp_array = numpy.zeros((count, count), dtype=numpy.dtype('uint8'))
        #print '\t[P] Serializing the data and writing it to a tempfile...'
        fd, tf = tempfile.mkstemp(suffix='.temptext')
        os.close(fd)
        p_file = open(tf, 'w')
        #print '[4] Writing results to temporary file {0}...'.format(tf)
        distance = getDistanceC(chunk_index, chunk_values, good_tag, temp_array, distances = True)
        #for d in distance:
        #    
        cPickle.dump(distance, p_file)
        p_file.close()
        results.put(tf)
        tasks.task_done()
    return

def single_worker(tasks, results, edit_distance, tag_length):
    for position, chunks in iter(tasks.get, 'STOP'):
        # just to ensure we're putting things where we think...
        distance_array = numpy.zeros((len(chunks), tag_length+1), dtype=numpy.dtype('uint8'))
        print "chunk of {0}".format(len(chunks))
        for k, chunk in enumerate(chunks):
            distance_per_chunk = [Levenshtein.distance(chunk[0],c[1]) for c in chunk[1]]
            distance_per_chunk_counts = dict([(x, distance_per_chunk.count(x)) for x in set(distance_per_chunk)])
            # stick those values in an array
            for i in sorted(distance_per_chunk_counts.keys()):
                distance_array[k][i] = distance_per_chunk_counts[i]
            #pdb.set_trace()
            #if k % 100 == 0:
            #    print "\t\tTag {0}".format(k)
        fd, tf = tempfile.mkstemp(suffix='.temptext')
        os.close(fd)
        d_array = open(tf, 'w')
        cPickle.dump(distance_array, d_array)
        d_array.close()
        results.put((position, tf))
        tasks.task_done()
    return

def single_worker2(chunks, edit_distance):
    all_keepers = []
    print "[5] Scanning {0} reduced tag sets (slow)...".format(len(chunks))
    for k, chunk in enumerate(chunks):
        print "\t\tSet {0}".format(k)
        # get only those tags, compared to the base tag that have 
        # edit_distance >= our minimum - we're essentially regenerating
        # and filtering the pairwise comparisons above
        good_comparisons = [c for c in chunk[1] if \
            Levenshtein.distance(chunk[0],c[1]) >= edit_distance]
        # add in the base tag.  this is now the set of tags, when compared
        # to the base tag, that have edit distance >= 5
        good_comparisons.insert(0,('0', chunk[0]))
        # now we need to compare all the tags to one another, not just to the
        # base tag
        #results = [[Levenshtein.distance(row[1], column[1]) for column in good_comparisons] for row in good_comparisons]
        results = []
        tags = numpy.array([])
        for k,row in enumerate(good_comparisons):
            tags = numpy.append(tags, row[1])
            column = [0] * len(good_comparisons)
            for k2, element in enumerate(good_comparisons[k:]):
                column[k + k2] = Levenshtein.distance(row[1], element[1])
            results.append(column)
        results = numpy.array(results)
        keepers = numpy.array([], dtype=int)
        for k,v in enumerate(results[:,0]):
            # append the 0th element (our base tag)
            if not keepers.any():
                keepers = numpy.append(keepers,k)
            # get the column of edit distances for k and reshape it
            else:
                column_to_row = numpy.reshape(results[:,k], len(results[:,k]))
                # reindex it by the tags we already have in the set
                if sum(column_to_row[keepers] >= edit_distance) == len(column_to_row[keepers]):
                    keepers = numpy.append(keepers,int(k))
        # we need to get all sets of keepers across all chunks.  we will
        # determine the largest batch later...
        all_keepers.append(tags[keepers])
    return all_keepers

def q_runner(n_procs, function, chunks, edit_distance, **kwargs):
    '''generic function used to start worker processes'''
    myResults = []
    tasks     = multiprocessing.JoinableQueue()
    results   = multiprocessing.Queue()
    re_chunk = []
    for i in xrange(0,len(chunks),500):
        group_chunk = chunks[i:i+500]
        re_chunk.append(group_chunk)
    for k,v in enumerate(re_chunk):
        if kwargs['tag_length']:
            tasks.put([k, v])
        else:
            tasks.put([k, v])
    if len(re_chunk) < n_procs:
        n_procs = len(re_chunk)   
    Workers = [multiprocessing.Process(target=function, args = (tasks, results, edit_distance, kwargs['tag_length'])) for i in xrange(n_procs)]
    for each in Workers:
        each.start()
    for each in xrange(n_procs):
        tasks.put('STOP')
    for process in Workers:
        process.join()
    for r in xrange(len(re_chunk)):
        myResults.append(results.get())
    tasks.close()
    results.close()
    #pdb.set_trace()
    return myResults

def chunker(good):
    """chunk shit up"""
    chunked = ()
    ordered_tags = []
    # make sure the vectors are sorted
    good = sorted(good, key=itemgetter(1))
    for tag in good:
        chunked += ((tag[1], good),)
        ordered_tags.append(tag[1])
    #chunked = []
    #for i in xrange(0, len(l), n):
    #    chunked.append([[i],l[i:i+n]])
    return chunked, numpy.array(ordered_tags)

def self_comp(seq):
    '''Return reverse complement of seq'''
    bases = string.maketrans('AGCTagct','TCGAtcga')
    # translate it, reverse, return
    return seq[::-1].translate(bases)

def main():
    print '''
########################################
#  Tag Generator                       #
########################################
        '''
    n_procs = 6
    count = 0
    good_tags = ()
    good_tags_dict = {}
    options, args = interface()
    print '[1] Generating all combinations of tags...'
    all_tags = itertools.product('ACGT', repeat = options.tl)
    if options.polybase:
        regex = re.compile('A{3,}|C{3,}|T{3,}|G{3,}')
    print '[2] If selected, removing tags based on filter criteria...'
    for tag in all_tags:
        #pdb.set_trace()
        tag_seq  = ''.join(tag)
        good = False
        if options.polybase:
            polybase = regex.search(tag_seq)
            if not polybase:
                good = True
        if good and options.gc:
            gc = (tag_seq.count('G') + tag_seq.count('C')) / float(len(tag))
            if 0.40 <= gc <= 0.60:
                good = True
            else:
                good = False
        if good and options.comp:
            if tag_seq != self_comp(tag_seq):
                good = True
            else:
                good = False
        if good:
            tag_name = '{0}'.format(count)
            good_tags += ((tag_name, tag_seq),)
            count += 1
    chunks, tags = chunker(good_tags)
    print '[1] There are {0} chunks'.format(len(chunks))
    print '[2] Calculating the Levenshtein distance across the chunks... (Slow)'
    if options.clev:
        print '\t[C] Using the C version of Levenshtein...'
        #distance_pairs = getDistanceC(good_tags, distances = True)
        results = q_runner(6, single_worker, chunks, options.ed, tag_length = options.tl)
        # need to rebuild the arrays from the component parts
        # first, ensure the filenames are sorted according to their input order
        results = sorted(results, key=itemgetter(0))
        distances = None
        print results
        for filename in results:
            temp_array = cPickle.load(open(filename[1]))
            if distances == None:
                distances = temp_array
            else:
                distances = numpy.vstack((distances, temp_array))
            os.remove(filename[1])
        #pdb.set_trace()
        #distances, tags = single_worker(chunks, options.ed, options.tl)
    # find those tags with the comparisons >= options.ed
    print '[4] Finding the set of tags with the most matches at edit_distance >= {0}'.format(options.ed)
    most_indices = numpy.nonzero(distances[:,options.ed] >= max(distances[:,options.ed]))[0]
    most_chunked = ()
    for tag in tags[most_indices]:
        most_chunked += ((tag, good_tags),)
    all_keepers = single_worker2(most_chunked, options.ed)
    max_length = 0
    for keeper in all_keepers:
        if len(keeper) > max_length:
            largest = keeper
        else:
            pass
    for k,v in enumerate(largest):
        print "Tag{0} = {1}".format(k,v)

if __name__ == '__main__':
    main()