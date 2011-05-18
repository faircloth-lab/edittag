#!/usr/bin/env python
# encoding: utf-8

"""
add_tags_to_primers.py

Created by Brant Faircloth on 04 October 2010 11:02 PDT (-0700).
Copyright (c) 2010 Brant C. Faircloth. All rights reserved.

USAGE:  add_tags_to_primers.py --left-primer=GTTATGCATGAACGTAATGCTC --right-primer=CGCGCATGGTGGATTCACAATCC \
    --input tmp/tags.txt --section='6nt ed3'
    --sort=pair_hairpin_either,pair_penalty,cycles \
    --remove-common --keep-database \
    --output tmp/trnH_tagged_with_10_nt_ed_5_tags.csv

"""

import pdb
import os
import sys
import numpy
import sqlite3
import optparse
import ConfigParser
from operator import itemgetter

from edittag.primer3 import primer
from edittag.helpers import get_tag_flows
from edittag.helpers import get_tag_array


def interface():
    '''Command-line interface'''
    usage = "usage: %prog [options]"

    p = optparse.OptionParser(usage)

    p.add_option('--input', dest = 'input', action='store', 
        type='string', default = None, help='The path to the sequence tag file.',
        metavar='FILE')
    
    p.add_option('--section', dest = 'section', action = 'store',
        type='string', default = None, help='[Optional] The section of'
        +' the config file to evaluate')
        
    p.add_option('--left-primer', dest = 'left', action='store', 
        type='string', default = None, help='The left primer to tag.')
        
    p.add_option('--right-primer', dest = 'right', action='store', 
        type='string', default = None, help='The right primer to tag.')
        
    p.add_option('--output', dest = 'output', action='store', 
        type='string', default = None, 
        help='The path to file for program output.',
        metavar='FILE')
    
    p.add_option('--fusion', dest = 'fusion', action='store_true', 
        default=False, help='Design 454-style `fusion` primers.')

    p.add_option('--fusion-pairs', dest = 'fusion_pairs', action='store_true', 
        default=False, help='Evaluate pairs of fusion primers')
    
    p.add_option('--pigtail', dest = 'pigtail', action='store_true', 
        default=False, help='Pigtail each tagged primer sequence.')
        
    p.add_option('--pigtail-sequence', dest = 'pigtail_seq', action='store', 
        type='string', default = 'GTTT', help='The pigtail sequence to add')
        
    p.add_option('--sort', dest = 'sort_keys', action='store', 
            type='string', default = None, 
            help='Comma-separated list of columns on which to sort.')
            
    p.add_option('--remove-common', dest = 'common', action='store_true', default=False, 
            help='Remove common bases between the pigtail and sequence tag')
            
    p.add_option('--keep-database', dest = 'keepdb', action='store_true', default=False, 
            help='Keeps the database')

    (options,arg) = p.parse_args()
    options.input = os.path.abspath(os.path.expanduser(options.input))
    if options.output:
        options.output = os.path.abspath(os.path.expanduser(options.output))
    if not options.left and options.right:
        print "You must provide a valid left and right primer sequence."
        p.print_help()
        sys.exit(2)
    if not os.path.isfile(options.input):
        print "You must provide a valid path to the tag file."
        p.print_help()
        sys.exit(2)
    if not options.output and not options.keepdb:
        print "You must output to a file `--output=something.csv` or `--output=my_database.sqlite --keep-database`."
        p.print_help()
        sys.exit(2)
    return options, arg 

def create_database(cur):
    """create the database to hold our results"""
    cur.execute('''CREATE TABLE primers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        section text,
        unmodified text,
        tag text,
        cycles int,
        left_tag_common text,
        left_tag text,
        left_sequence text,
        left_tm real,
        left_gc real,
        left_self_end real,
        left_self_any real,
        left_hairpin real,
        left_end_stability real,
        left_penalty real,
        left_problems text,
        right_tag_common text,
        right_tag text,
        right_sequence text,
        right_tm real,
        right_gc real,
        right_self_end real,
        right_self_any real,
        right_hairpin real,
        right_end_stability real,
        right_penalty real,
        right_problems text,
        pair_compl_end real,
        pair_compl_any real,
        pair_hairpin_either int,
        pair_penalty real
        )''')

