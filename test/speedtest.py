from cq2utils import CQ2TestCase
from cq2utils.profileit import profile
from cqlparser import parseString, cql2string
from time import time

class SpeedTest(CQ2TestCase):

    def testSpeed(self):
        q = open('ridiculouslongquery.txt').read().strip()
        t0 = time()
        def doParse():
            for i in range(10):
                r = parseString(q)
        doParse()
        t1 = time()
        #profile(doParse, runKCacheGrind = True)
        self.assertTiming(0.060, t1-t0, 0.064) # inlined TokenStack (way less code!)
        #self.assertTiming(0.074, t1-t0, 0.078) # let re do the tokenizing
        #self.assertTiming(0.101, t1-t0, 0.103) # rewrote everything to try/except
        #self.assertTiming(0.115, t1-t0, 0.120) # inlined _tryTerm and some _construct
        #self.assertTiming(0.132, t1-t0, 0.136) # inlined _tryTerm and some _construct
        #self.assertTiming(0.141, t1-t0, 0.149) # optimized _tryTerms
        #self.assertTiming(0.155, t1-t0, 0.165) # replaced Stack with []
        #self.assertTiming(0.180, t1-t0, 0.190) # start
