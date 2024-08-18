
class BlockVisitor():
    def __init__(self, node):
        self.node = node

    def visit(self, visitor):
        visitor.visit(self.node)
        for child in self.node.children:
            visitor.visit(child)