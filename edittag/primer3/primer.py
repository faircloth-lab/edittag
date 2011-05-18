#!/usr/bin/env python
# encoding: utf-8
"""
primer.py

Created by Brant Faircloth on 2009-10-31.
Copyright (c) 2009 Brant Faircloth. All rights reserved.


The following (unittests) assume that primer3_core and primer3_config are 
somewhere on the system path.  I've used /usr/local/bin for both.
"""

import sys
import os
import pdb
import copy
import errno
import shutil
import string
import tempfile
import unittest
import subprocess
try:
    from PyQt4 import QtCore, QtGui
except:
    pass


class Settings:
    def __init__(self, binary = 'primer3_core'):
        '''set default primer3 params'''
        #pdb.set_trace()
        self.td = None
        self.params = {}
        self.binary = binary
        # create temporary directory
        if not self.td or not os.path.isdir(self.td):
            self.td = tempfile.mkdtemp(prefix='py-primer3-', suffix='')
    
    def __del__(self):
        #pdb.set_trace()
        shutil.rmtree(self.td)
    
    def _is_exe(self, fpath):
        '''called by _which, below.  taken from: 
        http://stackoverflow.com/questions/377017/test-if-executable-exists-in-python'''
        return os.path.exists(fpath) and os.access(fpath, os.X_OK)
    
    def _which(self, program):
        '''equivalent to Unix `which`.  taken from: 
        http://stackoverflow.com/questions/377017/test-if-executable-exists-in-python'''
        fpath, fname = os.path.split(program)
        if fpath:
            if self._is_exe(program):
                return program
        else:
            for path in os.environ["PATH"].split(os.pathsep):
                exe_file = os.path.join(path, program)
                if self._is_exe(exe_file):
                    return exe_file

    def _mispriming(self):
        self.params['PRIMER_MISPRIMING_LIBRARY']        = 'misprime_lib_weight'
        self.params['PRIMER_MAX_LIBRARY_MISPRIMING']    = 7.00
    
    def _basic(self, path):
        # basic parameters for primer checking
        self.params['PRIMER_TM_FORMULA']                = 1     # boolean
        self.params['PRIMER_SALT_CORRECTIONS']          = 1     # boolean
        self.params['PRIMER_SALT_MONOVALENT']           = 50.0  # mM
        self.params['PRIMER_SALT_DIVALENT']             = 1.5   # mM
        
        self.params['PRIMER_DNTP_CONC']                 = 0.125 # mM
        self.params['PRIMER_THERMODYNAMIC_ALIGNMENT']   = 1
        if not path:
            self.params['PRIMER_THERMODYNAMIC_PARAMETERS_PATH']    = os.path.join(os.path.dirname(self._which(self.binary)), 'primer3_config/')
        else:
            self.params['PRIMER_THERMODYNAMIC_PARAMETERS_PATH']    = path
        self.params['PRIMER_MAX_POLY_X']                = 3     # nt
        self.params['PRIMER_EXPLAIN_FLAG']              = 1     # boolean
    
    def basic(self, path=False, mispriming=False, **kwargs):
        self._basic(path)
        self.params['PRIMER_PRODUCT_SIZE_RANGE']        = '150-450'
        self.params['PRIMER_MIN_TM']                    = 57.   # deg C
        self.params['PRIMER_MAX_TM']                    = 62.   # deg C
        self.params['PRIMER_OPT_TM']                    = 60.   # deg C
        self.params['PRIMER_PAIR_MAX_DIFF_TM']          = 5.    # deg C
        self.params['PRIMER_OPT_SIZE']                  = 19    # nt
        self.params['PRIMER_MIN_SIZE']                  = 16    # nt
        self.params['PRIMER_MIN_GC']                    = 30.0  # percent
        self.params['PRIMER_OPT_GC_PERCENT']            = 50.0  # percent
        self.params['PRIMER_MAX_GC']                    = 70.0  # percent
        self.params['PRIMER_GC_CLAMP']                  = 1     # boolean
        self.params['PRIMER_MAX_SELF_ANY_TH']           = 45.   # deg C
        self.params['PRIMER_PAIR_MAX_COMPL_ANY_TH']     = 45.   # deg C
        self.params['PRIMER_MAX_SELF_END_TH']           = 40.   # deg C
        self.params['PRIMER_PAIR_MAX_COMPL_END_TH']     = 40.   # deg C
        self.params['PRIMER_MAX_HAIRPIN_TH']            = 24.   # deg C
        self.params['PRIMER_PAIR_MAX_HAIRPIN_TH']       = 24.   # deg C
        self.params['PRIMER_MAX_END_STABILITY']         = 8.0   # delta G
        self.params['PRIMER_LOWERCASE_MASKING']         = 1     # avoids 3' mask
        self.params['PRIMER_NUM_RETURN']                = 4     # count
        if mispriming:
            self.mispriming()
        for k,v in kwargs.iteritems():
            self.params[k]                              = v
    
    def reduced(self, path=False, mispriming=False, **kwargs):
        self._basic(path)
        if mispriming:
            self.mispriming()
        for k,v in kwargs.iteritems():
            self.params[k]                              = v
    
    def manual(self, **kwargs):
        for k,v in kwargs.iteritems():
            self.params[k]                              = v
    
    def remove(self, item):
        '''removes and item from default parameters'''
        self.params.popitem(item)
    
    def clear(self):
        '''clears all default parameters'''
        self.params.clear()
        
    def parameter(self, key, value):
        '''reset or substitute default primer3 parameters'''
        self.params[key] = value
            
