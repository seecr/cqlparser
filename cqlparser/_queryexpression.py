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

from .cql2string import quottableTermChars


class QueryExpression(object):
    def __init__(self, **kwargs):
        self.operator = None
        self.relation_boost = None
        self.must_not = False
        for k,v in kwargs.items():
            setattr(self, k, v)

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

    def __eq__(self, other):
        return isinstance(other, QueryExpression) and self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self.__eq__(other)

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
            for operand in self.operands[:]:
                for f in operand.iter():
                    yield f

    def replaceWith(self, expression):
        for k in list(self.__dict__.keys()):
            delattr(self, k)
        for k,v in expression.__dict__.items():
            setattr(self, k, v)

    def toString(self, pretty_print=True):
        return ''.join(self._str(indent=0 if pretty_print else None))

    def __str__(self):
        return ''.join(self._str())

    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__, ', '.join("%s=%s" % (key, repr(value)) for key, value in sorted(self.__dict__.items())))

    def _str(self, indent=None):
        if self.must_not:
            yield '!'
        if self.operator:
            yield self.operator
            if indent is None:
                yield '['
                commaRepl = ', '
            else:
                commaRepl = '\n'
                yield '\n'
                indent += 1
            comma = ''
            for operand in self.operands:
                yield comma
                yield ' ' * 4 * (indent or 0)
                comma = commaRepl
                yield ''.join(operand._str(indent))
            if indent is None:
                yield ']'
            else:
                indent -= 1
        else:
            term = self.term
            if quottableTermChars.search(term):
                term = '"%s"' % term.replace(r'"', r'\"')
            yield repr(' '.join(r for r in [self.index, self.relation, term] if r))
