## begin license ##
#
# "CQLParser" is a parser that builds a parsetree for the given CQL and can convert this into other formats.
#
# Copyright (C) 2005-2010 Seek You Too (CQ2) http://www.cq2.nl
# Copyright (C) 2018, 2020 Seecr (Seek You Too B.V.) https://seecr.nl
#
# This file is part of "CQLParser"
#
# "CQLParser" is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# "CQLParser" is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with "CQLParser"; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
## end license ##

import unittest

from cqlparser import CQLTokenizerException
from cqlparser.cqltokenizer import tokenize


class CQLTokenizerTest(unittest.TestCase):
    def testTokens(self):
        self.assertEqual(['abc'], tokenize('abc'))
        self.assertEqual(['abc','def'], tokenize('abc def'))
        self.assertEqual(['(', 'abc',')', 'def'], tokenize('(abc) def'))
        self.assertEqual(['(', r'"a \"bc\" d"',')', 'def'], tokenize(r'("a \"bc\" d") def'))
        self.assertEqual(['"a"', 'AND', '"b"'], tokenize('"a" AND "b"'))
        self.assertEqual(['(', '>', 'abc',')', 'def'], tokenize('( > abc) def'))
        self.assertEqual([r'\\', r'bla\*bla'], tokenize(r'\\ bla\*bla'))
        # Test cases from http://loc.gov/cql
        self.assertEqual(['dinosaur'], tokenize('dinosaur'))
        self.assertEqual(['"complete dinosaur"'], tokenize('"complete dinosaur"'))
        self.assertEqual(['title', '=', '"complete dinosaur"'], tokenize('title = "complete dinosaur"'))
        self.assertEqual(['title', 'exact', '"the complete dinosaur"'], tokenize('title exact "the complete dinosaur"'))
        self.assertEqual(['title', '==', '"the complete dinosaur"'], tokenize('title == "the complete dinosaur"'))
        self.assertEqual(['(', 'bird', 'or', 'dinosaur', ')', 'and', '(', 'feathers', 'or', 'scales', ')'], tokenize('(bird or dinosaur) and (feathers or scales)'))
        self.assertEqual(['"feathered dinosaur"', 'and', '(', 'yixian', 'or', 'jehol', ')'], tokenize('"feathered dinosaur" and (yixian or jehol)'))
        self.assertEqual(['lengthOfFemur', '>', '2.4'], tokenize('lengthOfFemur > 2.4'))
        self.assertEqual(['bioMass', '>=', '100'], tokenize('bioMass >= 100'))
        self.assertEqual(['"dino(saur)"'], tokenize('"dino(saur)"'))
        self.assertEqual(['"\nterm with newline"'], tokenize('"\nterm with newline"'))

    def testUnfinishedLines(self):
        try:
            r = tokenize('ab and "cd')
            self.fail(r)
        except CQLTokenizerException as e:
            pass

    def testLongUnfinishedLinesDoesntCauseHanging(self):
        # Production issue discovered and fixed on June 10 2011
        try:
            r = tokenize('abcdefghijklmnopqrstuvwx and "yz')
            self.fail(r)
        except CQLTokenizerException as e:
            pass

    def testBugReportedByErik(self):
        stack = tokenize('lom.general.title="en" AND (lom.general.title="green" OR lom.general.title="red")')
        self.assertEqual(['lom.general.title', '=', '"en"', 'AND', '(', 'lom.general.title', '=', '"green"', 'OR', 'lom.general.title', '=', '"red"', ')'], stack)
