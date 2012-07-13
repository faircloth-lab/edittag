import numpy
import string


def get_tag_array(tags):
    """return an array of sequence tags from the input file"""
    return numpy.array([t[1].split('#')[0] for t in tags])


def get_name_array(tags):
    """return an array of sequence tags from the input file"""
    return numpy.array([t[0] for t in tags])


def get_tag_dict(tags):
    """return a dictionary of sequence tag with names from the input file"""
    d = {}
    for t in tags:
        d[t[0]] = t[1].split('#')[0]
    return d


def get_tag_flows(tag):
    """return the number of regent flows to sequence a given tag"""
    flows = []
    for base in tag:
        for count, flow in enumerate(['T', 'A', 'C', 'G']):
            if base == flow:
                flows.append(count + 1)
                break
    return sum(flows)


def get_rev_comp(seq):
    """return the reverse complement of seq"""
    bases = string.maketrans('AGCTNagctn', 'TCGANtcgan')
    # translate it, reverse, return
    return seq.translate(bases)[::-1]
