## begin license ##
#
# "CQLParser" is a parser that builds a parsetree for the given CQL and can convert this into other formats.
#
# Copyright (C) 2015 Seecr (Seek You Too B.V.) http://seecr.nl
# Copyright (C) 2015 Stichting Kennisnet http://www.kennisnet.nl
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

    def isNested(self):
        return self.operator is not None

    def isSearchterm(self):
        return not self.isNested()

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

    def iter(self):
        yield self
        if self.operator:
            for operand in self.operands:
                for f in operand.iter():
                    yield f

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

    def replaceWith(self, expression):
        for k in self.__dict__.keys():
            delattr(self, k)
        for k,v in expression.__dict__.items():
            setattr(self, k, v)

