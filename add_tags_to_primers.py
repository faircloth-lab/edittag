#!/usr/bin/env python
# encoding: utf-8

"""
add_tags_to_primers.py

Created by Brant Faircloth on 04 October 2010 11:02 PDT (-0700).
Copyright (c) 2010 Brant C. Faircloth. All rights reserved.
"""

import os
import sys
import pdb
import sqlite3
import optparse
from operator import itemgetter
from p3wrapr import primer

def interface():
    '''Command-line interface'''
    usage = "usage: %prog [options]"

    p = optparse.OptionParser(usage)

    p.add_option('--tag-file', dest = 'input', action='store', 
type='string', default = None, help='The path to the output file.',
metavar='FILE')
    p.add_option('--left-primer', dest = 'left', action='store', 
type='string', default = None, help='The left primer.',)
    p.add_option('--right-primer', dest = 'right', action='store', 
type='string', default = None, help='The left primer')
    p.add_option('--output', dest = 'output', action='store', 
type='string', default = None, help='The path to the output file.',
metavar='FILE')
    p.add_option('--pigtail', dest = 'pigtail', action='store', 
type='string', default = 'GTTT', help='The left primer')

    (options,arg) = p.parse_args()
    options.input = os.path.abspath(os.path.expanduser(options.input))
    #if options.output:
    #    options.output = os.path.abspath(os.path.expanduser(options.output))
    if not options.left and options.right:
        p.print_help()
        sys.exit(2)
    if not os.path.isfile(options.input):
        print "You must provide a valid path to the configuration file."
        p.print_help()
        sys.exit(2)
    return options, arg 

def create_database(cur):
    cur.execute('''CREATE TABLE primers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
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
        pair_penalty real
        )''')

def insert_primers(cur, data):
    query = ('''INSERT INTO primers (
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
        pair_penalty
        )
    VALUES (
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
        :PRIMER_PAIR_PENALTY)''')
    cur.execute(query, data)

def main():
    options, args = interface()
    # create a temporary table in memory for the results
    conn = sqlite3.connect(':memory:')
    #conn = sqlite3.connect('test.sqlite')
    cur = conn.cursor()
    create_database(cur)
    # set the tagging parameters of a particular primer
    settings = primer.Settings()
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
    settings.params['PRIMER_MAX_HAIRPIN']               = 24.   # deg C
    settings.params['PRIMER_PAIR_MAX_HAIRPIN']          = 24.   # deg C
    settings.params['PRIMER_MAX_END_STABILITY']         = 8.5   # delta G
    p3 = primer.Primers()
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
            p3.checked_primers[k]['CYCLES'] = 0
            p3.checked_primers[k]['TAG'] = None
            p3.checked_primers[k]['UNMODIFIED'] = 1
            # add some information that will be missing from these
            p3.checked_primers[k]['PRIMER_LEFT_TAG'] = None
            p3.checked_primers[k]['PRIMER_RIGHT_TAG'] = None
            p3.checked_primers[k]['PRIMER_LEFT_TAG_COMMON_BASES'] = None
            p3.checked_primers[k]['PRIMER_RIGHT_TAG_COMMON_BASES'] = None
            for p in ['PRIMER_LEFT_PROBLEMS', 'PRIMER_RIGHT_PROBLEMS']:
                if p not in p3.checked_primers[k].keys():
                    p3.checked_primers[k][p] = None
            #pdb.set_trace()
            insert_primers(cur, p3.checked_primers[k])
            
    f = open(options.input, 'rU')
    tags = [line.strip().split(',') for line in f]
    # iterate through tags, ensuring we are start with lowest flow count
    for tag in sorted(tags, key=itemgetter(2)):
        #pdb.set_trace()
        # use private method from p3wrapr to get common bases btw. tag and
        # pigtail
        p3.tagged_pt_common, p3.tagged_pt_tag = p3._common(options.pigtail, tag[1])
        stag = p3.tagged_pt_tag + tag[1]
        p3.dtag(settings, seqtag=stag)
        for k in p3.tagged_primers:
            if p3.tagged_primers[k]:
                p3.tagged_primers[k]['CYCLES'] = tag[2]
                p3.tagged_primers[k]['TAG'] = tag[1]
                p3.tagged_primers[k]['UNMODIFIED'] = 0
                # sometimes there won't be any problems
                for p in ['PRIMER_LEFT_PROBLEMS', 'PRIMER_RIGHT_PROBLEMS']:
                    if p not in p3.tagged_primers[k].keys():
                        p3.checked_primers[k][p] = None
                #pdb.set_trace()
                insert_primers(cur, p3.tagged_primers[k])
    conn.commit()
    o = open(options.output, 'w')
    # get header info
    cur.execute('''PRAGMA table_info( primers )''')
    header = ','.join([i[1] for i in cur.fetchall()])
    o.write('{0}\n'.format(header))
    cur.execute('''SELECT * FROM primers''')
    rows = cur.fetchall()
    for row in rows:
        o.write('{0}\n'.format(','.join([str(i) for i in row])))
    f.close()
    o.close()

if __name__ == '__main__':
    main()