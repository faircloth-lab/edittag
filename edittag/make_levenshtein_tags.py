#!/usr/bin/env python
# encoding: utf-8

"""
make_levenshtein_tags.py

Created by Brant Faircloth on 28 May 2010 23:27 PDT (-0700).
Copyright (c) 2010 Brant C. Faircloth. All rights reserved.

USAGE:   python tag_maker.py --tag-length=8 --edit-distance=3 \
            --no-polybase --gc --comp --use-c --multiprocessing \
            --min-and-greater | tee 8_nt.txt
"""

import pdb
import os
import sys
import string
import itertools
import optparse
import numpy
import multiprocessing
import operator
import tempfile
import cPickle
from operator import itemgetter
# tested re2 DFA module in place of re2 here, but there were no substantial 
# performance gains for simple regex
import re
try:
    from Levenshtein import distance
    from Levenshtein import hamming
except:
    from lib.levenshtein import distance
    from lib.levenshtein import hamming


def interface():
    '''Command-line interface'''
    usage = "usage: %prog [options]"

    p = optparse.OptionParser(usage)

    p.add_option('--tag-length', dest = 'tl', action='store', 
type='int', default = 6, help='The desired tag length')
    
    p.add_option('--edit-distance', dest = 'ed', action='store', 
type='int', default = 3, help='The desired edit distance')

    p.add_option('--multiprocessing', dest = 'multiprocessing', 
action='store_true', default=False, help='Use multiprocessing')

    p.add_option('--processors', dest = 'nprocs', action='store', 
type='int', default = 6, help='The number of processing cores to use when' +
'using multiprocessing')

    p.add_option('--no-polybase', dest = 'polybase', action='store_true', default=False, 
help='Remove tags with > 2 identical nucleotides in a row')

    p.add_option('--gc', dest = 'gc', action='store_true', default=False, 
help='Remove tags with GC content (%) 40 > x > 60')

    p.add_option('--comp', dest = 'comp', action='store_true', default=False, 
help='Remove tags that are perfect self-complements')
    
    p.add_option('--use-c', dest = 'clev', action='store_true', default=False, 
help='Use the C version of Levenshtein (faster)')

    p.add_option('--min-and-greater', dest = 'greater', action='store_true', default=False, 
help='Show tags at all integer values of edit distance > that specified')

    p.add_option('--rescan', dest = 'rescan', action='store', type='string', 
default = None, help='Rescan a file')

    p.add_option('--rescan-length', dest = 'rescan_length', action='store', type='int', 
default = 6, help='Rescan length')


    (options,arg) = p.parse_args()
    if not options.tl:
        p.print_help()
        sys.exit(2)
    return options, arg

def pickler(stuff_to_dump, count = None):
    """ multiprocessing.Queue() doesn't dig having a lot of shit shoved through
    it (in terms of data volume).  So, although our remaining data sets are
    usually small, pickle them, store them in a temp file, and we'll
    get to them after the multiprocessing run.
    """
    if count:
        fd, tf = tempfile.mkstemp(suffix='.{0}.temptext'.format(count))
    else:
        fd, tf = tempfile.mkstemp(suffix='.temptext')
    os.close(fd)
    dump_file = open(tf, 'w')
    cPickle.dump(stuff_to_dump, dump_file)
    dump_file.close()
    return tf

