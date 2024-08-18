from typing import List

from tree_sitter import Node

from parser.base import Symbol


class ImportsMap:
    def __init__(self):
        self.map: dict[str, list[str]] = {}

    def add_import(self, module, names: list[str]):
        if module not in self.map:
            self.map[module] = []
        self.map[module].extend(names)

    def get_libs(self):
        return self.map.keys()


class Context:
    def __init__(self, node, namespace, imports: ImportsMap):
        self.node = node
        self.namespace = namespace
        self.imports = imports


class DecoratorContext:
    def __init__(self, node, namespace):
        self.node = node
        self.namespace = namespace


def check_node(node: Node, type: str):
    if node.type != type:
        raise AssertionError(f"Expect {type}, but got {node.type}. {node.start_point}-{node.end_point}")


def to_str(node: Node):
    return node.text.decode()


def nodes_filter(nodes: List[Node], type: str):
    return [i for i in nodes if i.type == type]


def get_imports(node: Node):
    imports_map = ImportsMap()
    for child in node.children:
        match child.type:
            case 'future_import_statement':
                names = [i.text.decode() for i in child.named_children]
                imports_map.add_import("__future__", names)

            case 'import_statement':
                names = [i.text.decode() for i in child.named_children]
                for i in names:
                    imports_map.add_import(i, ["*"])

            case 'import_from_statement':
                names = [i.text.decode() for i in child.named_children]
                check_node(child.children[0], "from")
                check_node(child.children[2], "import")
                imports_map.add_import(names[0], names[1:])

    return imports_map


class PythonTreeWalker:
    def __init__(self,
                 root_node: Node,
                 content_lines: List[str],
                 module_path: str,
                 code_path: str
                 ):
        self.root_node = root_node
        self.content_lines = content_lines
        self.module_path = module_path
        self.symbols = []
        self.module_imports = []
        self.code_path = code_path

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
        check_node(node.named_child(0), "identifier")

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
            if left.named_child(0).type == "identifier":
                name = node.children[0].children[0].text.decode()
                self.add_symbol("variable", f"{parent.namespace}.{name}")
            return
    #     todo: add more

    def add_symbol(self, kind, id, start=None, end=None):
        self.symbols.append(Symbol(
            kind=kind,
            id=id,
            start=start,
            end=end,
            file_path=self.code_path
        ))
