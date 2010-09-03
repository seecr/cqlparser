## begin license ##
#
#    CQLParser is a parser that builds a parsetree for the given CQL and
#    can convert this into other formats.
#    Copyright (C) 2005-2010 Seek You Too (CQ2) http://www.cq2.nl
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

from unittest import TestCase

from cqlparser import CqlIdentityVisitor
from cqlparser import parseString

def allnodes(node):
    result = [node]
    index = 0 
    while index < len(result):
        new_index = len(result)
        for node in result[index:]:
            result.extend([n for n in node.children if hasattr(n, 'children')])
        index = new_index
    return result

class CqlIdentityVisitorTest(TestCase):
    def assertIdentity(self, query):
        input_query = parseString(query)
        result_query = CqlIdentityVisitor(input_query).visit()
        self.assertEquals(input_query, result_query)

        input_ids = set(id(n) for n in allnodes(input_query)) 
        result_ids = set(id(n) for n in allnodes(result_query))
        self.assertEquals(0, len(input_ids.intersection(result_ids)), 'Expected new ast to be a deepcopy.')

    def testIdentity(self):
        self.assertIdentity('query')
        self.assertIdentity('term and otherterm')
        self.assertIdentity('field = label')
        self.assertIdentity('(query)')
        self.assertIdentity('(one) and (two or three)')
        self.assertIdentity('(one) and (two = "three")')
        self.assertIdentity('one and two or three')
        self.assertIdentity('one or two and three')




