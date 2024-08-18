from tree_sitter_tools.indexer.symbol_indexer import SymbolIndexer


indexer = SymbolIndexer.from_dir("./")
indexer.index()