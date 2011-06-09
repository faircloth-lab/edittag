#!/usr/bin/env python
# encoding: utf-8

"""
make_levenshtein_tags.py

Created by Brant Faircloth on 28 May 2010 23:27 PDT (-0700).
Copyright (c) 2010 Brant C. Faircloth. All rights reserved.

USAGE:  design_edit_metric_tags.py --tag-length=8 --edit-distance=3 \
            --no-polybase --gc --comp --multiprocessing \
            --min-and-greater | tee 8_nt.txt
"""

#import pdb
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
import ConfigParser
from operator import itemgetter
# tested re2 DFA module in place of re2 here, but there were no substantial 
# performance gains for simple regex
import re


def interface():
    '''Command-line interface'''
    usage = "usage: %prog [options]"

    p = optparse.OptionParser(usage)
    
    p.add_option('--output', dest = 'output', action='store', type='string', 
default = None, help='The path to the file where you want to store the '+
'barcodes', metavar='FILE')

    p.add_option('--tag-length', dest = 'tl', action='store', 
type='int', default = 6, help='The desired tag length')
    
    p.add_option('--edit-distance', dest = 'ed', action='store', 
type='int', default = 3, help='The desired edit distance')

    p.add_option('--multiprocessing', dest = 'multiprocessing', 
action='store_true', default=False, help='Use multiprocessing')

    p.add_option('--processors', dest = 'nprocs', action='store', 
type='int', default = None, help='The number of processing cores to use when' +
' using multiprocessing.  Default is # of cores - 2')

    p.add_option('--no-polybase', dest = 'polybase', action='store_true', default=False, 
help='Remove tags with > 2 identical nucleotides in a row')

    p.add_option('--gc', dest = 'gc', action='store_true', default=False, 
help='Remove tags with GC content (%) 40 > x > 60')

    p.add_option('--comp', dest = 'comp', action='store_true', default=False, 
help='Remove tags that are perfect self-complements')

    p.add_option('--hamming', dest = 'hamming', action='store_true', default=False, 
help='Use Hamming distance in place of edit (Levenshtein) distance.')
    
    # c is on by default now
    #p.add_option('--use-c', dest = 'clev', action='store_true', default=False, 
#help='Use the C version of Levenshtein (faster)')

    p.add_option('--min-and-greater', dest = 'greater', action='store_true', default=False, 
help='Show tags at all integer values of edit distance > that specified')

    p.add_option('--rescan', dest = 'rescan', action='store', type='string', 
default = None, help='Rescan a file')

    p.add_option('--rescan-length', dest = 'rescan_length', action='store', type='int', 
default = 6, help='Rescan length')

        

    (options,arg) = p.parse_args()
    assert options.nprocs <= multiprocessing.cpu_count(), \
        "Processors count must equal those available"
    # set the number of processors by default
    if options.multiprocessing and not options.nprocs:
        options.nprocs = multiprocessing.cpu_count() - 2
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

def first_pass_tag_distance(chunks, edit_distance, tag_length, position = 1):
    # create an array to hold count of distances in difference classes on
    # a per-tag basis
    distance_array = numpy.zeros((len(chunks), tag_length+1), dtype=numpy.dtype('uint8'))
    for k, chunk in enumerate(chunks):
        # get the distances of a particular tag to all other tags, then 
        # group those counts into categories from 0 to max(edit_distance)
        distance_per_chunk = [distance(chunk[0],c[1]) for c in chunk[1]]
        distance_per_chunk_counts = dict([(x, distance_per_chunk.count(x)) for x in set(distance_per_chunk)])
        # stick those values in an array
        for i in sorted(distance_per_chunk_counts.keys()):
            distance_array[k][i] = distance_per_chunk_counts[i]
    # see docstring for pickler
    return pickler(distance_array, position)

def first_pass_tag_distance_worker(tasks, results, edit_distance, tag_length):
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
        tf = first_pass_tag_distance(chunks, edit_distance, tag_length, position)
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
        distance(chunk[0],c[1]) >= edit_distance]
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
            d = distance(keep,tag[1])
            if d < edit_distance:
                skip = True
                # no need to continue if we're already < edit_distance
                break
        if not skip:
            keepers.append(tag[1])
    # see docstring for pickler
    tf = pickler(keepers)
    return tf

def second_pass_tag_distance_worker(tasks, results, edit_distance):
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

def multiprocessing_queue(n_procs, function, chunks, **kwargs):
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
        good = True
        if options.polybase:
            polybase = regex.search(tag_seq)
            if polybase:
                good = False
        if options.gc:
            gc = (tag_seq.count('G') + tag_seq.count('C')) / float(len(tag))
            if not 0.40 <= gc <= 0.60:
                good = False
        if options.comp:
            if tag_seq == self_comp(tag_seq):
                good = False
        if good:
            tag_name = '{0}'.format(count)
            good_tags += ((tag_name, tag_seq),)
            count += 1
    return pickler(good_tags)

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

def make_tag_batches(tags, size):
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

def get_rescan_generator(file, length, tags):
    for name, tag in tags:
        tag_fragment = tag[:length]
        yield tuple(tag_fragment)

def tag_rescanner(file, length):
    """if we need to rescan tags or parts of tags (e.g. first x bases) then 
    this does it"""
    conf = ConfigParser.ConfigParser()
    conf.read(file)
    # assert there is only one section
    assert len(conf.sections()) == 1, "You may only rescan a single-section input file"
    #pdb.set_trace()
    # get tags for section
    rescanned_tags = {}
    tags = conf.items(conf.sections()[0])
    for name, tag in tags:
            tag_fragment = tag[:length]
            rescanned_tags[tag_fragment] = tag
    g = get_rescan_generator(file, length, tags)
    return rescanned_tags, g

