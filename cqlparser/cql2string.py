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

from cqlvisitor import CqlVisitor

from re import compile
quottableTermChars = compile(r'[\"\(\)\>\=\<\/\s]')

class Cql2StringVisitor(CqlVisitor):
    def visitSEARCH_CLAUSE(self, node):
        children = self.visitChildren(node)
        return ''.join(children)

    def visitMODIFIER(self, node):
        children = self.visitChildren(node)
        return '/'+''.join(children)

    def visitRELATION(self, node):
        children = self.visitChildren(node)
        result = ''.join(children)
        if result == '=':
            return result
        return ' %s ' % result

    def visitCQL_QUERY(self, node):
        return '(%s)' % self._joinChildren(node)

    def visitTERM(self, node):
        term = CqlVisitor.visitTERM(self, node)
        if quottableTermChars.search(term):
            return '"%s"' % term.replace(r'"', r'\"')
        return term

    def _joinChildren(self, node):
        children = self.visitChildren(node)
        return ' '.join(children)

    visitSEARCH_TERM = _joinChildren
    visitSCOPED_CLAUSE = _joinChildren
    visitINDEX = _joinChildren
    visitMODIFIERLIST = _joinChildren
    
def cql2string(ast):
    return Cql2StringVisitor(ast).visit()[1:-1]