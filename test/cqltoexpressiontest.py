## begin license ##
#
# "CQLParser" is a parser that builds a parsetree for the given CQL and can convert this into other formats.
#
# Copyright (C) 2015, 2020 Seecr (Seek You Too B.V.) http://seecr.nl
# Copyright (C) 2015 Stichting Kennisnet http://www.kennisnet.nl
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

from unittest import TestCase

from cqlparser import parseString as parseCql
from cqlparser.cqltoexpression import cqlToExpression, QueryExpression


class CqlToExpressionTest(TestCase):
    def testSimpleExpression(self):
        expression = cqlToExpression(parseCql('field=value'))
        self.assertEquals("field", expression.index)
        self.assertEquals("=", expression.relation)
        self.assertEquals("value", expression.term)

    def testSimpleExpressionWithParenthesis(self):
        expression = cqlToExpression('((field=value))')
        self.assertEquals("field", expression.index)
        self.assertEquals("=", expression.relation)
        self.assertEquals("value", expression.term)

    def testSimpleExpressionWithoutIndex(self):
        expression = cqlToExpression('value')
        self.assertEquals(None, expression.index)
        self.assertEquals(None, expression.relation)
        self.assertEquals("value", expression.term)

    def testSimpleQuotedTermExpression(self):
        expression = cqlToExpression('"the value"')
        self.assertEquals(None, expression.index)
        self.assertEquals(None, expression.relation)
        self.assertEquals("the value", expression.term)
        self.assertEquals('\'"the value"\'', str(expression))

    def testAndExpression(self):
        expression = cqlToExpression('field0=value0 AND field1=value1')
        self.assertEquals("AND", expression.operator)
        self.assertEquals(2, len(expression.operands))
        self.assertEquals(['field0', 'field1'], [e.index for e in expression.operands])

    def testAndExpressionMoreThanOne(self):
        expression = cqlToExpression('field0=value0 AND field1=value1 AND field2 = value2')
        self.assertEquals("AND", expression.operator)
        self.assertEquals(3, len(expression.operands))
        self.assertEquals([QE('field0=value0'), QE('field1=value1'), QE('field2=value2')], expression.operands)
        expression = cqlToExpression('field0=value0 AND (field1=value1 AND field2=value2)')
        self.assertEquals(QueryExpression(
                operator='AND',
                operands=[QE('field0=value0'), QE('field1=value1'), QE('field2=value2')],
            ), expression)

    def testOrExpressions(self):
        expression = cqlToExpression('field0=value0 AND field1=value1 OR field2 = value2')
        self.assertEquals(QueryExpression(
                operator='OR',
                operands=[
                    QueryExpression(
                        operator='AND',
                        operands=[
                            QE('field0=value0'),
                            QE('field1=value1'),
                        ]
                    ),
                    QE('field2=value2'),
                ]
            ), expression)
        expression2 = cqlToExpression('(field0=value0 AND field1=value1) OR field2 = value2')
        self.assertEquals(expression, expression2)

        expression = cqlToExpression('field0=value0 AND (field1=value1 OR field2 = value2)')
        self.assertEquals(QueryExpression(
                operator='AND',
                operands=[
                    QE('field0=value0'),
                    QueryExpression(
                        operator='OR',
                        operands=[
                            QE('field1=value1'),
                            QE('field2=value2'),
                        ]
                    ),
                ]
            ), expression)

    def testNot(self):
        expression = cqlToExpression('term NOT thisterm')
        self.assertEquals(QueryExpression(
                operator='AND',
                operands=[
                    QE('term'),
                    QE('thisterm', must_not=True),
                ]
            ), expression)

    def testNotNested(self):
        expression = cqlToExpression('term NOT (A AND B)')
        self.assertEquals(QueryExpression(
                operator='AND',
                operands=[
                    QE('term'),
                    QueryExpression(
                        operator='AND',
                        must_not=True,
                        operands=[
                            QE('A'),
                            QE('B'),
                        ]
                    ),
                ]
            ), expression)

    def testEquals(self):
        self.assertEquals(QueryExpression(index='field', relation='=', term='term'), QueryExpression(index='field', relation='=', term='term'))
        self.assertEquals(cqlToExpression('field=value AND otherfield=othervalue'), QueryExpression(operator='AND', operands=[QE('field=value'), QE('otherfield=othervalue')]))
        self.assertTrue(QueryExpression.searchterm('a') == QueryExpression.searchterm('a'))
        self.assertFalse(QueryExpression.searchterm('a') != QueryExpression.searchterm('a'))
        self.assertFalse(QueryExpression.searchterm('a') == QueryExpression.searchterm('b'))
        self.assertTrue(QueryExpression.searchterm('a') != QueryExpression.searchterm('b'))

    def testBoost(self):
        expression = cqlToExpression("title =/boost=2.0 cats")
        self.assertEqual(QE('title=cats', relation_boost=2.0), expression)

    def testAsDictFromDict(self):
        expression = cqlToExpression('aap NOT (noot OR title=mies) AND subject =/boost=3.0 boeien')
        d = expression.asDict()
        self.assertEquals(dict, type(d))
        self.assertEquals(expression, QueryExpression.fromDict(d))

    def testPrettyPrint(self):
        expression = cqlToExpression('aap NOT (noot OR title=mies)')
        prettyTrue = expression.toString(pretty_print=True)
        self.assertEquals("""\
AND
    'aap'
    !OR
        'noot'
        'title = mies'\
""", prettyTrue)
        prettyDefault = expression.toString()
        self.assertEquals(prettyTrue, prettyDefault)
        prettyFalse = expression.toString(pretty_print=False)
        self.assertEquals("AND['aap', !OR['noot', 'title = mies']]", prettyFalse)

    def testAcceptsCqlAstAndQueryExpression(self):
        a = cqlToExpression('field = value')
        b = cqlToExpression(parseCql('field = value'))
        c = cqlToExpression(b)
        self.assertEquals(a, b)
        self.assertEquals(a, c)

    def testIter(self):
        qe = cqlToExpression('aap NOT (noot OR title=mies)')
        result = list(qe.iter())
        self.assertEquals(qe, result[0])
        self.assertEquals(cqlToExpression('aap'), result[1])
        r2 = cqlToExpression('noot OR title=mies')
        r2.must_not = True
        self.assertEquals(r2, result[2])
        self.assertEquals(cqlToExpression('noot'), result[3])
        self.assertEquals(cqlToExpression('title=mies'), result[4])

    def testReplaceWith(self):
        qe = cqlToExpression('aap AND noot')
        replacement = cqlToExpression('fiets')
        qe.operands[1].replaceWith(replacement)
        self.assertEquals(cqlToExpression('aap AND fiets'), qe)
        qe.operands[0].replaceWith(cqlToExpression('boom OR vis'))
        self.assertEquals(cqlToExpression('(boom OR vis) AND fiets'), qe)

    def testRepr(self):
        qe = cqlToExpression('aap NOT (noot OR title=mies)')
        self.assertEquals("QueryExpression(operator='AND', operands=[QueryExpression(index=None, term='aap', relation=None, must_not=False, relation_boost=None, operator=None), QueryExpression(operator='OR', operands=[QueryExpression(index=None, term='noot', relation=None, must_not=False, relation_boost=None, operator=None), QueryExpression(index='title', term='mies', relation='=', must_not=False, relation_boost=None, operator=None)], must_not=True, relation_boost=None)], must_not=False, relation_boost=None)", repr(qe))
        self.assertEquals(qe, eval(repr(qe)))

    def testStrWithIndexAndQuotes(self):
        qe = cqlToExpression('field="aap noot"')
        self.assertEquals("QueryExpression(index='field', term='aap noot', relation='=', must_not=False, relation_boost=None, operator=None)", repr(qe))
        self.assertEquals('\'field = "aap noot"\'', str(qe))


def QE(aString, **kwargs):
    if '=' in aString:
        result = QueryExpression(index=aString.split('=', 1)[0], relation='=', term=aString.split('=',1)[-1])
    else:
        result = QueryExpression(index=None, relation=None, term=aString)
    for k,v in kwargs.items():
        setattr(result, k, v)
    return result
