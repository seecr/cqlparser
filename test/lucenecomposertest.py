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
from unittest import TestCase
from lucenecomposer import fromString as cqlToLucene, ParseException

class LuceneComposerTest(TestCase):
	
	def testEmptyOutput(self):
		self.assertConversion("")
		self.assertConversion("", "  \t \n")
	
	def testOneTermOutput(self):
		self.assertConversion("cat")
		
	def testOneTermOutputWithANumber(self):
		self.assertConversion("2005")

	def testPhraseOutput(self):
		self.assertConversion('"cats dogs"')
		
	def testMultipleTermsWithoutRelationAreIllegal(self):
		self.assertUnsupportedQuery('cats dogs')
		self.assertUnsupportedQuery('cats AND dogs "mice sheep"')
		
	def testIndexRelationTermOutput(self):
		self.assertConversion('animal:cats', 'animal=cats')
		self.assertConversion('generic1:cats', 'generic1=cats')
		self.assertConversion('animal:"cats dogs"', 'animal="cats dogs"')
	
	def testBooleanAndTermOutput(self):
		self.assertConversion('cats AND dogs')
		self.assertConversion('cats AND "mice sheep"')
		
	def testBooleanOrTermOutput(self):
		self.assertConversion('cats OR dogs')
		
	def testBooleanNotTermOutput(self):
		self.assertConversion('cats NOT dogs')
		
	def testBraces(self):
		self.assertConversion('(cats)')
		self.assertConversion('(cats AND dogs) OR mice')
		self.assertConversion('cats AND (dogs OR mice)')
		
	def testIsPrefixQuery(self):
		self.assertUnsupportedQuery('>http://blah.org cats NOT dogs')
		self.assertUnsupportedQuery('cats AND (>http://www.zoo.org dogs)')
		self.assertUnsupportedQuery('>PREFIX=http://blah.org cats NOT dogs')
		
	def testRelationQuery(self):
		self.assertUnsupportedQuery('dc.title any/relevant/rel.CORI "cat fish"')
	
	def assertUnsupportedQuery(self, query):
		try:
			result = cqlToLucene(query)
			self.fail()
		except ParseException, e:
			self.assertEquals('Unsupported query', str(e))
			
	def assertConversion(self, expected, input = None):
		if input == None:
			input = expected
		result = cqlToLucene(input)
		self.assertEquals(expected, result)			
		