## begin license ##
#
#    CQLParser is a parser that builds a parsetree for the given CQL and
#    can convert this into other formats.
#    Copyright (C) 2005-2011 Seek You Too (CQ2) http://www.cq2.nl
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

class CqlVisitor(object):
    def __init__(self, root):
        self._root = root

    def visit(self):
        return self._root.accept(self)

    def visitCQL_QUERY(self, node):
        return node.visitChildren(self)

    def visitSCOPED_CLAUSE(self, node):
        return node.visitChildren(self)

    def visitSEARCH_CLAUSE(self, node):
        return node.visitChildren(self)

    def visitRELATION(self, node):
        return node.visitChildren(self)

    def visitMODIFIERLIST(self, node):
        return node.children[0].accept(self)

    def visitMODIFIER(self, node):
        return node.visitChildren(self)

    # TERMINALS
    def visitINDEX(self, node):
        return node.children[0].accept(self)

    def visitCOMPARITOR(self, node):
        return node.children[0]

    def visitBOOLEAN(self, node):
        return node.children[0].upper()

    def visitSEARCH_TERM(self, node):
        return node.children[0].accept(self)

    def visitTERM(self, node):
        return node.children[0]
