#!/usr/bin/env python3
"""
Check for missing Python imports in the current directory.
Used by llm_code_gate.sh Layer 1 structural checks.

Usage: python3 check_python_imports.py [stdlib_module ...]
"""

import ast
import sys
from pathlib import Path


def check_imports(stdlib_modules):
    stdlib = set(stdlib_modules)
    errors = []

    for path in Path(".").rglob("*.py"):
        path_str = str(path)
        if any(skip in path_str for skip in [".venv", "__pycache__", "site-packages"]):
            continue
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        mod = alias.name.split(".")[0]
                        if mod in stdlib:
                            continue
                        if not Path(f"{mod}.py").exists() and not Path(mod).is_dir():
                            errors.append(f"{path}: import {mod}")
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        mod = node.module.split(".")[0]
                        if mod in stdlib:
                            continue
                        if not Path(f"{mod}.py").exists() and not Path(mod).is_dir():
                            errors.append(f"{path}: from {mod}")
        except SyntaxError as e:
            errors.append(f"{path}: SYNTAX ERROR: {e}")
        except Exception as e:
            errors.append(f"{path}: PARSE ERROR: {e}")

    for e in errors[:10]:
        print(e)


if __name__ == "__main__":
    stdlib_modules = sys.argv[1:]
    check_imports(stdlib_modules)
