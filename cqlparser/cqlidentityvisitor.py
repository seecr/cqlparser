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

class CqlIdentityVisitor(CqlVisitor):
    def visitChildren(self, node):
        return node.__class__(*CqlVisitor.visitChildren(self, node))

    def visitSEARCH_TERM(self, node):
        assert len(node.children()) == 1
        return self.visitChildren(node)

    def visitSEARCH_CLAUSE(self, node):
        if len(node.children()) == 3 and node.children()[0] == "(":
            return node.__class__("(", node.children()[1].accept(self), ")")
        return self.visitChildren(node)

    # terminals
    
    def visitCOMPARITOR(self, node):
        assert len(node.children()) == 1
        return node

    def visitBOOLEAN(self, node):
        assert len(node.children()) == 1
        return node
    
    def visitTERM(self, node):
        return node