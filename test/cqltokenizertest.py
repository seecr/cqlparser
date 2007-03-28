#!/usr/bin/env python
## begin license ##
#
#    CQLParser is parser that builts up a parsetree for the given CQL and 
#    can convert this into other formats.
#    Copyright (C) 2005-2007 Seek You Too B.V. (CQ2) http://www.cq2.nl
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
#    along with $PROGRAM; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
## end license ##

import unittest
import re
import cqltokenizer

def tokenize(s):
	return list(cqltokenizer.CQLTokenizer(s))

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
		
	def testUnfinishedLines(self):
		try:
			tokenize('ab and "cd')
			self.fail()
		except cqltokenizer.CQLTokenizerException, e:
			pass
		
	def testTokenStackOne(self):
		stack = cqltokenizer.tokenStack('term')
		self.assertTrue(stack.hasNext())
		self.assertEquals('term', stack.peek())
		self.assertEquals('term', stack.next())
		self.assertFalse(stack.hasNext())
		self.assertEquals('term', stack.prev())
		self.assertTrue(stack.hasNext())
		self.assertEquals('term', stack.next())
		try:
			stack.peek()
			self.fail()
		except StopIteration:
			pass
		try:
			stack.next()
			self.fail()
		except StopIteration:
			pass
		self.assertEquals(None, stack.safeNext())

		
	def testTokenStackTwo(self):
		stack = cqltokenizer.tokenStack('term term2')
		self.assertTrue(stack.hasNext())
		self.assertEquals('term', stack.next())
		self.assertTrue(stack.hasNext())
		self.assertEquals('term2', stack.next())
		self.assertFalse(stack.hasNext())

	def testTokenStackBookmarksSingleCase(self):
		stack = cqltokenizer.tokenStack('term0 term1 term2 term3')
		self.assertEquals('term0', stack.peek())
		stack.bookmark()
		stack.next()
		stack.next()
		stack.revertToBookmark()
		self.assertEquals('term0', stack.peek())
		
	def testTokenStackBookmarksAreStack(self):
		stack = cqltokenizer.tokenStack('term0 term1 term2 term3')
		self.assertEquals('term0', stack.peek())
		stack.bookmark()
		stack.next()
		self.assertEquals('term1', stack.peek())
		stack.bookmark()
		stack.next()
		stack.revertToBookmark()
		self.assertEquals('term1', stack.peek())
		stack.revertToBookmark()
		self.assertEquals('term0', stack.peek())
		
	def testTokenStackBookmarksCanBeDropped(self):
		stack = cqltokenizer.tokenStack('term0 term1 term2 term3')
		self.assertEquals('term0', stack.peek())
		stack.bookmark()
		stack.next()
		self.assertEquals('term1', stack.peek())
		stack.bookmark()
		stack.next()
		self.assertEquals('term2', stack.peek())
		stack.dropBookmark()
		self.assertEquals('term2', stack.peek())
		stack.revertToBookmark()
		self.assertEquals('term0', stack.peek())
		
	def testBugReportedByErik(self):
		stack = cqltokenizer.tokenStack('lom.general.title="en" AND (lom.general.title="green" OR lom.general.title="red")')
		self.assertEquals(['lom.general.title', '=', '"en"', 'AND', '(', 'lom.general.title', '=', '"green"', 'OR', 'lom.general.title', '=', '"red"', ')'], stack._tokens)
	
if __name__ == '__main__':
	unittest.main()
