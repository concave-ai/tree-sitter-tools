
import tree_sitter_python as tspython
from tree_sitter import Language, Parser, Node

PY_LANGUAGE = Language(tspython.language())
parser = Parser(PY_LANGUAGE)


code = """
a.b[1].c.result, b = 1 < x <= 100, 234<1000
"""

tree = parser.parse(bytes(code, "utf-8"))

# print(tree.root_node.child(0))
for i in tree.root_node.child(0).children:
    print(i)
