# -*- coding: utf-8 -*-
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

from unittest import TestCase

from cqlparser import parseString, cql2string, quotTerm

class Cql2StringTest(TestCase):
    def testTerm(self):
        self.assertCql('term')
        self.assertCql('"term 2"')
        self.assertCql(r'"term \"two\""')

    def testQuotTerm(self):
        self.assertEqual('term', quotTerm('term'))
        self.assertEqual('"term 2"', quotTerm('term 2'))
        self.assertEqual(r'"\"two\""', quotTerm('"two"'))
        self.assertEqual(r'"(some) braces"', quotTerm('(some) braces'))

    def testTermAndTerm(self):
        self.assertCql('term1 AND term2')
        self.assertCql('term1 AND term2 AND term3')
        self.assertCql('term1 AND term2 AND term3 AND term4')
        self.assertCql('(term1 AND term2) OR term3 AND term4')
        self.assertCql('(term1 NOT term2) OR term3 AND term4')

    def testRelation(self):
        self.assertCql('field1=term1')
        self.assertCql('field1 exact term1')
        self.assertCql('field1=term1 AND field2 exact term2')
        self.assertCql('field1 > 3')
        self.assertCql('field1 >= 3')

    def testBraces(self):
        self.assertCql('field1=term1 AND (term2 OR term3)')

    def testBoost(self):
        self.assertCql('field0 =/boost=1.5 value')

    def assertCql(self, expected, input=None):
        if input == None:
            input = expected
        self.assertEqual(expected, cql2string(parseString(input)))
        self.assertTrue(parseString(expected))
