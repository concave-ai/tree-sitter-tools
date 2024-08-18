from parser.parser import ParseResult


def print_result(result: ParseResult):
    print(f"Module: {result.module_path}")
    print(f"Path: {result.relative_path}")
    print(f"Time used: {result.time_used_ms}ms")

    print("======== Imports =========")
    for i in result.module_imports:
        print(f"- {i}")

    print("======== Symbols =========")
    for s in result.symbols:
        name = s.id[len(result.module_path) + 1:] if s.id.startswith(result.module_path) else s.id
        print(f"- {s.kind.upper().ljust(10, " ")} :{name} ")


# auto remove all line indent (size=start_col)
def block_lines_between(start_line, start_col, end_line, end_col, lines):
    if start_line == end_line:
        return lines[start_line][start_col:end_col]
    else:
        results = []
        for i in range(start_line, end_line + 1):
            line = lines[i]
            results.append(line)
        return "".join(results)


def print_code_block(result: ParseResult):
    with open(result.relative_path, "r") as f:
        lines = f.readlines()

    for s in result.symbols:
        if s.kind in ["function"]:
            print(f"=========={s.kind}: {s.id} ===============")
            print()
            code = block_lines_between(s.start[0], s.start[1], s.end[0], s.end[1], lines)
            print(code)
            print()
