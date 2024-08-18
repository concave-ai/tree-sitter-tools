from indexer.symbol_indexer import SymbolIndexer
from searcher.searcher import SymbolSearcher

# SymbolIndexer.from_dir("/Users/justwph/labs/hackathons/2024/libs/django").index()
searcher = SymbolSearcher("symbol_index.parquet")


results = searcher.search(["AddConstraintNotValid"])
for r in results:
    print(r)
