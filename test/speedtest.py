from cq2utils import CQ2TestCase
from cq2utils.profileit import profile
from cqlparser import parseString, cql2string, CqlIdentityVisitor, CqlVisitor
from time import time

class SpeedTest(CQ2TestCase):

    def testParser(self):
        q = open('ridiculouslongquery.txt').read().strip()
        def doParse():
            for i in range(10):
                r = parseString(q)
        t0 = time()
        doParse()
        t1 = time()
        #profile(doParse, runKCacheGrind = True)
        self.assertTiming(0.053, t1-t0, 0.057) # used __slots__ in CqlAbstractNode
        #self.assertTiming(0.060, t1-t0, 0.064) # inlined TokenStack (way less code!)
        #self.assertTiming(0.074, t1-t0, 0.078) # let re do the tokenizing
        #self.assertTiming(0.101, t1-t0, 0.103) # rewrote everything to try/except
        #self.assertTiming(0.115, t1-t0, 0.120) # inlined _tryTerm and some _construct
        #self.assertTiming(0.132, t1-t0, 0.136) # inlined _tryTerm and some _construct
        #self.assertTiming(0.141, t1-t0, 0.149) # optimized _tryTerms
        #self.assertTiming(0.155, t1-t0, 0.165) # replaced Stack with []
        #self.assertTiming(0.180, t1-t0, 0.190) # start

    def testIdentityVisitor(self):
        p = parseString(open('ridiculouslongquery.txt').read().strip())
        def doVisit():
            for i in range(10):
                CqlIdentityVisitor(p).visit()
        t0 = time()
        doVisit()
        t1 = time()
        #profile(doVisit, runKCacheGrind = True)
        self.assertTiming(0.039, t1-t0, 0.041) # optimized identityvisitor
        #self.assertTiming(0.050, t1-t0, 0.053) # made visitXYZ() optional
        #self.assertTiming(0.064, t1-t0, 0.068) # replaced children() attr access and replaced tuple by list
        #self.assertTiming(0.100, t1-t0, 0.110) # start

    def testPartialVisitor(self):
        class PartialVisitor(CqlVisitor):
            def visitINDEX(self, node):
                return node.visitChildren(self)
        p = parseString(open('ridiculouslongquery.txt').read().strip())
        def doVisit():
            for i in range(10):
                PartialVisitor(p).visit()
        t0 = time()
        doVisit()
        t1 = time()
        #profile(doVisit, runKCacheGrind = True)
        self.assertTiming(0.021, t1-t0, 0.024) 