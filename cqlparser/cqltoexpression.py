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

class QueryExpression(object):
    def __init__(self, **kwargs):
        self.operator = None
        self.relation_boost = None
        self.must_not = False
        for k,v in kwargs.items():
            setattr(self, k, v)

    def __repr__(self):
        return 'QueryExpression(' + ', '.join(sorted('%s=%s'%(k,repr(v)) for k, v in self.__dict__.items() if not k.startswith('_'))) +')'

    def __eq__(self, other):
        return isinstance(other, QueryExpression) and self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self.__eq__(other)

    @classmethod
    def nested(cls, operator):
        return cls(operator=operator, operands=[])

    @classmethod
    def searchterm(cls, index=None, relation=None, term=None, boost=None):
        result = cls(index=index, relation=relation, term=term)
        if boost is not None:
            result.relation_boost = boost
        return result

    def asDict(self):
        result = {}
        for k, v in self.__dict__.items():
            if k == 'operands':
                result['operands'] = [expr.asDict() for expr in v]
            else:
                result[k] = v
        return result

    @classmethod
    def fromDict(cls, aDict):
        operands = aDict.pop('operands', None)
        result = cls(**aDict)
        if operands:
            result.operands = [cls.fromDict(o) for o in operands]
        return result

    def _toString(self, indent=0):
        operator = getattr(self, 'operator', None)
        if operator:
            yield "{0}{1}{2}".format(' '*indent,
                    '!' if getattr(self, 'must_not', False) else '',
                    operator)
            for operand in self.operands:
                yield '\n'.join(operand._toString(indent+4))
        else:
            yield "{0}{1}{2}{3}{4}".format(
                    ' '*indent,
                    '!' if getattr(self, 'must_not', False) else '',
                    self.index or '',
                    ' {0} '.format(self.relation) if self.relation else '',
                    self.term,
                )

    def toString(self, pretty_print=True):
        return '\n'.join(self._toString(indent=0))