def insert_primers(cur, data):
    """insert our tagged primers to the database"""
    query = ('''INSERT INTO primers (
        section,
        unmodified,
        tag,
        cycles,
        left_tag_common,
        left_tag,
        left_sequence,
        left_tm,
        left_gc,
        left_self_end,
        left_self_any,
        left_hairpin,
        left_end_stability,
        left_penalty,
        left_problems,
        right_tag_common,
        right_tag,
        right_sequence,
        right_tm,
        right_gc,
        right_self_end,
        right_self_any,
        right_hairpin,
        right_end_stability,
        right_penalty,
        right_problems,
        pair_compl_end,
        pair_compl_any,
        pair_hairpin_either,
        pair_penalty
        )
    VALUES (
        :SECTION,
        :UNMODIFIED,
        :TAG,
        :CYCLES,
        :PRIMER_LEFT_TAG_COMMON_BASES,
        :PRIMER_LEFT_TAG,
        :PRIMER_LEFT_SEQUENCE,
        :PRIMER_LEFT_TM,
        :PRIMER_LEFT_GC_PERCENT,
        :PRIMER_LEFT_SELF_END_TH,
        :PRIMER_LEFT_SELF_ANY_TH,
        :PRIMER_LEFT_HAIRPIN_TH,
        :PRIMER_LEFT_END_STABILITY,
        :PRIMER_LEFT_PENALTY,
        :PRIMER_LEFT_PROBLEMS,
        :PRIMER_RIGHT_TAG_COMMON_BASES,
        :PRIMER_RIGHT_TAG,
        :PRIMER_RIGHT_SEQUENCE,
        :PRIMER_RIGHT_TM,
        :PRIMER_RIGHT_GC_PERCENT,
        :PRIMER_RIGHT_SELF_END_TH,
        :PRIMER_RIGHT_SELF_ANY_TH,
        :PRIMER_RIGHT_HAIRPIN_TH,
        :PRIMER_RIGHT_END_STABILITY,
        :PRIMER_RIGHT_PENALTY,
        :PRIMER_RIGHT_PROBLEMS,
        :PRIMER_PAIR_COMPL_END_TH,
        :PRIMER_PAIR_COMPL_ANY_TH,
        :PAIR_HAIRPIN_EITHER,
        :PRIMER_PAIR_PENALTY)''')
    try:
        cur.execute(query, data)
    except sqlite3.ProgrammingError:
        pdb.set_trace()

def get_primer3_settings():
    """set the tagging parameters of a particular primer"""
    settings = primer.Settings(binary='primer3_long')
    settings.reduced()
    settings.params['PRIMER_MAX_SIZE']                  = 55
    settings.params['PRIMER_PICK_ANYWAY']               = 1
    settings.params['PRIMER_MIN_GC']                    = 30.0  # percent
    settings.params['PRIMER_OPT_GC_PERCENT']            = 50.0  # percent
    settings.params['PRIMER_MAX_GC']                    = 70.0  # percent
    settings.params['PRIMER_GC_CLAMP']                  = 1     # boolean
    settings.params['PRIMER_MAX_SELF_ANY_TH']           = 45.   # deg C
    settings.params['PRIMER_PAIR_MAX_COMPL_ANY_TH']     = 45.   # deg C
    settings.params['PRIMER_MAX_SELF_END_TH']           = 40.   # deg C
    settings.params['PRIMER_PAIR_MAX_COMPL_END_TH']     = 40.   # deg C
    # there are going to be hairpins - let's try and make sure they melt
    settings.params['PRIMER_MAX_HAIRPIN_TH']            = 40.   # deg C
    settings.params['PRIMER_PAIR_MAX_HAIRPIN_TH']       = 40.   # deg C
    settings.params['PRIMER_MAX_END_STABILITY']         = 8.5   # delta G
    return settings

def write_results(cur, output, sort):
    """function to create the output"""
    o = open(output, 'w')
    # get header info
    cur.execute('''PRAGMA table_info( primers )''')
    header = ','.join([i[1] for i in cur.fetchall()])
    o.write('{0}\n'.format(header))
    # get the primer info
    if not sort:
        cur.execute('''SELECT * FROM primers''')
    else:
        query = "SELECT * FROM primers ORDER BY {0}".format(sort)
        cur.execute(query)
    rows = cur.fetchall()
    for row in rows:
        o.write('{0}\n'.format(','.join([str(i) for i in row])))
    o.close()

def store_primers(cur, p3, section, tag):
    for k in p3.tagged_primers:
        if p3.tagged_primers[k]:
            p3.tagged_primers[k]['SECTION'] = section
            p3.tagged_primers[k]['CYCLES'] = get_tag_flows(tag)
            p3.tagged_primers[k]['TAG'] = tag
            p3.tagged_primers[k]['UNMODIFIED'] = 0
            p3.tagged_primers[k]['PAIR_HAIRPIN_EITHER'] = 0
            # sometimes there won't be any problems
            for p in ['PRIMER_LEFT_PROBLEMS', 'PRIMER_RIGHT_PROBLEMS']:
                if p not in p3.tagged_primers[k].keys():
                    p3.tagged_primers[k][p] = None
                elif 'Hairpin stability too high;' in p3.tagged_primers[k][p]:
                    p3.tagged_primers[k]['PAIR_HAIRPIN_EITHER'] = 1
            #pdb.set_trace()
            insert_primers(cur, p3.tagged_primers[k])

