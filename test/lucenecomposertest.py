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
			

if __name__ == '__main__':
	unittest.main()
