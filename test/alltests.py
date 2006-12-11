#!/usr/bin/env python
## begin license ##
#
#    CQLParser is parser that builts up a parsetree for the given CQL and 
#    can convert this into other formats.
#    Copyright (C) 2005, 2006 Seek You Too B.V. (CQ2) http://www.cq2.nl
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