def worker(tasks, results, edit_distance, tag_length):
    """we are going to generate a summary array of edit distances from of one 
    tag against all other tags like so, where the index position is equiv. to 
    the edit distance:
    
    [1, 12, 124, 5, 76]
    
    So, this tag has 1 tags that is edit distance 0 from it (the tag vs.
    itself), 12 tags in the entire set that are edit_distance 1
    from it; 124 that are edit distance 2 from it etc.  The rows of the array
    are the index of the alphabetically sorted tags.
    
    After this step, we're going to reduce the data, only getting those tags
    that have the most other tags that are in approrpriate edit-distance
    categories.  We're doing it this way, because we can greatly reduce the
    number of comparisons we have to make across the entire data set... e.g.
    from 14,500 x 14,500 to 14,500 x 120.
    """
    for position, chunks in iter(tasks.get, 'STOP'):
        # pretty output
        sys.stdout.write(".")
        sys.stdout.flush()
        # create an array to hold count of distances in difference classes on
        # a per-tag basis
        distance_array = numpy.zeros((len(chunks), tag_length+1), dtype=numpy.dtype('uint8'))
        for k, chunk in enumerate(chunks):
            # get the distances of a particular tag to all other tags, then 
            # group those counts into categories from 0 to max(edit_distance)
            distance_per_chunk = [Levenshtein.distance(chunk[0],c[1]) for c in chunk[1]]
            distance_per_chunk_counts = dict([(x, distance_per_chunk.count(x)) for x in set(distance_per_chunk)])
            # stick those values in an array
            for i in sorted(distance_per_chunk_counts.keys()):
                distance_array[k][i] = distance_per_chunk_counts[i]
        # see docstring for pickler
        tf = pickler(distance_array, position)
        results.put((position, tf))
        tasks.task_done()
    return

def get_reduced_distances(chunk, edit_distance):
    """
    Now that we've reduced the data set, we need to actually look at these tags
    that appear to have the most other tags some > min(edit_distance) from
    them.  We're going to do this by comparing each tag to the "base" tag
    that got it included in this set to begin with, and also comparing each 
    tag that we keep to all other tags that we keep to ensure that none are
    less than min(edit_distance from one another).  This was a stuggle to do
    simply and without consuming LOTS of RAM (e.g. numpy arrays), but the
    solution is rather simple.
    """
    all_keepers = []
    # get only those tags, compared to the base tag that have 
    # edit_distance >= our minimum - we're essentially regenerating
    # and filtering the pairwise comparisons above
    good_comparisons = [c for c in chunk[1] if \
        Levenshtein.distance(chunk[0],c[1]) >= edit_distance]
    # we know that the first tag is good (it is the basis for comparison),
    # so keep that one
    keepers = [chunk[0]]
    # now, loop over all the tags in the reduced set, checking each against
    # the tags already in 'keepers' for the proper edit distance
    for tag in good_comparisons:
        #pdb.set_trace()
        temp_dist = []
        skip = False
        for keep in keepers:
            d = Levenshtein.distance(keep,tag[1])
            if d < edit_distance:
                skip = True
                # no need to continue if we're already < edit_distance
                break
        if not skip:
            keepers.append(tag[1])
    # see docstring for pickler
    tf = pickler(keepers)
    return tf

def worker2(tasks, results, edit_distance):
    """this worker tasks sets up multiprocessing for the get_reduced_distances
    function"""
    for position, chunk in iter(tasks.get, 'STOP'):
        sys.stdout.write(".")
        sys.stdout.flush()
        tf = get_reduced_distances(chunk, edit_distance)
        # just cram the filename into the Queue()
        results.put(tf)
        tasks.task_done()
    return

def single_worker2(chunks, edit_distance):
    """this function sets up the single processing version of the 
    get_reduced_distances function"""
    results = []
    sys.stdout.write("\tThere are {0} chunks.\n\tProcessing: ".format(len(chunks), len(chunks[0][1])))
    for chunk in chunks:
        sys.stdout.write(".")
        sys.stdout.flush()
        tf = get_reduced_distances(chunk, edit_distance)
        results.append(tf)
    return results

