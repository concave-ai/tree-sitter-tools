from pydantic import BaseModel


class Symbol(BaseModel):
    id: str
    kind: str
    file_path: str
    range: list[int]


class ParseResult(BaseModel):
    module_path: str
    relative_path: str
    time_used_ms: float
    symbols: list[Symbol]
    module_imports: list[str]

