import pyarrow.parquet as pq
import pyarrow as pa

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

    def search(self, keywords: list[str]):
        indexes = []
        ids = self.table.column('id')
        for i, id_value in enumerate(ids):
            id_str = id_value.as_py()
            if any(keyword in id_str for keyword in keywords):
                indexes.append(i)

        result = []
        for i in indexes:
            id_value = ids[i]
            kind_value = self.table.column('kind')[i]
            start_line = self.table.column('start_line')[i]
            start_col = self.table.column('start_col')[i]
            end_line = self.table.column('end_line')[i]
            end_col = self.table.column('end_col')[i]
            result.append({
                'id': id_value.as_py(),
                'kind': kind_value.as_py(),
                'start_line': start_line.as_py(),
                'start_col': start_col.as_py(),
                'end_line': end_line.as_py(),
                'end_col': end_col.as_py()
            })
        return result