class Primers:                            
    def __init__(self, binary='primer3_core'):
        self.tagged_good    = None
        self.binary         = binary
    
    def _locals(self, obj, **kwargs):
        #if ('left_primer' and 'right_primer') not in kwargs.keys() and 'sequence' not in kwargs.keys():
        #    raise ValueError('You must provide a template sequence or primers to test')
        od = copy.deepcopy(obj.params)
        od['SEQUENCE_ID']              = kwargs['name']
        if 'sequence' in kwargs.keys():
            od['SEQUENCE_TEMPLATE']    = kwargs['sequence']
            od['SEQUENCE_TARGET']      = kwargs['target']
            if 'quality' in kwargs.keys():
                od['SEQUENCE_QUALITY'] = kwargs['quality']
            if 'excluded' in kwargs.keys():
                od['SEQUENCE_EXCLUDED_REGION'] = kwargs['excluded']
        elif 'left_primer' in kwargs.keys() and 'right_primer' in kwargs.keys():
            od['PRIMER_TASK'] = 'check_primers'
            od['SEQUENCE_PRIMER'] = kwargs['left_primer']
            od['SEQUENCE_PRIMER_REVCOMP'] = kwargs['right_primer']
        elif 'left_primer' in kwargs.keys():
            od['PRIMER_TASK'] = 'check_primers'
            od['SEQUENCE_PRIMER'] = kwargs['left_primer']
        elif 'right_primer' in kwargs.keys():
            od['PRIMER_TASK'] = 'check_primers'
            od['SEQUENCE_PRIMER_REVCOMP'] = kwargs['right_primer']
        self._create_temp_file(od, obj.td) 
    
    def _create_temp_file(self, od, td):
        '''create the temporary input file for use by the primer3 binary'''
        fd, self.tf = tempfile.mkstemp(prefix='primer-%s-' % \
        od['SEQUENCE_ID'], suffix='.tmp', dir=td)
        os.close(fd)
        tfh = open(self.tf, 'w')
        for k,v in od.iteritems():
            tfh.write('%s=%s\n' % (k, v))
        tfh.write('=')
        tfh.close()
        #pdb.set_trace()
    
    def _rm_temp_file(self):
        '''remove the temporary files area following primer design'''
        os.remove(self.tf)
        #os.rmdir(self.td)
    
    def _common(self, tag, primer):
        '''checks primer and tag for common bases and removes them'''
        common, index = False, None
        for i in range(1,len(primer)):
            frag = primer[0:i]
            if tag.endswith(frag):
                index = i
        if index:
            tag = tag[:-index]
            common = True
        else:
            tag = tag
        # not sure why this is needed
        return common, tag
        
    
    def _complement(self, seq):
        '''Return complement of seq'''
        bases = string.maketrans('AGCTagct','TCGAtcga')
        # translate it, reverse, return
        return seq.translate(bases)
    
    def _revcomp(self, seq):
        '''Return reverse complement of seq'''
        bases = string.maketrans('AGCTagct','TCGAtcga')
        # translate it, reverse, return
        return seq.translate(bases)[::-1]
    
    def _p_design(self, delete = True):
        '''call primer3 and feed it our temporary design file'''
        #QtCore.pyqtRemoveInputHook()
        #pdb.set_trace()
        try:
            stdout,stderr = subprocess.Popen('%s -strict_tags %s' % (self.binary, self.tf),\
            shell=True, stdout=subprocess.PIPE, stdin=None, \
            stderr=subprocess.PIPE, universal_newlines=True).communicate()
        except OSError, e:
            if e.errno == errno.EINTR:
                self._p_design
            else:
                raise
        except AttributeError:
            self._p_design
        except:
            print "Unexpected error:", sys.exc_info()[0]
            raise
        #pdb.set_trace()
        if stdout:
            primers = {}
            stdout = stdout.split('\n')
            for l in stdout:
                try:
                    name, val = l.split('=')
                    try:
                        val = float(val)
                    except ValueError:
                        pass
                    if name in ['PRIMER_LEFT_EXPLAIN', 
                    'PRIMER_RIGHT_EXPLAIN', 'PRIMER_PAIR_EXPLAIN']:
                        if 'metadata' not in primers.keys():
                            primers['metadata'] = {name:val}
                        else:
                            primers['metadata'][name] = val
                    else:
                        k = int(name.split('_')[2])
                        name = name.replace(('_%s') % k, '')
                        if k not in primers.keys():
                            primers[k] = {name:val}
                        else:
                            primers[k][name] = val
                except:
                    pass
        else:
            primers = None
        #pdb.set_trace()
        # delete the temporary directory and files
        if delete:
            self._rm_temp_file()
        return primers

    
    def _good(self):
        '''select those primers meeting the minimum criteria for usefulness'''
        #QtCore.pyqtRemoveInputHook()
        #pdb.set_trace()
        self.tagged_good = {}
        min_qual = {
            'PRIMER_PAIR_COMPL_ANY_TH':45.,
            'PRIMER_PAIR_COMPL_END_TH':45.,
            'PRIMER_RIGHT_HAIRPIN_TH':24.,
            'PRIMER_LEFT_HAIRPIN_TH':24.,
            'PRIMER_LEFT_SELF_ANY_TH':45.,
            'PRIMER_RIGHT_SELF_ANY_TH':45.,
            'PRIMER_LEFT_SELF_END_TH':40., 
            'PRIMER_RIGHT_SELF_END_TH':40.
            }
        for k,v in self.tagged_primers.iteritems():
            okay = False
            for m,q in min_qual.iteritems():
                if v[m] <= q:
                    okay = True
                else:
                    okay = False
                    break
            if okay:
                self.tagged_good[k] = v
                # add null values for pigtails
                self.tagged_good[k]['PRIMER_PIGTAILED']                = None
                self.tagged_good[k]['PRIMER_PIGTAIL_TAG_COMMON_BASES'] = None
                self.tagged_good[k]['PRIMER_PIGTAIL_TAG']              = None
    
    def _best(self):
        '''select the best tagged primer from the group, and screen it to 
        ensure that it is still within normal spec for complementarity'''
        #QtCore.pyqtRemoveInputHook()
        #pdb.set_trace()
        self.tagged_best    = None
        self.tagged_best_id = None
        low_penalty = None
        if self.tagged_good:
            for k,v in self.tagged_good.iteritems():
                if not low_penalty:
                    low_penalty = (k,v['PRIMER_PAIR_PENALTY'])
                elif v['PRIMER_PAIR_PENALTY'] < low_penalty[1]:
                    low_penalty = (k,v['PRIMER_PAIR_PENALTY'])
            self.tagged_best = {low_penalty[0]:self.tagged_primers[low_penalty[0]]}
            self.tagged_best_id = low_penalty[0]
        #pdb.set_trace()
    
    def _bestprobe(self):
        '''select the best tagged probe from the group, and screen it to 
        ensure that it is still within normal spec for complementarity'''
        low_penalty = {}
        # TODO:  modify this to consider only complementarity measures?
        for k,v in self.tagged_primers.iteritems():
            s = k.split('_')[2]
            if s == 'f':
                keyname = 'PRIMER_LEFT_HAIRPIN_TH'
            else:
                keyname = 'PRIMER_RIGHT_HAIRPIN_TH'
            if s not in low_penalty.keys():
                low_penalty[s] = (k,v[keyname])
            elif v[keyname] < low_penalty[s][1]:
                low_penalty[s] = (k,v[keyname])
        #pdb.set_trace()
        self.tagged_best = {}
        self.tagged_best['f'] = self.tagged_primers[low_penalty['f'][0]]
        self.tagged_best['r'] = self.tagged_primers[low_penalty['r'][0]]
        self.tagged_best_id = {}
        self.tagged_best_id['f'] = low_penalty['f'][0].split('_')[0]
        self.tagged_best_id['r'] = low_penalty['r'][0].split('_')[0]
        min_qual = {'f':{'PRIMER_LEFT_HAIRPIN_TH':45.,
        'PRIMER_LEFT_SELF_ANY_TH':45.,
        'PRIMER_LEFT_SELF_END_TH':40.}, 
        'r':{'PRIMER_RIGHT_HAIRPIN_TH':45.,
        'PRIMER_RIGHT_SELF_ANY_TH':45., 
        'PRIMER_RIGHT_SELF_END_TH':40.}}
        self.tagged_best_okay = {}
        #pdb.set_trace()
        for k,v in min_qual.iteritems():
            for j,c in v.iteritems():
                if self.tagged_best[k][j] <= c:
                    self.tagged_best_okay[k] = True
                else:
                    self.tagged_best_okay[k] = False
                    break
        #pdb.set_trace() 
    
    def pick(self, design, **kwargs):
        '''pick primers given settings'''
        self.design = design
        self._locals(self.design, **kwargs)
        self.primers = self._p_design()
        if self.primers and 0 in self.primers.keys():
            self.primers_designed = True
        else:
            self.primers_designed = False      
    
    def tag(self, tagging, delete=True, **kwargs):
        '''tag and check newly designed primers'''
        if self.primers_designed:
            self.tagging = tagging
            self.tagged_primers = {}
            #pdb.set_trace()
            primers = self.primers.keys()
            primers.remove('metadata')
            for p in primers:
                for ts in kwargs:
                    if kwargs[ts]:
                        for s in xrange(2):
                            if s == 0:
                                self.tagged_common, self.tagged_tag = self._common(kwargs[ts], self.primers[p]['PRIMER_LEFT_SEQUENCE'])
                                l_tagged = self.tagged_tag + self.primers[p]['PRIMER_LEFT_SEQUENCE']
                                r_untagged = self.primers[p]['PRIMER_RIGHT_SEQUENCE']
                                # reinitialize with reduced set of Primer3Params
                                self._locals(self.tagging, left_primer=l_tagged, right_primer=r_untagged, name='tagging')
                                k = '%s_%s_%s' % (p, ts, 'f')
                                self.tagged_primers[k] = self._p_design()[0]
                                self.tagged_primers[k]['PRIMER_TAGGED'] = 'LEFT'
                                self.tagged_primers[k]['PRIMER_TAG_COMMON_BASES'] = self.tagged_common
                                self.tagged_primers[k]['PRIMER_TAG'] = self.tagged_tag
                                # cleanup is automatic in _p_design
                                
                            else:
                                l_untagged = self.primers[p]['PRIMER_LEFT_SEQUENCE']
                                self.tagged_common, self.tagged_tag = self._common(kwargs[ts], self.primers[p]['PRIMER_RIGHT_SEQUENCE'])
                                r_tagged = self.tagged_tag + self.primers[p]['PRIMER_RIGHT_SEQUENCE']
                                # reinitialize with reduced set of Primer3Params
                                self._locals(self.tagging, left_primer=l_untagged, right_primer=r_tagged, name='tagging')
                                k = '%s_%s_%s' % (p, ts, 'r')
                                #pdb.set_trace()
                                self.tagged_primers[k] = self._p_design()[0]
                                self.tagged_primers[k]['PRIMER_TAGGED'] = 'RIGHT'
                                self.tagged_primers[k]['PRIMER_TAG_COMMON_BASES'] = self.tagged_common
                                self.tagged_primers[k]['PRIMER_TAG'] = self.tagged_tag
                            self.tagged_primers[k]['PRIMER_TAG_PRODUCT_SIZE'] = self.primers[p]['PRIMER_PAIR_PRODUCT_SIZE'] + len(self.tagged_tag)
            self._good()
            self._best()
            #QtCore.pyqtRemoveInputHook()
            #pdb.set_trace()
        else:
            self.tagged_primers = None
            self.tagged_best = None
    
    def dtag(self, tagging, remove_common = True, delete=True, **kwargs):
        '''tag and check newly designed primers'''
        if self.primers_designed:
            self.tagging = tagging
            self.tagged_primers = {}
            #pdb.set_trace()
            primers = self.primers.keys()
            primers.remove('metadata')
            for p in primers:
                for ts in kwargs:
                    if kwargs[ts]:
                        if remove_common:
                            self.tagged_l_common, self.tagged_l_tag = self._common(kwargs[ts], self.primers[p]['PRIMER_LEFT_SEQUENCE'])
                            self.tagged_r_common, self.tagged_r_tag = self._common(kwargs[ts], self.primers[p]['PRIMER_RIGHT_SEQUENCE'])
                        else:
                            self.tagged_l_common, self.tagged_l_tag = kwargs[ts], kwargs[ts]
                            self.tagged_r_common, self.tagged_r_tag = kwargs[ts], kwargs[ts]
                        l_tagged = self.tagged_l_tag + self.primers[p]['PRIMER_LEFT_SEQUENCE']
                        r_tagged = self.tagged_r_tag + self.primers[p]['PRIMER_RIGHT_SEQUENCE']
                        # reinitialize with reduced set of Primer3Params
                        self._locals(self.tagging, left_primer=l_tagged, right_primer=r_tagged, name='tagging')
                        k = '%s_%s_%s' % (p, ts, 'f')
                        self.tagged_primers[k] = self._p_design()[0]
                        self.tagged_primers[k]['PRIMER_TAGGED'] = 'BOTH'
                        self.tagged_primers[k]['PRIMER_LEFT_TAG_COMMON_BASES'] = self.tagged_l_common
                        self.tagged_primers[k]['PRIMER_RIGHT_TAG_COMMON_BASES'] = self.tagged_r_common
                        self.tagged_primers[k]['PRIMER_LEFT_TAG'] = self.tagged_l_tag
                        self.tagged_primers[k]['PRIMER_RIGHT_TAG'] = self.tagged_r_tag
            #if len(self.tagged_primers) > 1:
            self._good()
            self._best()
            #else:
                
            #QtCore.pyqtRemoveInputHook()
            #pdb.set_trace()
        else:
            self.tagged_primers = None
            self.tagged_best = None

    def ftag(self, tagging, delete=True, f_left = 'CGTATCGCCTCCCTCGCGCCATCAG', f_right = 'CTATGCGCCTTGCCAGCCCGCTCAG', **kwargs):
        '''tag and check newly designed primers'''
        if self.primers_designed:
            self.tagging = tagging
            self.tagged_primers = {}
            #pdb.set_trace()
            primers = self.primers.keys()
            primers.remove('metadata')
            for p in primers:
                for ts in kwargs:
                    if kwargs[ts]:
                        self.tagged_l_common = False
                        self.tagged_l_tag = kwargs[ts][0]
                        l_tagged = f_left + self.tagged_l_tag + self.primers[p]['PRIMER_LEFT_SEQUENCE']
                        self.tagged_r_common = False
                        self.tagged_r_tag = kwargs[ts][0]
                        r_tagged = f_right + self.tagged_r_tag + self.primers[p]['PRIMER_RIGHT_SEQUENCE']
                        # reinitialize with reduced set of Primer3Params
                        self._locals(self.tagging, left_primer=l_tagged, right_primer=r_tagged, name='tagging')
                        k = '%s_%s_%s' % (p, ts, 'f')
                        self.tagged_primers[k] = self._p_design()[0]
                        self.tagged_primers[k]['PRIMER_TAGGED'] = 'BOTH'
                        self.tagged_primers[k]['PRIMER_LEFT_TAG_COMMON_BASES'] = self.tagged_l_common
                        self.tagged_primers[k]['PRIMER_RIGHT_TAG_COMMON_BASES'] = self.tagged_r_common
                        self.tagged_primers[k]['PRIMER_LEFT_TAG'] = self.tagged_l_tag
                        self.tagged_primers[k]['PRIMER_RIGHT_TAG'] = self.tagged_r_tag
            #if len(self.tagged_primers) > 1:
            self._good()
            self._best()
            #else:

            #QtCore.pyqtRemoveInputHook()
            #pdb.set_trace()
        else:
            self.tagged_primers = None
            self.tagged_best = None
    
    def check(self, tagging, delete=True, **kwargs):
        '''check primers designed elsewhere'''
        if self.primers_designed:
            self.tagging = tagging
            self.checked_primers = {}
            #pdb.set_trace()
            primers = self.primers.keys()
            primers.remove('metadata')
            for p in primers:
                # reinitialize with reduced set of Primer3Params
                self._locals(self.tagging, left_primer=self.primers[p]['PRIMER_LEFT_SEQUENCE'], right_primer=self.primers[p]['PRIMER_RIGHT_SEQUENCE'], name='checking')
                self.checked_primers[p] = self._p_design()[0]
                self.checked_primers[p]['PRIMER_TAGGED'] = 'NONE'
            #if len(self.tagged_primers) > 1:
            # self._good()
            # self._best()
            #else:

            #QtCore.pyqtRemoveInputHook()
            #pdb.set_trace()
        else:
            self.tagged_primers = None
            self.tagged_best = None

    def pigtail(self, tagging, pigtail = 'GTTT'):
        '''Add pigtail to untagged primer of tagged pair'''
        if self.tagged_good:
            right = False
            for k,v in self.tagged_good.iteritems():
                if v['PRIMER_TAGGED'] == 'LEFT':
                    self.tagged_good[k]['PRIMER_PIGTAILED'] = 'RIGHT'
                    self.tagged_good[k]['PRIMER_PIGTAIL_TAG_COMMON_BASES'], \
                        self.tagged_good[k]['PRIMER_PIGTAIL_TAG'] = \
                        self._common(pigtail, v['PRIMER_RIGHT_SEQUENCE'])
                    self.tagged_good[k]['PRIMER_RIGHT_SEQUENCE'] = self.tagged_good[k]['PRIMER_PIGTAIL_TAG'] + v['PRIMER_RIGHT_SEQUENCE']
                    #QtCore.pyqtRemoveInputHook()
                    #pdb.set_trace()
                else:
                    #QtCore.pyqtRemoveInputHook()
                    #pdb.set_trace()
                    self.tagged_good[k]['PRIMER_PIGTAILED'] = 'LEFT'
                    self.tagged_good[k]['PRIMER_PIGTAIL_TAG_COMMON_BASES'], \
                        self.tagged_good[k]['PRIMER_PIGTAIL_TAG'] = \
                        self._common(pigtail, v['PRIMER_LEFT_SEQUENCE'])
                    self.tagged_good[k]['PRIMER_LEFT_SEQUENCE'] = self.tagged_good[k]['PRIMER_PIGTAIL_TAG'] + v['PRIMER_LEFT_SEQUENCE']
                # update the size of the tagged primer + pigtail
                self.tagged_good[k]['PRIMER_TAG_PRODUCT_SIZE'] += len(self.tagged_good[k]['PRIMER_PIGTAIL_TAG'])
        elif self.primers_designed:
            #from PyQt4 import QtCore
            #QtCore.pyqtRemoveInputHook()
            #pdb.set_trace()
            self.tag(tagging, PIGTAIL=pigtail)
            self._good()
            self._best()
    
    
    def probe(self, tagging, delete=True, **kwargs):
        '''tag and check newly designed primers'''
        if self.primers_designed:
            self.tagging = tagging
            self.tagged_primers = {}
            #pdb.set_trace()
            primers = self.primers.keys()
            primers.remove('metadata')
            for p in primers:
                for ts in kwargs:
                    if kwargs[ts]:
                        for s in xrange(2):
                            if s == 0:
                                #pdb.set_trace()
                                c_t, c_p = self._complement(kwargs[ts]), self._complement(self.primers[p]['PRIMER_LEFT_SEQUENCE'])
                                self.tagged_common, self.tagged_tag = self._common(c_t, c_p)
                                l_tagged = self.tagged_tag + c_p
                                # reverse
                                l_tagged = l_tagged[::-1]
                                # reinitialize with reduced set of Primer3Params
                                #pdb.set_trace()                            
                                self._locals(self.tagging, left_primer=l_tagged, name='probe')
                                k = '%s_%s_%s' % (p, ts, 'f')
                                self.tagged_primers[k] = self._p_design()[0]
                                # cleanup is automatic in _p_design
                            else:
                                c_t, c_p = self._complement(kwargs[ts]), self._complement(self.primers[p]['PRIMER_RIGHT_SEQUENCE'])
                                self.tagged_common, self.tagged_tag = self._common(c_t, c_p)
                                r_tagged = self.tagged_tag + c_p
                                # reverse
                                r_tagged = r_tagged[::-1]
                                # reinitialize with reduced set of Primer3Params
                                self._locals(self.tagging, right_primer=r_tagged, name='probe')
                                k = '%s_%s_%s' % (p, ts, 'r')
                                #pdb.set_trace()
                                self.tagged_primers[k] = self._p_design()[0]
                                # cleanup is automatic in _p_design   
            self._bestprobe()
            #pdb.set_trace()            
        else:
            self.tagged_primers = None
            self.tagged_best = None
    

