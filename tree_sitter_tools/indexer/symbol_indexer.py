from pathlib import Path

import pyarrow.parquet as pq
import pyarrow as pa
import time

from tree_sitter_tools.indexer.scan import ModuleFile, DirPackageScanner
from tree_sitter_tools.parser.base import Symbol
from tree_sitter_tools.parser.parser import parse_code

def symbol_to_dict(symbol: Symbol):

    return {
        "id": symbol.id,
        "kind": symbol.kind,
        "file_path": symbol.file_path,
        "range": symbol.range
    }




class SymbolIndexer:
    def __init__(self, files: list[ModuleFile], work_path):
        self.work_path = work_path
        self.files = files
        self.symbols: list[Symbol] = []
        self.time_used = 0

    @classmethod
    def from_dir(cls, dir_path):
        scanner = DirPackageScanner(Path(dir_path))
        scanner.scan()
        return cls(scanner.files, dir_path)

    def index(self):
        total = len(self.files)
        cnt = 0
        for file in self.files:
            cnt += 1
            if cnt % 30 == 0:
                print(f"Indexing {cnt}/{total}: {file.name}")
            result = parse_code(file.path, file.name, self.work_path)
            self.symbols.extend(result.symbols)
            self.time_used += result.time_used_ms

        print(f"parsed done, used: {self.time_used}ms")
        print(f"found {len(self.symbols)} symbols")

        start = time.time()
        _symbols = [symbol_to_dict(s) for s in self.symbols]
        table = pa.Table.from_pylist(_symbols,
                                     schema=pa.schema([
                                         pa.field('id', pa.string()),
                                         pa.field('kind', pa.dictionary(pa.int16(), pa.string())),
                                         pa.field('range', pa.list_(pa.int32(), 6)),
                                         pa.field('file_path', pa.dictionary(pa.int16(), pa.string())),
                                     ]))

        pq.write_table(table, 'symbol_index.parquet',
                       compression='snappy',
                       use_dictionary=True,
                       )


        print(f"writing done, used: {(time.time() - start)*1e3}ms")
        print(f"Indexing done.")