def q_runner(n_procs, function, chunks, **kwargs):
    """a generic function that i use to start worker processes with all the
    appropriate bits and stuff"""
    myResults = []
    tasks     = multiprocessing.JoinableQueue()
    results   = multiprocessing.Queue()
    sys.stdout.write("\t[Info] There are {0} chunks.\n\tProcessing: ".format(len(chunks)))
    #sys.stdout.write("Processing: ")
    sys.stdout.flush()
    for k,v in enumerate(chunks):
        tasks.put([k, v])
    if len(chunks) < n_procs:
        n_procs = len(chunks)
    if 'tag_length' in kwargs:
        Workers = [multiprocessing.Process(target=function, args = 
            (tasks, results, kwargs['edit_distance'], kwargs['tag_length'])) for i in xrange(n_procs)]
    elif 'edit_distance' in kwargs:
        Workers = [multiprocessing.Process(target=function, args = 
            (tasks, results, kwargs['edit_distance'])) for i in xrange(n_procs)]
    elif 'regex' in kwargs:
        Workers = [multiprocessing.Process(target=function, args = 
            (tasks, results, kwargs['regex'], kwargs['options'])) for i in xrange(n_procs)]
    for each in Workers:
        each.start()
    for each in xrange(n_procs):
        tasks.put('STOP')
    for r in xrange(len(chunks)):
        myResults.append(results.get())
    #for process in Workers:
    #    process.join()
    tasks.close()
    results.close()
    return myResults

def chunker(good):
    """For each tag, create a set of tuple that includes
    
    (the tag, (all, other, tags),)
    
    We'll send these to our multiprocessing script.
    """
    chunked = ()
    ordered_tags = []
    # make sure the vectors are sorted
    good = sorted(good, key=itemgetter(1))
    for tag in good:
        chunked += ((tag[1], good),)
        ordered_tags.append(tag[1])
    return chunked, numpy.array(ordered_tags)

def self_comp(seq):
    """Return the reverse complement of seq"""
    bases = string.maketrans('AGCTagct','TCGAtcga')
    # translate it, reverse, return
    return seq[::-1].translate(bases)

def filter_tags(count, batch, regex, options):
    """Filter sequence tags based on criteria including poly-bases, gc content
    and self-complementarity."""
    good_tags = ()
    for tag in batch:
        tag_seq  = ''.join(tag)
        good = False
        if options.polybase:
            polybase = regex.search(tag_seq)
            if not polybase:
                good = True
        else:
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
    return pickler(good_tags)

def filter_tags_single_proc(batch, regex, options):
    """The single processing version of the tag filtereding code.  Here, I've
    maintained the use of a temporary pickle file just to keep things similar
    through the main loop (there are already enough decisions)"""
    count = 0
    return [filter_tags(count, batch, regex, options)]

def filter_tags_worker(tasks, results, regex, options):
    """The multiprocessing version of the tag filtering code."""
    for position, batch in iter(tasks.get, 'STOP'):
        count = 0
        sys.stdout.write(".")
        sys.stdout.flush()
        print '\n'
        tf = filter_tags(count, batch, regex, options)
        results.put(tf)
    return

def batches(tags, size):
    """Batch up our tags for filtering using multiprocessing.  Tried to do this
    using generators, but ran into problems with pickling to pass the objects
    off to multiprocessing.  This is a costly operation, so it should likely
    only be invoked when the length of each tag is long."""
    count = 0
    output = ()
    temp = ()
    for tag in tags:
        # if we're > size, then split and start new tuple
        if count != 0 and count % size == 0:
            temp += (tag,)
            output += (temp,)
            temp = ()
        else:
            temp += (tag,)
        count += 1
    # always make sure we add the last tuple, even if < 25000 units
    output += (temp,)
    return output

def get_rescan_generator(file, length):
    for line in open(file, 'rU').readlines():
        if line and not line.startswith('#'):
            tag_fragment = line.split('\t')[1][:length]
            yield tuple(tag_fragment)

def tag_rescanner(file, length):
    """if we need to rescan tags or parts of tags (e.g. first x bases) then 
    this does it"""
    rescanned_tags = {}
    for line in open(file, 'rU').readlines():
        if line and not line.startswith('#'):
            tag = line.split('\t')[1].strip()
            tag_fragment = tag[:length]
            rescanned_tags[tag_fragment] = tag
    g = get_rescan_generator(file, length)
    return rescanned_tags, g

            

