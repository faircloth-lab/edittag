#!/usr/bin/env python
# encoding: utf-8

"""
test_py

Created by Brant Faircloth on 17 January 2011 1300 PST (-0800).
Copyright (c) 2011 Brant C. Faircloth. All rights reserved.
"""

import unittest
from Levenshtein import distance
from Levenshtein import hamming

import pdb

class TestPythonLevenshteinDistance(unittest.TestCase):
    
    def test_zero_differences(self):
        """[levenshtein-c] no differences"""
        expected = 0
        observed = distance('wonderful', 'wonderful')
        self.assertEqual(expected, observed)

    def test_one_insertion(self):
        """[levenshtein-c] one insertion"""
        expected = 1
        observed = distance('wonderful', 'wonderiful')
        self.assertEqual(expected, observed)
    
    def test_one_deletion(self):
        """[levenshtein-c] one deletion"""
        expected = 1
        observed = distance('wonderful', 'wondeful')
        self.assertEqual(expected, observed)
    
    def test_one_substitution(self):
        """[levenshtein-c] one substitution"""
        expected = 1
        observed = distance('wonderful', 'wondetful')
        self.assertEqual(expected, observed)
    
    def test_two_insertions(self):
        """[levenshtein-c] two insertions"""
        expected = 2
        observed = distance('wonderful', 'woinderiful')
        self.assertEqual(expected, observed)
    
    def test_two_deletions(self):
        """[levenshtein-c] two deletions"""
        expected = 2
        observed = distance('wonderful', 'wondful')
        self.assertEqual(expected, observed)
    
    def test_two_substitutions(self):
        """[levenshtein-c] two substitutions"""
        expected = 2
        observed = distance('wonderful', 'tonderfil')
        self.assertEqual(expected, observed)
        
    def test_one_subs_one_deletion(self):
        """[levenshtein-c] one substitution, one deletion"""
        expected = 2
        observed = distance('wonderful', 'tonderfl')
        self.assertEqual(expected, observed)
    
    def test_one_ins_one_deletion(self):
        """[levenshtein-c] one insertion, one deletion"""
        expected = 2
        observed = distance('wonderful', 'wionderfl')
        self.assertEqual(expected, observed)

class TestPythonHammingDistance(unittest.TestCase):

    def test_zero_differences(self):
        """[hamming-c] no differences"""
        expected = 0
        observed = hamming('wonderful', 'wonderful')
        self.assertEqual(expected, observed)
    
    def test_one_substitution(self):
        """[hamming-c] one difference"""
        expected = 1
        observed = hamming('wonderful', 'wondirful')
        self.assertEqual(expected, observed)
    
    def test_one_deletion(self):
        """[hamming-c] one deletion"""
        self.assertRaises(ValueError, hamming, 'wonderful', 'wondrful')
    
    def test_one_insertion(self):
        """[hamming-c] one insertion"""
        self.assertRaises(ValueError, hamming, 'wonderful', 'wonderiful')

if __name__ == '__main__':
    unittest.main()
