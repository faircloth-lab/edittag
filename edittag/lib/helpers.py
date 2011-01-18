import numpy
import string

def get_tag_array(tags):
    """return an arrray of sequence tags from the input file"""
    return numpy.array([t[1].split('#')[0] for t in tags])
    
def get_rev_comp(seq):
   '''Return reverse complement of seq'''
   bases = string.maketrans('AGCTNagctn','TCGANtcgan')
   # translate it, reverse, return
   return seq.translate(bases)[::-1]
    