def main():
    print "\n"
    print "##############################################################################"
    print "#  make_edit_distance_tags.py  - generate sequence tags of arbitrary length  #"
    print "#                                                                            #"
    print "#  Copyright (c) 2009-2010 Brant C. Faircloth                                #"
    print "#  621 Charles E. Young Drive                                                #"
    print "#  University of California, Los Angeles, 90095, USA                         #"
    print "##############################################################################"
    print "\n"
    good_tags = ()
    good_tags_dict = {}
    options, args = interface()
    print '[1] Generating all combinations of tags'
    if options.tl >= 9:
        print '\t[Warn] Slow when tag length > 8'
    if not options.rescan:
        all_tags = itertools.product('ACGT', repeat = options.tl)
    else:
        rescanned_tags, all_tags = tag_rescanner(options.rescan, options.rescan_length)
    pdb.set_trace()
    #if options.polybase:
    regex = re.compile('A{3,}|C{3,}|T{3,}|G{3,}')
    print '[2] If selected, removing tags based on filter criteria'
    if options.tl >= 9:
        print '\t[Warn] Slow when tag length > 8'
    if options.multiprocessing and options.tl >= 9:
        tag_batches = batches(all_tags, 25000)
        good_tag_files = q_runner(options.nprocs, filter_tags_worker, tag_batches, regex = regex, options = options)
    else:
        good_tag_files = filter_tags_single_proc(all_tags, regex, options)
    # read out filtered tags back from their temp pickles
    good_tags = []
    for filename in good_tag_files:
        temp_tags = cPickle.load(open(filename))
        good_tags.extend(temp_tags)
        os.remove(filename)
    pdb.set_trace()
    chunks, tags = chunker(good_tags)
    print '[3] There are {0} tags remaining after filtering'.format(len(chunks))
    print '[4] Calculating the Levenshtein distance across the tags'
    if options.multiprocessing:
        print '\t[Info] Using multiprocessing...'
    re_chunk = []
    # split tags up into groups of 500 each
    for i in xrange(0,len(chunks),500):
        group_chunk = chunks[i:i+500]
        re_chunk.append(group_chunk)
    if options.clev:
        print '\t[Info] Using the C version of Levenshtein...'
        #distance_pairs = getDistanceC(good_tags, distances = True)
        results = q_runner(options.nprocs, worker, re_chunk, edit_distance = options.ed, tag_length = options.tl)
        # need to rebuild the arrays from the component parts
        # first, ensure the filenames are sorted according to their input order
    if options.clev:
        results = sorted(results, key=itemgetter(0))
        distances = None
        for filename in results:
            temp_array = cPickle.load(open(filename[1]))
            if distances == None:
                distances = temp_array
            else:
                distances = numpy.vstack((distances, temp_array))
            #os.remove(filename[1])
        #pdb.set_trace()
        #distances, tags = worker(chunks, options.ed, options.tl)
    # find those tags with the comparisons >= options.ed
    if options.greater:
        all_distances = xrange(options.ed,options.tl)
    else:
        all_distances = [options.ed]
    for ed in all_distances:
        print '\n[5] Finding the set of tags with the most matches at edit_distance >= {0}'.format(ed)
        most_indices = numpy.nonzero(distances[:,ed] >= max(distances[:,ed]))[0]
        most_chunked = ()
        for tag in tags[most_indices]:
            most_chunked += ((tag, good_tags),)
        #all_keepers = worker2(most_chunked, ed)
        if options.multiprocessing:
            all_keepers = q_runner(options.nprocs, worker2, most_chunked, edit_distance = ed)
        else:
            all_keepers = single_worker2(most_chunked, ed)
        #pdb.set_trace()
        max_length = 0
        for filename in all_keepers:
            #pdb.set_trace()
            keeper = cPickle.load(open(filename))
            if len(keeper) > max_length:
                largest = keeper
            else:
                pass
            os.remove(filename)
        print '\n\n\tMinimum edit distance {0} tags'.format(ed)
        print '\t*****************************'
        for k,v in enumerate(largest):
            if not options.rescan:
                print "\tTag{0} = {1}".format(k,v)
            else:
                print "\tTag{0} = {1}, {2}".format(k,rescanned_tags[v],v)
        print '\n'

if __name__ == '__main__':
    main()
