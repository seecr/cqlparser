## begin license ##
#
#    CQLParser is a parser that builds a parsetree for the given CQL and
#    can convert this into other formats.
#    Copyright (C) 2005-2009 Seek You Too (CQ2) http://www.cq2.nl
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
from cqlparser import parseString, CQL_QUERY, SCOPED_CLAUSE, SEARCH_CLAUSE, BOOLEAN, SEARCH_TERM, INDEX, RELATION, COMPARITOR, TERM, UnsupportedCQL, CQLParseException

class ParseException(Exception):
    pass

# REWRITE using CqlVisitor (left as an exercise to ther reader ;-)
def compose(node):
    if node.__class__ in [INDEX]:
        assert len(node.children()) == 1
        return compose(node.children()[0])
    if node.__class__ in [SCOPED_CLAUSE, SEARCH_TERM, CQL_QUERY]:
        return " ".join(map(compose, node.children()))
    if node.__class__ == SEARCH_CLAUSE:
        return "".join(map(compose, node.children()))
    if node.__class__ == RELATION:
        assert len(node.children()) == 1
        return compose(node.children()[0])
    if node.__class__ == COMPARITOR:
        assert len(node.children()) == 1
        return node.children()[0]
    if node.__class__ == BOOLEAN:
        assert len(node.children()) == 1
        return node.children()[0]
    if node.__class__ == TERM:
        return node.children()[0]
    return str(node)

def fromString(aCQLString):
    if aCQLString.strip() == '':
        return ''
    try:
        abstractSyntaxTree = parseString(aCQLString)
    except UnsupportedCQL, e:
        raise ParseException('Unsupported query')
    except CQLParseException, e:
        raise ParseException('Unsupported query')

    return compose(abstractSyntaxTree)
