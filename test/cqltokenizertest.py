## begin license ##
#
#    CQLParser is a parser that builds a parsetree for the given CQL and
#    can convert this into other formats.
#    Copyright (C) 2005-2010 Seek You Too (CQ2) http://www.cq2.nl
#
#    This file is part of CQLParser
#
#    CQLParser is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    CQLParser is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with CQLParser; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
## end license ##

import unittest
import re
from cqlparser.cqltokenizer import CQLTokenizer, CQLTokenizerException

def tokenize(s):
    return CQLTokenizer(s).all()

class CQLTokenizerTest(unittest.TestCase):

    def testTokens(self):
        self.assertEquals(['abc'], tokenize('abc'))
        self.assertEquals(['abc','def'], tokenize('abc def'))
        self.assertEquals(['(', 'abc',')', 'def'], tokenize('(abc) def'))
        self.assertEquals(['(', r'"a \"bc\" d"',')', 'def'], tokenize(r'("a \"bc\" d") def'))
        self.assertEquals(['"a"', 'AND', '"b"'], tokenize('"a" AND "b"'))
        self.assertEquals(['(', '>', 'abc',')', 'def'], tokenize('( > abc) def'))
        self.assertEquals([r'\\', r'bla\*bla'], tokenize(r'\\ bla\*bla'))
        # Test cases from http://loc.gov/cql
        self.assertEquals(['dinosaur'], tokenize('dinosaur'))
        self.assertEquals(['"complete dinosaur"'], tokenize('"complete dinosaur"'))
        self.assertEquals(['title', '=', '"complete dinosaur"'], tokenize('title = "complete dinosaur"'))
        self.assertEquals(['title', 'exact', '"the complete dinosaur"'], tokenize('title exact "the complete dinosaur"'))
        self.assertEquals(['(', 'bird', 'or', 'dinosaur', ')', 'and', '(', 'feathers', 'or', 'scales', ')'], tokenize('(bird or dinosaur) and (feathers or scales)'))
        self.assertEquals(['"feathered dinosaur"', 'and', '(', 'yixian', 'or', 'jehol', ')'], tokenize('"feathered dinosaur" and (yixian or jehol)'))
        self.assertEquals(['lengthOfFemur', '>', '2.4'], tokenize('lengthOfFemur > 2.4'))
        self.assertEquals(['bioMass', '>=', '100'], tokenize('bioMass >= 100'))
        self.assertEquals(['"dino(saur)"'], tokenize('"dino(saur)"'))
        self.assertEquals(['"\nterm with newline"'], tokenize('"\nterm with newline"'))

    def testUnfinishedLines(self):
        try:
            r = tokenize('ab and "cd')
            self.fail(r)
        except CQLTokenizerException, e:
            pass

    def testBugReportedByErik(self):
        stack = CQLTokenizer('lom.general.title="en" AND (lom.general.title="green" OR lom.general.title="red")').all()
        self.assertEquals(['lom.general.title', '=', '"en"', 'AND', '(', 'lom.general.title', '=', '"green"', 'OR', 'lom.general.title', '=', '"red"', ')'], stack)
