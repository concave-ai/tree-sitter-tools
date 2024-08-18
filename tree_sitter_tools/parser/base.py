from pydantic import BaseModel


class Symbol(BaseModel):
    id: str
    kind: str
    start: tuple[int, int] | None
    end: tuple[int, int] | None
    file_path: str


class ParseResult(BaseModel):
    module_path: str
    relative_path: str
    time_used_ms: float
    symbols: list[Symbol]
    module_imports: list[str]

