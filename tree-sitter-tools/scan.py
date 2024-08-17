import os
from pathlib import Path

from parser.parser import parse_code


def is_python_package(path: Path):
    return (path / "__init__.py").exists()


class DirPackageScanner:
    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.packages = []
        self.files = []

    def add_file(self, namespace, path: Path):
        self.files.append({
            "name": f"{namespace}.{path.stem}",
            "path": path
        })

    def scan_python_files(self, path, namespace):
        for p in path.iterdir():
            if p.is_file() and p.suffix == ".py":
                self.add_file(namespace, p)
            elif p.is_dir():
                self.scan_python_files(p, f"{namespace}.{p.name}")

    def scan_python_package(self, path):
        namespace = path.name
        for p in path.iterdir():
            if p.is_file() and p.suffix == ".py":
                self.add_file(namespace, p)
            elif p.is_dir():
                self.scan_python_files(p, f"{namespace}.{p.name}")

    def scan_dir(self, dir_path: Path):
        for p in dir_path.iterdir():
            # if start doc or test, skip
            if p.name.startswith("doc") or p.name.startswith("test"):
                continue

            if p.is_dir():
                if is_python_package(p):
                    self.scan_python_package(p)
                else:
                    self.scan_dir(p)

    def scan(self):
        self.scan_dir(self.root_path)


if __name__ == "__main__":
    p = "/Users/justwph/labs/hackathons/2024/libs/django"
    scanner = DirPackageScanner(Path(p))
    scanner.scan()
    symbols = []
    total_time = 0
    func_count = 0
    class_count = 0
    var_count = 0

    for f in scanner.files:
        print(f"scanning {f['path']}")
        result = parse_code(f["path"], f["name"])
        symbols.extend(result.symbols)
        total_time += result.time_used_ms
        for s in result.symbols:
            if s.kind == "function":
                func_count += 1
            elif s.kind == "class":
                class_count += 1
            elif s.kind == "variable":
                var_count += 1

    print(f"scanned {len(scanner.files)} files")
    print("time used[ms]", total_time)
    print("symbols:", len(symbols))
    print("functions:", func_count)
    print("classes:", class_count)
    print("variables:", var_count)
