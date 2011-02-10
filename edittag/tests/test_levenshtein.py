#!/usr/bin/env python
# encoding: utf-8

"""
test_py

Created by Brant Faircloth on 17 January 2011 1300 PST (-0800).
Copyright (c) 2011 Brant C. Faircloth. All rights reserved.
"""

import unittest
from edittag.levenshtein import *

import pdb

class TestPythonLevenshteinDistance(unittest.TestCase):
    
    def test_zero_differences(self):
        """[levenshtein-python] no differences"""
        expected = 0
        observed = distance('wonderful', 'wonderful')
        self.assertEqual(expected, observed)

    def test_one_insertion(self):
        """[levenshtein-python] one insertion"""
        expected = 1
        observed = distance('wonderful', 'wonderiful')
        self.assertEqual(expected, observed)
    
    def test_one_deletion(self):
        """[levenshtein-python] one deletion"""
        expected = 1
        observed = distance('wonderful', 'wondeful')
        self.assertEqual(expected, observed)
    
    def test_one_substitution(self):
        """[levenshtein-python] one substitution"""
        expected = 1
        observed = distance('wonderful', 'wondetful')
        self.assertEqual(expected, observed)
    
    def test_two_insertions(self):
        """[levenshtein-python] two insertions"""
        expected = 2
        observed = distance('wonderful', 'woinderiful')
        self.assertEqual(expected, observed)
    
    def test_two_deletions(self):
        """[levenshtein-python] two deletions"""
        expected = 2
        observed = distance('wonderful', 'wondful')
        self.assertEqual(expected, observed)
    
    def test_two_substitutions(self):
        """[levenshtein-python] two substitutions"""
        expected = 2
        observed = distance('wonderful', 'tonderfil')
        self.assertEqual(expected, observed)
        
    def test_one_subs_one_deletion(self):
        """[levenshtein-python] one substitution, one deletion"""
        expected = 2
        observed = distance('wonderful', 'tonderfl')
        self.assertEqual(expected, observed)
    
    def test_one_ins_one_deletion(self):
        """[levenshtein-python] one insertion, one deletion"""
        expected = 2
        observed = distance('wonderful', 'wionderfl')
        self.assertEqual(expected, observed)

class TestPythonHammingDistance(unittest.TestCase):

    def test_zero_differences(self):
        """[hamming-python] no differences"""
        expected = 0
        observed = hamming('wonderful', 'wonderful')
        self.assertEqual(expected, observed)
    
    def test_one_substitution(self):
        """[hamming-python] one difference"""
        expected = 1
        observed = hamming('wonderful', 'wondirful')
        self.assertEqual(expected, observed)
    
    def test_one_deletion(self):
        """[hamming-python] one deletion"""
        self.assertRaises(AssertionError, hamming, 'wonderful', 'wondrful')
    
    def test_one_insertion(self):
        """[hamming-python] one insertion"""
        self.assertRaises(AssertionError, hamming, 'wonderful', 'wonderiful')

if __name__ == '__main__':
    unittest.main()