def design_and_store_primers(options, cur, section, tags, p3, settings):
    """iterate through tags, designing primers by removing common
    bases, integrating tags, and adding pigtails"""
    for tag in tags:
        #pdb.set_trace()
        # use private method from p3wrapr to get common bases btw. tag and
        # pigtail - we're doing this because we want to add the pigtails to
        # the tags and then just treat that whole unit as the tag, instead of
        # adding the tag, then adding the pigtail.
        if not options.fusion:
            if options.common:
                p3.tagged_pt_common, p3.tagged_pt_tag = p3._common(options.pigtail_seq, tag)
            elif options.pigtail:
                p3.tagged_pt_common, p3.tagged_pt_tag = options.pigtail_seq, options.pigtail_seq
            else:
                p3.tagged_pt_common, p3.tagged_pt_tag = '',''
            stag = p3.tagged_pt_tag + tag
            p3.dtag(settings, options.common, seqtag = stag)
            store_primers(cur, p3, section, tag)
        if options.fusion:
            if options.fusion_pairs:
                tag_pairs = [(tag, i) for i in tags[numpy.where(tags==tag)[0][0]:]]
                tag_pairs = [(tag, tag)] + tag_pairs
            else:
                tag_pairs = [(tag, tag)]
            for pair in tag_pairs:
                print pair
                p3.ftag(settings, seqtag_pair = pair)
                store_primers(cur, p3, section, tag)
    
def main():
    options, args = interface()
    conf = ConfigParser.ConfigParser()
    conf.read(options.input)
    # create a temporary table in memory for the results
    if options.keepdb:
        dir, name = os.path.split(options.output)
        name = name.split('.')[0] + '.sqlite'
        db_path = os.path.join(dir, name)
        conn = sqlite3.connect(db_path)
    else:
        conn = sqlite3.connect(':memory:')
    cur = conn.cursor()
    create_database(cur)
    settings = get_primer3_settings()
    # make sure we send it the correct version of primer3
    p3 = primer.Primers(binary='primer3_long')
    # trick the module to think we've actually designed primers
    p3.primers_designed = True
    p3.primers = {0:
        {'PRIMER_LEFT_SEQUENCE':options.left, 'PRIMER_RIGHT_SEQUENCE':options.right}, 
        'metadata':None
        }
    # check normal primers
    p3.check(settings)
    for k in p3.checked_primers:
        if p3.checked_primers[k]:
            p3.checked_primers[k]['SECTION'] = 'None'
            p3.checked_primers[k]['CYCLES'] = 0
            p3.checked_primers[k]['TAG'] = None
            p3.checked_primers[k]['UNMODIFIED'] = 1
            p3.checked_primers[k]['PAIR_HAIRPIN_EITHER'] = 0
            # add some information that will be missing from these
            p3.checked_primers[k]['PRIMER_LEFT_TAG'] = None
            p3.checked_primers[k]['PRIMER_RIGHT_TAG'] = None
            p3.checked_primers[k]['PRIMER_LEFT_TAG_COMMON_BASES'] = None
            p3.checked_primers[k]['PRIMER_RIGHT_TAG_COMMON_BASES'] = None
            for p in ['PRIMER_LEFT_PROBLEMS', 'PRIMER_RIGHT_PROBLEMS']:
                if p not in p3.checked_primers[k].keys():
                    p3.checked_primers[k][p] = None
                elif 'Hairpin stability too high;' in p3.checked_primers[k][p]:
                    p3.checked_primers[k]['PAIR_HAIRPIN_EITHER'] = 1
            #pdb.set_trace()
            insert_primers(cur, p3.checked_primers[k])
    #f = open(options.input, 'rU')
    # [[name, tag]]
    #tags = [line.strip().split(',') for line in f]
    if not options.section:
        for section in conf.sections():
            tags = get_tag_array(conf.items(section))
            design_and_store_primers(options, cur, section, tags, p3, settings)
    elif options.section:
        tags = get_tag_array(conf.items(options.section))
        design_and_store_primers(options, cur, options.section, tags, p3, settings)
    conn.commit()
    # close the tag input file - it's not needed anymore
    #f.close()
    if options.output:
        write_results(cur, options.output, options.sort_keys)

if __name__ == '__main__':
    main()
