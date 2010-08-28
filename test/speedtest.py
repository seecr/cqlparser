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
        #profile(doParse, runKCacheGrind = True)
        t1 = time()
        self.assertTiming(0.141, t1-t0, 0.149) # optimized _tryTerms
        #self.assertTiming(0.155, t1-t0, 0.165) # replaced Stack with []
        #self.assertTiming(0.180, t1-t0, 0.190) # start
