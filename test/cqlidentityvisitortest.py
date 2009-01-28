
from unittest import TestCase

from cqlparser import CqlIdentityVisitor
from cqlparser import parseString

class CqlIdentityVisitorTest(TestCase):
    def assertIdentity(self, query):
        self.assertEquals(parseString(query), CqlIdentityVisitor(parseString(query)).visit())

    def testIdentity(self):
        self.assertIdentity('query')
        self.assertIdentity('term and otherterm')
        self.assertIdentity('field = label')
        self.assertIdentity('(query)')
        self.assertIdentity('(one) and (two or three)')
        self.assertIdentity('(one) and (two = "three")')

#CQL_QUERY(SCOPED_CLAUSE(SEARCH_CLAUSE('(', CQL_QUERY(SCOPED_CLAUSE(SEARCH_CLAUSE(SEARCH_TERM(TERM('query'))))), ')'))) !=
#CQL_QUERY(SCOPED_CLAUSE(             ('(', CQL_QUERY(SCOPED_CLAUSE(SEARCH_CLAUSE(SEARCH_TERM(TERM('query'))))), ')')))