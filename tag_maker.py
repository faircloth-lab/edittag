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
import levenshtein
import operator
import tempfile
import cPickle
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

def single_worker(chunk, good_tag, edit_distance, final = False):
    #pdb.set_trace()
    best_tags = []
    for c in chunk:
        chunk_index = c[0][0]
        chunk_values = c[1]
        temp_array = numpy.zeros((len(chunk_values), len(chunk_values)), dtype=numpy.dtype('uint8'))
        #print '\t[P] Serializing the data and writing it to a tempfile...'
        fd, tf = tempfile.mkstemp(suffix='.temptext')
        #os.close(fd)
        p_file = open(tf, 'w')
        #print '[4] Writing results to temporary file {0}...'.format(tf)
        temp_array = getDistanceC(chunk_index, chunk_values, good_tag, temp_array, distances = True)
        for r, row in enumerate(temp_array):
            for c, column in enumerate(row):
                p_file.write('{0}\t'.format(column))
            p_file.write('\n')
        p_file.close()        
        pdb.set_trace()
        # get the full array from its 1/2
        full_temp_array = temp_array + temp_array.transpose()
        # get the vector (row) of data with the largest count of tags with edit
        # distance > edit_distance
        positions = []
        holder = []
        all_edit_distances = (full_temp_array >= edit_distance).sum(axis = 1)
        for pos, row in enumerate(all_edit_distances):
            if row == max(all_edit_distances):
                counts = numpy.bincount(full_temp_array[pos])
                positions.append(pos)
                holder.append(counts.tolist())
        # get index of the row containing the most differences from other tags
        # if there is a tie, this should return the first element meeting the
        # criteria
        best_row = positions[holder.index(max(holder))]
        print chunk_values[best_row]
        best_tags.append(chunk_values[best_row])
        #pdb.set_trace()
    if not final:
        return best_tags
    else:
        pdb.set_trace()
        print all_edit_distances[best_row]
            

def q_runner(n_procs, chunks, good_tags, count, function, *args):
    '''generic function used to start worker processes'''
    myResults = []
    tasks     = multiprocessing.JoinableQueue()
    results   = multiprocessing.Queue()
    print 'there are {0} chunks'.format(len(chunks))
    for each in chunks:
        tasks.put([each, good_tags, count])
    #pdb.set_trace()    
    Workers = [multiprocessing.Process(target=worker, args = (tasks, results)) for i in xrange(n_procs)]
    for each in Workers:
        each.start()
    for each in xrange(n_procs):
        tasks.put('STOP')
    for process in Workers:
        process.join()
    for r in xrange(len(chunks)):
        myResults.append(results.get())
    tasks.close()
    results.close()
    #pdb.set_trace()
    return myResults

def chunker(l, n):
    '''Yield successive n-sized chunks from l'''
    chunked = []
    for i in xrange(0, len(l), n):
        chunked.append([[i],l[i:i+n]])
    return chunked

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
    good_tags = []
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
            good_tags.append((tag_name, tag_seq))
            count += 1
    # index the boogers, so we can pull out the good ones
    for k, v in good_tags:
        good_tags_dict.setdefault(int(k), []).append(v)
    # chunk the good_tags list into nproc approx evenly sized chunks
    # 500 is a bit too big with 8GB RAM
    #pdb.set_trace()
    if len(good_tags)/n_procs > 250:
        chunk_count = 250
    else:
        chunk_count = len(good_tags)/n_procs
    chunks = list(chunker(good_tags, chunk_count))
    print '[I] There are {0} chunks of size {1}'.format(len(chunks), chunk_count)
    print '[I] Count = {0}'.format(count)
    # get the pairwise distance
    #pdb.set_trace()
    print '[3] Calculating the Levenshtein distance across remaining pairs... (Slow)'
    if options.clev:
        print '\t[C] Using the C version of Levenshtein...'
        #distance_pairs = getDistanceC(good_tags, distances = True)
        results = q_runner(n_procs, chunks, good_tags, count, worker)
        #results = single_worker(chunks, good_tags, options.ed)
    #else:
    #    distance_pairs = getDistance(good_tags, distances = True)
    
    #single_worker([[[0], results]], good_tags, options.ed, final=True)
    #pdb.set_trace()
    hm = numpy.zeros((count, count), dtype=numpy.dtype('uint8'))
    print '[4] Reading text output into array...'
    for infile in results:
        pkl = open(infile, 'r')
        temp_array = cPickle.load(pkl)
        hm += temp_array
        pkl.close()
        #for tag_pair in pkl.readlines():
        #    #pdb.set_trace()
        #    # jam all of our distances into an array
        #    t1, t2, d = [int(i) for i in tag_pair.strip('\n').split(',')]
        #    hm[t1,t2] = d
    #pdb.set_trace()    
    print '[5] Empirically determining the greatest number of returnable tags of Levenshtein distance {0}...'.format(options.ed)
    # get the vector (row) of data with the largest count of tags with edit
    # distance > options.ed
    max_row_sum = [None, 0]
    for pos, row in enumerate(hm):
        bool_row_sum = sum(row >= options.ed)
        if bool_row_sum > max_row_sum[1]:
            max_row_sum = [pos, bool_row_sum]
    # get the indices of those values with edit distances >= options.ed
    best_row = hm[max_row_sum[0]]
    #pdb.set_trace()
    index = numpy.argwhere(best_row >= options.ed)
    keepers = numpy.array([], dtype=int)
    for i in index:
        if not keepers.any():
            keepers = numpy.append(keepers,int(i))
        else:
            # get the column of edit distances for i and reshape it
            column_to_row = numpy.reshape(hm[:,i], len(hm[:,i]))
            # reindex by the keepers
            if sum(column_to_row[keepers] >= options.ed) == len(column_to_row[keepers]):
                keepers = numpy.append(keepers,int(i))
    print '\n'
    #pdb.set_trace()
    for k in keepers:
        print 'Tag{0} = {1}'.format(k, good_tags_dict[k][0])
    #print chunk_values[best_row]
    #best_tags.append(chunk_values[best_row])
    
    #pdb.set_trace()    
    #outp.close()

if __name__ == '__main__':
    main()