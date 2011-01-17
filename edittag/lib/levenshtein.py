#!/usr/bin/env python
# encoding: utf-8

"""
levenshtein.py

Created by Brant Faircloth on 20 November 2010 15:27 PST (-0800).
Copyright (c) 2010 Brant C. Faircloth. All rights reserved.
"""


def hamming(s1, s2):
    """Find the Hamming distance btw. 2 strings. Substitutions only.
    
    ORIGINALLY FROM http://en.wikipedia.org/wiki/Hamming_distance
    
    """
    assert len(s1) == len(s2)
    return sum([ch1 != ch2 for ch1, ch2 in zip(s1, s2)])

def distance(a,b):
    """Pure python version to compute the levenshtein distance between a and b.
    The Levenshtein distance includes insertions, deletions, substitutions; 
    unlike the Hamming distance, which is substitutions only.

    ORIGINALLY FROM:  http://hetland.org/coding/python/levenshtein.py

    """
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