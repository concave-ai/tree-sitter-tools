import logging
from typing import List

from pydantic import BaseModel
from tree_sitter import Node

from parser.walker import get_imports
from utils.base import ImportsMap, check_node, Context


class Occurrence(BaseModel):
    id: str
    name: str
    kind: str


class Visitor:
    def __init__(self, node, namespace, imports: ImportsMap):
        self.node = node
        self.namespace = namespace
        self.imports = imports
        self.symbols = {

        }
        self.occurrences = []

    def visit(self, node):
        pass

    def extend_occurrences(self, occurrences: List[Occurrence]):
        self.occurrences.extend(occurrences)


#  _simple_statement: $ => choice(
#       $.future_import_statement,
#       $.import_statement,
#       $.import_from_statement,
#       $.print_statement,
#       $.assert_statement,
#       $.expression_statement,
#       $.return_statement,
#       $.delete_statement,
#       $.raise_statement,
#       $.pass_statement,
#       $.break_statement,
#       $.continue_statement,
#       $.global_statement,
#       $.nonlocal_statement,
#       $.exec_statement,
#       $.type_alias_statement,
#     ),


#  _compound_statement
#       $.if_statement,
#       $.for_statement,
#       $.while_statement,
#       $.try_statement,
#       $.with_statement,
#       $.function_definition,
#       $.class_definition,
#       $.decorated_definition,
#       $.match_statement,

IGNORE_STATEMENTS = [
    'print_statement',
    'assert_statement',
    'return_statement',
    'delete_statement',
    'raise_statement',
    'pass_statement',
    'break_statement',
    'continue_statement',
    'global_statement',
    'nonlocal_statement',
    'exec_statement',
    'type_alias_statement',
]
TODO_STATEMENTS = [
]


# case 'future_import_statement':
#                 names = [i.text.decode() for i in child.named_children]
#                 imports_map.add_import("__future__", names)
#
#             case 'import_statement':
#                 names = [i.text.decode() for i in child.named_children]
#                 for i in names:
#                     imports_map.add_import(i, ["*"])
#
#             case 'import_from_statement':
#                 names = [i.text.decode() for i in child.named_children]
#                 check_node(child.children[0], "from")
#                 check_node(child.children[2], "import")
#                 imports_map.add_import(names[0], names[1:])
def get_future_imports_statement(node):
    check_node(node, "future_import_statement")
    names = [i.text.decode() for i in node.named_children]
    return [
        Occurrence(
            id=f"__future__.{i}",
            name=i,
            kind="ReadAccess",
        )
        for i in names
    ]


def get_imports_statement(node):
    names = [i.text.decode() for i in node.named_children]
    return [
        Occurrence(
            id=f"{i}.__init__",
            name=i,
            kind="ReadAccess",
        )
        for i in names
    ]


def get_import_from_statement(node):
    names = [i.text.decode() for i in node.named_children]
    lib_name = names[0]
    return [
        Occurrence(
            id=f"{lib_name}.{i}",
            name=i,
            kind="ReadAccess",
        )
        for i in names[1:]
    ]


def get_expression_statement(node: Node):
    child = node.children[0]
    match child.type:
        case 'assignment':
            name = child.child(0).text.decode()
            return [
                Occurrence(
                    id=f"{name}",
                    name=name,
                    kind="WriteAccess",
                )
            ]
        case 'augmented_assignment':
            name = child.child(0).text.decode()
            return [
                Occurrence(
                    id=f"{name}",
                    name=name,
                    kind="ReadAccess",
                )
            ]
        case _:
            logging.debug(f"Unsupported expression statement: {child.type}")
            return []


class BlockVisitor(Visitor):

    def visit(self, node):
        for child in node.children:
            if child.type in IGNORE_STATEMENTS:
                continue
            match child.type:
                case 'future_import_statement':
                    self.extend_occurrences(get_future_imports_statement(child))
                case 'import_statement':
                    self.extend_occurrences(get_future_imports_statement(child))
                case 'import_from_statement':
                    self.extend_occurrences(get_future_imports_statement(child))

                case 'print_statement':
                    # todo
                    pass
                case 'assert_statement':
                    # todo
                    pass

                # case 'expression_statement':

                case _:
                    logging.debug(f"Unsupported statement: {child.type}")


class PythonTreeWalker:
    def __init__(self,
                 root_node: Node,
                 content_lines: List[str],
                 module_path: str,
                 ):
        self.root_node = root_node
        self.content_lines = content_lines
        self.module_path = module_path
        self.symbols = []
        self.module_imports = []

    def visit(self):
        assert self.root_node.type == 'module'
        imports = get_imports(self.root_node)
        parent = Context(self.root_node, self.module_path, imports)
        parent.namespace = self.module_path

        self.module_imports = parent.imports.get_libs()
        self.visit_block(self.root_node, parent)

    # https://github.com/tree-sitter/tree-sitter-python/blob/master/grammar.js#L531

    def visit_decorated_definition(self, node: Node, parent: Context):
        check_node(node, "decorated_definition")

        last_child = node.children[-1]
        match last_child.type:
            case 'function_definition':
                self.visit_function_definition(last_child, parent)
            case 'class_definition':
                self.visit_class_definition(last_child, parent)
            case _:
                raise AssertionError(f"Unsupported decorated definition: {last_child.type}")

    def visit_block(self, node: Node, parent: Context):
        for child in node.children:
            match child.type:
                case 'function_definition':
                    self.visit_function_definition(child, parent)
                case 'class_definition':
                    self.visit_class_definition(child, parent)
                case 'expression_statement':
                    self.visit_expression_statement(child, parent)
                case 'decorated_definition':
                    self.visit_decorated_definition(child, parent)

    # if have decorator, will set start_point
    def visit_function_definition(self, node: Node, parent: Context, start_point=None):

        check_node(node, "function_definition")
        check_node(node.children[0], "def")
        check_node(node.children[1], "identifier")

        func_name = node.children[1].text.decode()
        ctx = Context(node, f"{parent.namespace}.{func_name}", parent.imports)
        self.add_symbol("function",
                        ctx.namespace,
                        node.start_point if start_point is None else start_point,
                        node.end_point,
                        )
        self.visit_block(node, ctx)

    # https://github.com/tree-sitter/tree-sitter-python/blob/master/grammar.js#L472
    # if have decorator, will set start_point
    def visit_class_definition(self, node: Node, parent: Context, start_point=None):
        check_node(node, "class_definition")
        check_node(node.children[0], "class")
        check_node(node.children[1], "identifier")
        check_node(node.children[-1], "block")

        class_name = node.children[1].text.decode()
        ctx = Context(node, f"{parent.namespace}.{class_name}", parent.imports)
        self.add_symbol("class",
                        ctx.namespace,
                        node.start_point if start_point is None else start_point,
                        node.end_point,
                        )
        self.visit_block(node.children[-1], ctx)

    # https://github.com/tree-sitter/tree-sitter-python/blob/master/grammar.js#L217
    def visit_expression_statement(self, node: Node, parent: Context):
        check_node(node, "expression_statement")
        left = node.children[0]

        if left.type == "assignment":
            check_node(node.children[0].children[0], "identifier")
            name = node.children[0].children[0].text.decode()
            self.add_symbol("const", f"{parent.namespace}.{name}")
            return

    def add_symbol(self, kind, id, start=None, end=None):
        self.symbols.append({
            "kind": kind,
            "id": id,
            "start": start,
            "end": end,
        })
