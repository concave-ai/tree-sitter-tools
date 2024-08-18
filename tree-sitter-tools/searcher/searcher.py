import pyarrow.parquet as pq


class SymbolSearcher:
    def __init__(self, index_path):
        self.table = pq.read_table(index_path)

    def tokens(self):
        tokens = set()
        ids = self.table.column('id')
        for i in ids:
            parts = i.as_py().split('.')
            tokens.update(parts)
        return tokens


