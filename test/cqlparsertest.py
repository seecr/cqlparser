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

from cqlparser import CQLParser, parseString, \
    CQL_QUERY, SCOPED_CLAUSE, SEARCH_CLAUSE, BOOLEAN, SEARCH_TERM, INDEX, RELATION, COMPARITOR, MODIFIER, UnsupportedCQL, CQLParseException

class CQLParserTest(unittest.TestCase):
    """http://www.loc.gov/standards/sru/sru1-1archive/cql.html"""

    def testOneTerm(self):
        self.assertEquals(CQL_QUERY(SCOPED_CLAUSE(SEARCH_CLAUSE(SEARCH_TERM('term')))), parseString('term'))
        self.assertEquals(CQL_QUERY(SCOPED_CLAUSE(SEARCH_CLAUSE(SEARCH_TERM('"white space"')))), parseString('"white space"'))

    def testTwoTerms(self):
        self.assertEquals(
            CQL_QUERY(SCOPED_CLAUSE(
                SEARCH_CLAUSE(SEARCH_TERM('term')), BOOLEAN('and'),
                    SCOPED_CLAUSE(SEARCH_CLAUSE(SEARCH_TERM('term2'))))),
            parseString('term and term2'))

    def testBooleansAreCaseInsensitive(self):
        self.assertEquals(
            CQL_QUERY(SCOPED_CLAUSE(
                SEARCH_CLAUSE(SEARCH_TERM('term')), BOOLEAN('and'),
                    SCOPED_CLAUSE(SEARCH_CLAUSE(SEARCH_TERM('term2'))))),
            parseString('term AnD term2'))

    def testPrefixesAreIllegal(self):
        self.assertException(UnsupportedCQL, "> prefix = some:thing aquery")

    def testUnfinishedQuery(self):
        self.assertException(CQLParseException, 'term and')

    def testIllegalBooleanGroups(self):
        self.assertException(CQLParseException, 'term notanyof_and_or_not_prox term2')
        self.assertException(UnsupportedCQL, 'term prox term2')

    def testParentheses(self):
        Q = CQL_QUERY
        SC = SCOPED_CLAUSE
        SE = SEARCH_CLAUSE
        T = SEARCH_TERM
        self.assertEquals(Q(SC(SE("(", Q(SC(SE(T('term')))), ")"))), parseString('(term)'))
        self.assertEquals(Q(SC(SE("(", Q(SC(SE("(", Q(SC(SE(T('term')))), ")"))), ")"))), parseString('((term))'))

        self.assertEquals(Q(SC(SE("(", Q(SC(SE(T('term')), BOOLEAN('and'), SC(SE(T('term2'))))), ")"))), parseString('(term and term2)'))

        self.assertException(CQLParseException, '(term')
        self.assertException(CQLParseException, '(term term2')

    def testTermsAreIdentifiers(self):
        self.assertException(CQLParseException, ')')

    def testIndexRelationSearchTerm(self):
        Q = CQL_QUERY
        SC = SCOPED_CLAUSE
        SE = SEARCH_CLAUSE
        T = SEARCH_TERM
        R = RELATION
        self.assertEquals(Q(SC(SE(INDEX('field1'), R(COMPARITOR('=')), T('200')))), parseString('field1 = 200'))
        for comparitor in ['>', '<', '>=', '<=', '<>']:
            self.assertException(UnsupportedCQL, 'field1 %s 200' % comparitor)

    def testModifiers(self):
        Q = CQL_QUERY
        SC = SCOPED_CLAUSE
        SE = SEARCH_CLAUSE
        T = SEARCH_TERM
        self.assertEquals(Q(SC(SE(INDEX('field0'), RELATION(COMPARITOR('any'), MODIFIER("boost", "=", "1.5")), T('value')))), parseString("field0 any/boost=1.5 value"))

    def testInvalidModifiers(self):
        self.assertException(CQLParseException, 'field0 any /')
        self.assertException(UnsupportedCQL, 'field0 any /field0')
        self.assertException(CQLParseException, 'field0 any /field0=')
        self.assertException(UnsupportedCQL, 'field0 any /field0>10')

    ### Helper methods
    def assertException(self, exceptionClass, queryString):
        try:
            parseString(queryString)
            self.fail()
        except exceptionClass, e:
            pass
