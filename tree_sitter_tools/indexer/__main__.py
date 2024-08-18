from indexer.symbol_indexer import SymbolIndexer


indexer = SymbolIndexer.from_dir("./")
indexer.index()