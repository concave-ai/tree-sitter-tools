import os
from pathlib import Path

from pydantic import BaseModel

from tree_sitter_tools.parser.parser import parse_code


def is_python_package(path: Path):
    return (path / "__init__.py").exists()


class ModuleFile(BaseModel):
    name: str
    path: str


class DirPackageScanner:
    def __init__(self, work_path: Path):
        self.work_path = work_path
        self.packages = []
        self.files: list[ModuleFile] = []

    def add_file(self, namespace, path: Path):
        relative_path = path.relative_to(self.work_path)
        self.files.append(ModuleFile(name=namespace, path=str(relative_path)))

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
                self.add_file(f"{namespace}.{p.stem}", p)
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
        self.scan_dir(self.work_path)
