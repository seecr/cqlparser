## begin license ##
#
# "Edurep" is a service for searching in educational repositories.
# "Edurep" is developed for Stichting Kennisnet (http://www.kennisnet.nl) by
# Seek You Too (http://www.cq2.nl). The project is based on the opensource
# project Meresco (http://www.meresco.com).
#
# Copyright (C) 2015 Seecr (Seek You Too B.V.) http://seecr.nl
# Copyright (C) 2015 Stichting Kennisnet http://www.kennisnet.nl
#
# This file is part of "Edurep"
#
# "Edurep" is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# "Edurep" is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with "Edurep"; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
## end license ##

from seecr.test import SeecrTestCase
from cqlparser import parseString as parseCql
from cqlparser.cqltoexpression import cqlToExpression, QueryExpression

class CqlToExpressionTest(SeecrTestCase):

    def testSimpleExpression(self):
        expression = toExpression('field=value')
        self.assertEquals("field", expression.index)
        self.assertEquals("=", expression.relation)
        self.assertEquals("value", expression.term)

    def testSimpleExpressionWithParenthesis(self):
        expression = toExpression('((field=value))')
        self.assertEquals("field", expression.index)
        self.assertEquals("=", expression.relation)
        self.assertEquals("value", expression.term)

    def testSimpleExpressionWithoutIndex(self):
        expression = toExpression('value')
        self.assertEquals(None, expression.index)
        self.assertEquals(None, expression.relation)
        self.assertEquals("value", expression.term)

    def testAndExpression(self):
        expression = toExpression('field0=value0 AND field1=value1')
        self.assertEquals("AND", expression.operator)
        self.assertEquals(2, len(expression.operands))
        self.assertEquals(['field0', 'field1'], [e.index for e in expression.operands])

    def testAndExpressionMoreThanOne(self):
        expression = toExpression('field0=value0 AND field1=value1 AND field2 = value2')
        self.assertEquals("AND", expression.operator)
        self.assertEquals(3, len(expression.operands))
        self.assertEquals([QE('field0=value0'), QE('field1=value1'), QE('field2=value2')], expression.operands)
        expression = toExpression('field0=value0 AND (field1=value1 AND field2=value2)')
        self.assertEquals(QueryExpression(
                operator='AND',
                operands=[QE('field0=value0'), QE('field1=value1'), QE('field2=value2')],
            ), expression)

    def testOrExpressions(self):
        expression = toExpression('field0=value0 AND field1=value1 OR field2 = value2')
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
        expression2 = toExpression('(field0=value0 AND field1=value1) OR field2 = value2')
        self.assertEquals(expression, expression2)

        expression = toExpression('field0=value0 AND (field1=value1 OR field2 = value2)')
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
        expression = toExpression('term NOT thisterm')
        self.assertEquals(QueryExpression(
                operator='AND',
                operands=[
                    QE('term'),
                    QE('thisterm', must_not=True),
                ]
            ), expression)

    def testNotNested(self):
        expression = toExpression('term NOT (A AND B)')
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
        self.assertEquals(toExpression('field=value AND otherfield=othervalue'), QueryExpression(operator='AND', operands=[QE('field=value'), QE('otherfield=othervalue')]))

    def testBoost(self):
        expression = toExpression("title =/boost=2.0 cats")
        self.assertEqual(QE('title=cats', relation_boost=2.0), expression)

    def testAsDictFromDict(self):
        expression = toExpression('aap NOT (noot OR title=mies) AND subject =/boost=3.0 boeien')
        d = expression.asDict()
        self.assertEquals(dict, type(d))
        self.assertEquals(expression, QueryExpression.fromDict(d))


def pprintE(expression, indent=0):
    operator = getattr(expression, 'operator', None)
    if operator:
        print "{0}{1}{2}".format(' '*indent,
                '!' if getattr(expression, 'must_not', False) else '',
                operator)
        for operand in expression.operands:
            pprintE(operand, indent+1)
    else:
        print "{0}{1}{2}{3}{4}".format(
                ' '*indent,
                '!' if getattr(expression, 'must_not', False) else '',
                expression.index or '',
                expression.relation or '',
                expression.term,
            )

def QE(aString, **kwargs):
    if '=' in aString:
        result = QueryExpression(index=aString.split('=', 1)[0], relation='=', term=aString.split('=',1)[-1])
    else:
        result = QueryExpression(index=None, relation=None, term=aString)
    for k,v in kwargs.items():
        setattr(result, k, v)
    return result


def toExpression(cqlstring):
    ast = parseCql(cqlstring)
    return cqlToExpression(ast)
