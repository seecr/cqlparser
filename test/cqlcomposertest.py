## begin license ##
#
#    CQLParser is a parser that builds a parsetree for the given CQL and
#    can convert this into other formats.
#    Copyright (C) 2005-2009 Seek You Too (CQ2) http://www.cq2.nl
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
from unittest import TestCase
from cqlparser.cqlcomposer import fromString as astToCQL, ParseException

class CQLComposerTest(TestCase):
    
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
        self.assertUnsupportedQuery('cats and dogs "mice sheep"')
        
    def testIndexRelationTermOutput(self):
        self.assertConversion('animal=cats')
        self.assertConversion('generic1=cats')
        self.assertConversion('animal="cats dogs"')
    
    def testBooleanAndTermOutput(self):
        self.assertConversion('cats and dogs')
        self.assertConversion('cats and "mice sheep"')
        
    def testBooleanOrTermOutput(self):
        self.assertConversion('cats or dogs')
        
    def testBooleanNotTermOutput(self):
        self.assertConversion('cats not dogs')
        
    def testBraces(self):
        self.assertConversion('(cats)')
        self.assertConversion('(cats and dogs) or mice')
        self.assertConversion('cats and (dogs or mice)')
        
    def testIsPrefixQuery(self):
        self.assertUnsupportedQuery('>http://blah.org cats not dogs')
        self.assertUnsupportedQuery('cats and (>http://www.zoo.org dogs)')
        self.assertUnsupportedQuery('>PREFIX=http://blah.org cats not dogs')
        
    def testRelationQuery(self):
        self.assertUnsupportedQuery('dc.title any/relevant/rel.CorI "cat fish"')
    
    def assertUnsupportedQuery(self, query):
        try:
            result = astToCQL(query)
            self.fail()
        except ParseException, e:
            self.assertEquals('Unsupported query', str(e))
            
    def assertConversion(self, expected, input = None):
        if input == None:
            input = expected
        result = astToCQL(input)
        self.assertEquals(expected, result)            
        
