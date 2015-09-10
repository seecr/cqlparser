## begin license ##
#
# "Edurep" is a service for searching in educational repositories.
# "Edurep" is developed for Stichting Kennisnet (http://www.kennisnet.nl) by
# Seek You Too (http://www.cq2.nl). The project is based on the opensource
# project Meresco (http://www.meresco.com).
#
# Copyright (C) 2015 Seecr (Seek You Too B.V.) http://seecr.nl
# Copyright (C) 2015 Stichting Kennisnet http://www.kennisnet.nl
#
# This file is part of "Edurep"
#
# "Edurep" is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# "Edurep" is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with "Edurep"; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
## end license ##

from cqlvisitor import CqlVisitor
from cqlparser import parseString as parseCql
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
