
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