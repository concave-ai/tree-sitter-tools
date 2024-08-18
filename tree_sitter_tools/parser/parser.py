import os.path
import time

import tree_sitter_python as tspython
from tree_sitter import Language, Parser, Node

from tree_sitter_tools.parser.base import ParseResult
from tree_sitter_tools.parser.walker import PythonTreeWalker

PY_LANGUAGE = Language(tspython.language())
parser = Parser(PY_LANGUAGE)


def parse_code(relative_path: str, module_path: str, work_path: str):
    start = time.time()
    with open(os.path.join(work_path, relative_path), "rb") as f:
        content_raw = f.read()
    tree = parser.parse(content_raw)
    content_lines = content_raw.decode().split("\n")

    visitor = PythonTreeWalker(tree.root_node, content_lines, module_path, relative_path)
    visitor.visit()

    return ParseResult(
        module_path=module_path,
        relative_path=relative_path,
        time_used_ms=int((time.time() - start) * 1e6) / 1e3,
        symbols=visitor.symbols,
        module_imports=visitor.module_imports
    )
