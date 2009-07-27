# -*- coding: utf-8 -*-
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

import unittest
from cqlparser.cqlparser import CQLParser, parseString, \
    CQL_QUERY, SCOPED_CLAUSE, SEARCH_CLAUSE, BOOLEAN, SEARCH_TERM, INDEX, RELATION, COMPARITOR, MODIFIERLIST, MODIFIER, TERM, IDENTIFIER, UnsupportedCQL, CQLParseException

class CQLParserTest(unittest.TestCase):
    """http://www.loc.gov/standards/sru/sru1-1archive/cql.html"""

    def testNoTerms(self):
        self.assertException(CQLParseException, '')

    def testOneTerm(self):
        self.assertEquals(CQL_QUERY(SCOPED_CLAUSE(SEARCH_CLAUSE(SEARCH_TERM(TERM('term'))))), parseString('term'))
        self.assertEquals(CQL_QUERY(SCOPED_CLAUSE(SEARCH_CLAUSE(SEARCH_TERM(TERM('white space'))))), parseString('"white space"'))
        self.assertEquals(CQL_QUERY(SCOPED_CLAUSE(SEARCH_CLAUSE(SEARCH_TERM(TERM('string "quotes"'))))), parseString(r'"string \"quotes\""'))
        
    def testTwoTerms(self):
        self.assertEquals(
            CQL_QUERY(SCOPED_CLAUSE(
                SEARCH_CLAUSE(SEARCH_TERM(TERM('term'))), BOOLEAN('and'),
                    SCOPED_CLAUSE(SEARCH_CLAUSE(SEARCH_TERM(TERM('term2')))))),
            parseString('term and term2'))

    def testPrecedence(self):
        answer = CQL_QUERY(
            SCOPED_CLAUSE(
                SCOPED_CLAUSE(
                    SEARCH_CLAUSE(SEARCH_TERM(TERM('term'))),
                    BOOLEAN('and'),
                    SEARCH_CLAUSE(SEARCH_TERM(TERM('term2')))
                ),
                BOOLEAN('or'),
                SEARCH_CLAUSE(SEARCH_TERM(TERM('term3')))
            )
        )
        self.assertEquals(answer, parseString('term and term2 or term3'))
        
    def testAddClauseToQuery(self):
        q1 = parseString('term1')
        q2 = parseString('term2')
        q3 = q1.andQuery(q2)
        should = parseString('term1 AND term2')
        self.assertEquals(should, q3)

        q4 = parseString('term4')
        print str(q4)
        q5 = q3.andQuery(q4)
        should = parseString('term1 AND term2 AND term4')
        self.assertEquals(should, q5)

        q6 = parseString('term6')
        q7 = q5.andQuery(q6)
        should = parseString('term1 AND term2 AND term4 AND term6')
        self.assertEquals(should, q7)


    def testBooleansAreCaseInsensitive(self):
        self.assertEquals(
            CQL_QUERY(SCOPED_CLAUSE(
                SEARCH_CLAUSE(SEARCH_TERM(TERM('term'))), BOOLEAN('and'),
                    SCOPED_CLAUSE(SEARCH_CLAUSE(SEARCH_TERM(TERM('term2')))))),
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
        ST = SEARCH_TERM
        T = TERM
        self.assertEquals(Q(SC(SE(Q(SC(SE(ST(T('term')))))))), parseString('(term)'))
        self.assertEquals(Q(SC(SE(Q(SC(SE(Q(SC(SE(ST(T('term'))))))))))), parseString('((term))'))

        self.assertEquals(Q(SC(SE(Q(SC(SE(ST(T('term'))), BOOLEAN('and'), SC(SE(ST(T('term2'))))))))), parseString('(term and term2)'))

        self.assertException(CQLParseException, '(term')
        self.assertException(CQLParseException, '(term term2')

    def testTermsAreIdentifiers(self):
        self.assertException(CQLParseException, ')')

    def testIndexRelationSearchTerm(self):
        Q = CQL_QUERY
        SC = SCOPED_CLAUSE
        SE = SEARCH_CLAUSE
        ST = SEARCH_TERM
        T = TERM
        R = RELATION
        self.assertEquals(Q(SC(SE(INDEX(T('field1')), R(COMPARITOR('=')), ST(T('200'))))), parseString('field1 = 200'))
        for comparitor in ['>', '<', '>=', '<=', '<>']:
            self.assertException(UnsupportedCQL, 'field1 %s 200' % comparitor, supportedComparitors=['='])

    def testModifiers(self):
        Q = CQL_QUERY
        SC = SCOPED_CLAUSE
        SE = SEARCH_CLAUSE
        ST = SEARCH_TERM
        T = TERM
        self.assertEquals(Q(SC(SE(INDEX(T('field0')), RELATION(COMPARITOR('='), MODIFIERLIST(MODIFIER(T("boost"), COMPARITOR("="), T("1.5")))), ST(T('value'))))), parseString("field0 =/boost=1.5 value"))

    def testIndexRelationExactSearchTerm(self):
        Q = CQL_QUERY
        SC = SCOPED_CLAUSE
        SE = SEARCH_CLAUSE
        ST = SEARCH_TERM
        T = TERM
        R = RELATION
        self.assertEquals(Q(SC(SE(INDEX(T('field1')), R(COMPARITOR('exact')), ST(T('200'))))), parseString('field1 exact 200'))

    def testInvalidModifiers(self):
        self.assertException(CQLParseException, 'field0 =/')
        self.assertException(CQLParseException, 'field0 =/boost')
        self.assertException(CQLParseException, 'field0 =/boost=')
        self.assertException(CQLParseException, 'field0 =/boost>10')
        self.assertException(UnsupportedCQL, 'field0 =/not_boost=1.0 value', supportedModifierNames=['aap'])

    def testAcceptVisitor(self):
        q = CQL_QUERY(None)
        c = COMPARITOR('=')
        class MockVisitor(object):
            def __init__(self):
                self.visitCQL_QUERY_called = 0
                self.visitCQL_QUERY_args = []
                self.visitCOMPARITOR_called = 0
                self.visitCOMPARITOR_args = []
            def visitCQL_QUERY(self, *args):
                self.visitCQL_QUERY_called += 1
                self.visitCQL_QUERY_args += args
            def visitCOMPARITOR(self, *args):
                self.visitCOMPARITOR_called += 1
                self.visitCOMPARITOR_args += args

        mockVisitor = MockVisitor()
        q.accept(mockVisitor)
        self.assertEquals(1, mockVisitor.visitCQL_QUERY_called)
        self.assertEquals(q, mockVisitor.visitCQL_QUERY_args[0])
        c.accept(mockVisitor)
        self.assertEquals(1, mockVisitor.visitCOMPARITOR_called)
        self.assertEquals(c, mockVisitor.visitCOMPARITOR_args[0])

    def testVisitReturnValue(self):
        q = CQL_QUERY(None)
        class MockVisitor(object):
            def visitCQL_QUERY(self, *args):
                return 'nut'
        mockVisitor = MockVisitor()
        value = q.accept(mockVisitor)
        self.assertEquals('nut', value)

    def testPrettyPrintSimple(self):
        q = parseString('aap')
        self.assertEquals("""CQL_QUERY(
    SCOPED_CLAUSE(
        SEARCH_CLAUSE(
            SEARCH_TERM(
                TERM('aap')
            )
        )
    )
)""", q.prettyPrint())

    def testPrettyPrintComplex(self):
        q = parseString('aap AND (noot = mies OR vuur)')
        self.assertEquals("""CQL_QUERY(
    SCOPED_CLAUSE(
        SEARCH_CLAUSE(
            SEARCH_TERM(
                TERM('aap')
            )
        ),
        BOOLEAN('and'),
        SCOPED_CLAUSE(
            SEARCH_CLAUSE(
                CQL_QUERY(
                    SCOPED_CLAUSE(
                        SEARCH_CLAUSE(
                            INDEX(
                                TERM('noot')
                            ),
                            RELATION(
                                COMPARITOR('=')
                            ),
                            SEARCH_TERM(
                                TERM('mies')
                            )
                        ),
                        BOOLEAN('or'),
                        SCOPED_CLAUSE(
                            SEARCH_CLAUSE(
                                SEARCH_TERM(
                                    TERM('vuur')
                                )
                            )
                        )
                    )
                )
            )
        )
    )
)""", q.prettyPrint())

    ### Helper methods
    def assertException(self, exceptionClass, queryString, **kwargs):
        try:
            parseString(queryString, **kwargs)
            self.fail()
        except exceptionClass, e:
            pass