def results_to_stdout(ed, largest, options, rescanned_tags):
    """pretty print our results to stdout"""
    print '\n\n\tMinimum edit distance {0} tags'.format(ed)
    print '\t*****************************'
    for k,v in enumerate(largest):
        if not options.rescan:
            print "\tTag{0} = {1}".format(k,v)
        else:
            print "\tTag{0} = {1}, {2}".format(k,rescanned_tags[v],v)
    print '\n'

def results_to_outfile(ed, largest, options, rescanned_tags, outfile):
    """write our results to an outfile in formats accepted by our 
    other programs"""
    outfile.write("[{0}nt ed{1}]\n".format(options.tl, ed))
    for k,v in enumerate(largest):
        if not options.rescan:
            outfile.write("Tag{0}:{1}\n".format(k,v))
        else:
            outfile.write("\tTag{0}:{1},{2}\n".format(k,rescanned_tags[v],v))
    print '\n'

def main():
    print "\n"
    print "##############################################################################"
    print "#  design_edit_metric_tags.py  - generate sequence tags of arbitrary length  #"
    print "#                                                                            #"
    print "#  Copyright (c) 2009-2011 Brant C. Faircloth                                #"
    print "#  621 Charles E. Young Drive                                                #"
    print "#  University of California, Los Angeles, 90095, USA                         #"
    print "##############################################################################"
    print "\n"
    good_tags = ()
    good_tags_dict = {}
    options, args = interface()
    if not options.hamming:
        try:
            from Levenshtein import distance
        except ImportError:
            from edittag.levenshtein import distance
    else:
        print "[Info] Using **Hamming** distances"
        try:
            from Levenshtein import hamming as distance
        except ImportError:
            from edittag.levenshtein import hamming as distance
    # make the import global, otherwise the scope will be limited to main()
    global distance
    regex = re.compile('A{3,}|C{3,}|T{3,}|G{3,}')
    if options.multiprocessing:
        print "[Info] Using multiprocessing with {0} cores".format(options.nprocs)
    # Generate tags
    print '[1] Generating all combinations of tags'
    if options.tl >= 9:
        print '\t[Warn] Slow when tag length > 8'
    if not options.rescan:
        all_tags = itertools.product('ACGT', repeat = options.tl)
        rescanned_tags = None
    else:
        # this is sort of lazy, but to keep from having to rewrite
        # code, just set the options.tl value to options.rescan_length
        options.tl = options.rescan_length
        rescanned_tags, all_tags = tag_rescanner(options.rescan, options.tl)
    # Filter tags
    print '[2] If selected, removing tags based on filter criteria'
    if options.tl >= 9:
        print '\t[Warn] Slow when tag length > 8'
    if options.multiprocessing and options.tl >= 9:
        tag_batches = make_tag_batches(all_tags, 25000)
        filtered_tag_files = multiprocessing_queue(
                            options.nprocs, 
                            filter_tags_worker, 
                            tag_batches, 
                            regex = regex, 
                            options = options
                            )
    else:
        filtered_tag_files = [filter_tags(0, all_tags, regex, options)]
    # read filtered tags back from their temp pickles
    good_tags = []
    for filename in filtered_tag_files:
        temp_tags = cPickle.load(open(filename))
        good_tags.extend(temp_tags)
        os.remove(filename)
    chunks, tags = chunker(good_tags)
    print '[3] There are {0} tags remaining after filtering'.format(len(chunks))
    # First pass tag distance
    print '[4] Calculating the Levenshtein distance across the tags'
    if options.multiprocessing:
        re_chunk = []
        # split tags up into groups of 500 each
        for i in xrange(0,len(chunks),500):
            group_chunk = chunks[i:i+500]
            re_chunk.append(group_chunk)
        results = multiprocessing_queue(options.nprocs, 
                            first_pass_tag_distance_worker, 
                            re_chunk, 
                            edit_distance = options.ed, 
                            tag_length = options.tl
                            )
        # we need to rebuild the arrays from the component parts
        # first, ensure the filenames are sorted according to their input order
        results = sorted(results, key=itemgetter(0))
    else:
        # mock the return from multiprocessing_queue to we don't need to change below
        results = [(0, first_pass_tag_distance(chunks, options.ed, options.tl),)]
    distances = None
    for filename in results:
        temp_array = cPickle.load(open(filename[1]))
        if distances == None:
            distances = temp_array
        else:
            distances = numpy.vstack((distances, temp_array))
    
    # Find those tags with the comparisons >= options.ed
    if options.greater:
        all_distances = xrange(options.ed,options.tl)
    else:
        all_distances = [options.ed]
    if options.output:
        outfile = open(options.output, 'w')
    # Second pass tag distances
    for ed in all_distances:
        print '[5] Finding the set of tags with the most matches at edit_distance >= {0}'.format(ed)
        most_indices = numpy.nonzero(distances[:,ed] >= max(distances[:,ed]))[0]
        most_chunked = ()
        for tag in tags[most_indices]:
            most_chunked += ((tag, good_tags),)
        if options.multiprocessing:
            all_keepers = multiprocessing_queue(
                            options.nprocs, 
                            second_pass_tag_distance_worker, 
                            most_chunked, 
                            edit_distance = ed)
        else:
            all_keepers = [get_reduced_distances(chunk, ed) for chunk in most_chunked]
        max_length = 0
        for filename in all_keepers:
            keeper = cPickle.load(open(filename))
            if len(keeper) > max_length:
                largest = keeper
            else:
                pass
            os.remove(filename)
        if not options.output:
            results_to_stdout(ed, largest, options, rescanned_tags)
        else:
            results_to_outfile(ed, largest, options, rescanned_tags, outfile)
    if options.output:
        outfile.close()

if __name__ == '__main__':
    main()
