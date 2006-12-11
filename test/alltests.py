#!/usr/bin/env python
#
# Generated with:
#
# $Id$
#
# on Mon Jul 24 16:12:39 CEST 2006 by thijs
#

import os, sys
os.system('rm -f *.pyc')

sys.path.insert(0, '../src')

import unittest

from cqlparsertest import CQLParserTest
from cqltokenizertest import CQLTokenizerTest

if __name__ == '__main__':
        unittest.main()

