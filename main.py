from indexer.symbol_indexer import SymbolIndexer
from searcher.searcher import SymbolSearcher

# SymbolIndexer.from_dir("/Users/justwph/labs/hackathons/2024/libs/django").index()

tokens = SymbolSearcher("symbol_index.parquet").tokens()
for i in tokens:
    print(i)