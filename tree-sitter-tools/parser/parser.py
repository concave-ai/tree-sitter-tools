import time
from pathlib import Path

import tree_sitter_python as tspython
from tree_sitter import Language, Parser, Node
from pydantic import BaseModel

from parser.walker import PythonTreeWalker

PY_LANGUAGE = Language(tspython.language())
parser = Parser(PY_LANGUAGE)


class Symbol(BaseModel):
    id: str
    kind: str
    start: tuple[int, int] | None
    end: tuple[int, int] | None


class ParseResult(BaseModel):
    module_path: str
    relative_path: str
    time_used_ms: float
    symbols: list[Symbol]
    module_imports: list[str]


def parse_code(path: Path, module_path: str):
    start = time.time()
    content_raw = path.read_bytes()
    tree = parser.parse(content_raw)
    content_lines = content_raw.decode().split("\n")

    visitor = PythonTreeWalker(tree.root_node, content_lines, module_path)
    visitor.visit()

    return ParseResult(
        module_path=module_path,
        relative_path=str(path),
        time_used_ms=int((time.time() - start) * 1e6) / 1e3,
        symbols=visitor.symbols,
        module_imports=visitor.module_imports
    )
