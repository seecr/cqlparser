## begin license ##
#
# "CQLParser" is a parser that builds a parsetree for the given CQL and can convert this into other formats.
#
# Copyright (C) 2015, 2020-2021 Seecr (Seek You Too B.V.) https://seecr.nl
# Copyright (C) 2015, 2021 Stichting Kennisnet https://www.kennisnet.nl
# Copyright (C) 2021 Data Archiving and Network Services https://dans.knaw.nl
# Copyright (C) 2021 SURF https://www.surf.nl
# Copyright (C) 2021 The Netherlands Institute for Sound and Vision https://beeldengeluid.nl
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

from .cqlvisitor import CqlVisitor
from .cqlparser import parseString as parseCql
from ._queryexpression import QueryExpression

def cqlToExpression(cql):
    if isinstance(cql, QueryExpression):
        return cql
    if not hasattr(cql, 'accept'):
        cql = parseCql(cql)
    return CqlToExpressionVisitor(cql).visit()

class CqlToExpressionVisitor(CqlVisitor):
    def visitCQL_QUERY(self, node):
        return CqlVisitor.visitCQL_QUERY(self, node)[0]

    def visitSCOPED_CLAUSE(self, node):
        clause = CqlVisitor.visitSCOPED_CLAUSE(self, node)
        if len(clause) == 1:
            return clause[0]
        lhs, operator, rhs = clause
        if operator == 'NOT':
            operator = 'AND'
            rhs.must_not = True
        result = QueryExpression.nested(operator)
        for hs in [lhs, rhs]:
            if hs.operator == operator and not hs.must_not:
                result.operands.extend(hs.operands)
            else:
                result.operands.append(hs)
        return result

    def visitSEARCH_CLAUSE(self, node):
        firstChild = node.children[0].name
        results = CqlVisitor.visitSEARCH_CLAUSE(self, node)
        if firstChild == 'SEARCH_TERM':
            return QueryExpression.searchterm(term=results[0])
        elif firstChild == 'INDEX':
            #INDEX(TERM('term')), RELATION(COMPARITOR('comparitor')), SEARCH_TERM(TERM('term'))
            index, (relation, boost), term = results
            result = QueryExpression.searchterm(
                index=index,
                relation=relation,
                term=term,
                boost=boost,
            )
            return result
        return results[0]

    def visitRELATION(self, node):
        results = CqlVisitor.visitRELATION(self, node)
        if len(results) == 1:
            relation = results[0]
            boost = None
        else:
            (relation, (modifier, comparitor, value)) = results
            boost = float(value)
        return relation, boost
