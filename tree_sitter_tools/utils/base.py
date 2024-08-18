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
        raise AssertionError(f"Expect {type}, but got {node.type}")


def to_str(node: Node):
    return node.text.decode()


def nodes_filter(nodes: List[Node], type: str):
    return [i for i in nodes if i.type == type]