class Primer3Tests(unittest.TestCase):
    def setUp(self):
        self.seq = "TAAAATGATTAACTGCTGCATACAGCTATGACTTTATTTGTAAGGAGCAG\
TTAGGAGAGGCAAAATGAGTATGCAGCTTTCCATTATATACAGGCATATTTTCAATAGCCGTGTGAGTCTT\
TTTATGGCTCCATTTATGTCAATGTCCTAGTGTCATCTGTAATAAACTGGCAGCAATTAGAGCCACAATAA\
ACCCCATAATGCAACACAAACAACAGGAAGTCTCCCAGTACCCCAACGCTCTAAATTTACATCTCCCCTTC\
GAAAGTCTATTTATCACCAGAGTTTGCAAGCCCGTCTGCTAAAGAGCGCTCTAATTAAGATGTATCTGGTG\
AACAAGTGTCTGCTTTTCACCCTACTCTTTTAACATATCATGTATGCACTGAGCAATCTTCGTCGGGTCTC\
ATAATGAGAAAACTGTGATATGCAAAAACTCTGTGAAATCTTTTATCCTCCCAGGAGACCTCCCTTGATGC\
CAGGCATTCATCATCTAGCCTCTAATATCAGTTATTTTGTGCCTCCTCTGCTTACA"
        self.static_results = {'PRIMER_LEFT_SELF_END_TH': '0.00', 'PRIMER_PAIR_COMPL_ANY_TH': '0.00', 'PRIMER_RIGHT_PENALTY': '0.307605', 'PRIMER_RIGHT_GC_PERCENT': '52.632', 'PRIMER_LEFT_HAIRPIN_TH': '0.00', 'PRIMER_LEFT': '41,19', 'PRIMER_PAIR_COMPL_END_TH': '0.00', 'PRIMER_LEFT_PENALTY': '0.663820', 'PRIMER_PAIR_PRODUCT_SIZE': '190', 'PRIMER_LEFT_END_STABILITY': '7.9000', 'PRIMER_LEFT_TM': '59.336', 'PRIMER_PAIR_PENALTY': '0.971425', 'PRIMER_RIGHT_HAIRPIN_TH': '40.16', 'PRIMER_RIGHT_SELF_ANY_TH': '0.00', 'PRIMER_LEFT_GC_PERCENT': '52.632', 'PRIMER_LEFT_SELF_ANY_TH': '0.00', 'PRIMER_RIGHT_END_STABILITY': '7.0000', 'PRIMER_RIGHT_SEQUENCE': 'ACTGGGAGACTTCCTGTTG', 'PRIMER_RIGHT_SELF_END_TH': '0.00', 'PRIMER_LEFT_SEQUENCE': 'AAGGAGCAGTTAGGAGAGG', 'PRIMER_RIGHT': '230,19', 'PRIMER_RIGHT_TM': '59.692'}
        self.basic_settings = {'PRIMER_MAX_SELF_ANY_TH': 45.0, 'PRIMER_MAX_SELF_END_TH': 40.0, 'PRIMER_MIN_GC': 30.0, 'PRIMER_OPT_SIZE': 19, 'PRIMER_MIN_TM': 57.0, 'PRIMER_MIN_SIZE': 16, 'PRIMER_MAX_END_STABILITY': 8.0, 'PRIMER_OPT_GC_PERCENT': 50.0, 'PRIMER_PAIR_MAX_COMPL_END_TH': 40.0, 'PRIMER_SALT_CONC': 50.0, 'PRIMER_NUM_RETURN': 4, 'PRIMER_PRODUCT_SIZE_RANGE': '150-450', 'PRIMER_MAX_TM': 62.0, 'PRIMER_DNTP_CONC': 0.125, 'PRIMER_THERMODYNAMIC_ALIGNMENT': 1, 'PRIMER_MAX_HAIRPIN': 24.0, 'PRIMER_MAX_POLY_X': 3, 'PRIMER_PAIR_MAX_COMPL_ANY_TH': 45.0, 'PRIMER_MAX_GC': 70.0, 'PRIMER_TM_SANTALUCIA': 1, 'PRIMER_SALT_CORRECTIONS': 1, 'PRIMER_THERMODYNAMIC_PARAMETERS_PATH': '/usr/local/bin/primer3_config/', 'PRIMER_OPT_TM': 60.0, 'PRIMER_MAX_DIFF_TM': 5.0, 'PRIMER_GC_CLAMP': 1, 'PRIMER_DIVALENT_CONC': 1.5, 'PRIMER_PAIR_MAX_HAIRPIN': 24.0, 'PRIMER_EXPLAIN_FLAG': 1, 'PRIMER_LOWERCASE_MASKING': 1}
        self.reduced_settings = {'PRIMER_THERMODYNAMIC_ALIGNMENT': 1, 'PRIMER_MAX_POLY_X': 3, 'PRIMER_TM_SANTALUCIA': 1, 'PRIMER_SALT_CORRECTIONS': 1, 'PRIMER_DIVALENT_CONC': 1.5, 'PRIMER_SALT_CONC': 50.0, 'PRIMER_THERMODYNAMIC_PARAMETERS_PATH': '/usr/local/bin/primer3_config/', 'PRIMER_EXPLAIN_FLAG': 1, 'PRIMER_DNTP_CONC': 0.125}
    
    def testReducedParams(self):
        '''Ensure that we retrieve the reduced set of design parameters'''
        #pdb.set_trace()
        self.settings = Settings()
        self.settings.reduced()
        self.assertEqual(self.settings.params, self.reduced_settings)

    def testFullParams(self):
        '''Ensure that we retrieve the full set of design parameters'''
        #pdb.set_trace()
        self.settings = Settings()
        self.settings.basic()
        self.assertEqual(self.settings.params, self.basic_settings)
        
    def testPrimerDesign(self):
        '''Ensure that we are designing primers with the same resulting
        parameters as previous attempts'''
        #pdb.set_trace()
        self.settings = Settings()
        self.settings.basic()
        self.primer3 = Primers()
        self.primer3.pick(self.settings, sequence=self.seq, target='100,100', name = 'primer_design')
        self.assertEqual(self.primer3.primers[0], self.static_results)
        
    def testTagging(self):
        '''Test tagging functionality'''
        #pdb.set_trace()
        self.settings = Settings()
        self.settings.basic()
        self.primers = Primers()
        self.primers.pick(self.settings, sequence=self.seq, target='100,100', name = 'primer_design')
        self.tag_settings = Settings()
        self.tag_settings.reduced(PRIMER_PICK_ANYWAY=1)
        self.primers.tag(self.tag_settings, cag='CAGTGCGAAGG')
        self.assertEqual(self.primers.tagged_best['PRIMER_PAIR_PENALTY'], str(19.607853))
        pdb.set_trace()
        self.assert_(self.primers.tagged_best['PRIMER_LEFT_SEQUENCE'].startswith('CAGTGCGAAGG'))
        self.assert_(self.primers.tagged_best['PRIMER_PAIR_COMPL_ANY_TH'], str(45.))
        self.assert_(self.primers.tagged_best['PRIMER_PAIR_COMPL_END_TH'], str(45.))
        self.assert_(self.primers.tagged_best['PRIMER_LEFT_SELF_ANY_TH'], str(45.))
        self.assert_(self.primers.tagged_best['PRIMER_RIGHT_SELF_ANY_TH'], str(45.))
        self.assert_(self.primers.tagged_best['PRIMER_LEFT_SELF_END_TH'], str(40.))
        self.assert_(self.primers.tagged_best['PRIMER_RIGHT_SELF_END_TH'], str(40.))
        self.assert_(self.primers.tagged_best['PRIMER_RIGHT_HAIRPIN_TH'], str(24.))
        self.assert_(self.primers.tagged_best['PRIMER_LEFT_HAIRPIN_TH'], str(24.))
         

if __name__ == '__main__':
    unittest.main()