## begin license ##
#
# "CQLParser" is a parser that builds a parsetree for the given CQL and can convert this into other formats.
#
# Copyright (C) 2012-2013, 2020 Seecr (Seek You Too B.V.) https://seecr.nl
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

from seecrtest.timing import T
from unittest import TestCase
#from cq2utils.profileit import profile
from cqlparser import parseString, cql2string, CqlIdentityVisitor, CqlVisitor
from time import time

class SpeedTest(TestCase):
    @staticmethod
    def ridiculouslongquery():
        with open('ridiculouslongquery.txt') as f:
            return f.read().strip()

    def testParser(self):
        q = self.ridiculouslongquery()
        def doParse():
            for i in range(10):
                r = parseString(q)
        t0 = time()
        doParse()
        t1 = time()
        #profile(doParse, runKCacheGrind = True)
        self.assertTiming(0.058, t1-t0, 0.065) # bugfix with AND NOT (implementation following BNF)
        #self.assertTiming(0.050, t1-t0, 0.054) # side effect of optimizing visitor
        #self.assertTiming(0.053, t1-t0, 0.057) # used __slots__ in CqlAbstractNode
        #self.assertTiming(0.060, t1-t0, 0.064) # inlined TokenStack (way less code!)
        #self.assertTiming(0.074, t1-t0, 0.078) # let re do the tokenizing
        #self.assertTiming(0.101, t1-t0, 0.103) # rewrote everything to try/except
        #self.assertTiming(0.115, t1-t0, 0.120) # inlined _tryTerm and some _construct
        #self.assertTiming(0.132, t1-t0, 0.136) # inlined _tryTerm and some _construct
        #self.assertTiming(0.141, t1-t0, 0.149) # optimized _tryTerms
        #self.assertTiming(0.155, t1-t0, 0.165) # replaced Stack with []
        #self.assertTiming(0.180, t1-t0, 0.190) # start

    def testIdentityVisitor(self):
        p = parseString(self.ridiculouslongquery())
        def doVisit():
            for i in range(10):
                CqlIdentityVisitor(p).visit()
        t0 = time()
        doVisit()
        t1 = time()
        #profile(doVisit, runKCacheGrind = True)
        self.assertTiming(0.032, t1-t0, 0.041) # optimized identityvisitor
        #self.assertTiming(0.050, t1-t0, 0.053) # made visitXYZ() optional
        #self.assertTiming(0.064, t1-t0, 0.068) # replaced children() attr access and replaced tuple by list
        #self.assertTiming(0.100, t1-t0, 0.110) # start

    def testPartialVisitor(self):
        class PartialVisitor(CqlVisitor):
            def visitINDEX(self, node):
                return node.visitChildren(self)
        p = parseString(self.ridiculouslongquery())
        def doVisit():
            for i in range(10):
                PartialVisitor(p).visit()
        t0 = time()
        doVisit()
        t1 = time()
        #profile(doVisit, runKCacheGrind = True)
        self.assertTiming(0.018, t1-t0, 0.024)

    def assertTiming(self, t0, t, t1):
        self.assertTrue(t0*T < t < t1*T, t/T)
