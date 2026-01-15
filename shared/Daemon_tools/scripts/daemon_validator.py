"""
Daemon Validator
================

This script inspects a collection of daemon scripts for common pitfalls and
potential safety issues. It uses Python's abstract syntax tree (AST) module
and simple regular‑expression scans to perform static analysis on each file
without executing any of the daemon code. The goal is to surface areas
that may require refactoring or additional safeguards before these daemons
are run in production.

Usage
-----
Execute the script with Python and pass one or more root directories to
scan.  The validator will recursively search those directories for files
matching a known list of daemon names (case‑insensitive) and analyse
each file found.  Any daemons not located will be reported as missing.

Example::

    python daemon_validator.py /path/to/eden/daemons /other/path

If no directories are supplied, the current working directory will be
scanned by default.

The script prints a summary table to standard output, detailing which
issues were detected for each daemon, or indicating that the file was
not found.  You can customise the list of daemon names at the top of
this file.
"""

import ast
import os
import re
import sys
from typing import Dict, List, Tuple


###############################################################################
# Configuration
###############################################################################

# List of daemon names to check.  Update this list if you add or remove
# daemons in your Eden setup.  Names are matched to filenames with a
# ``.py`` extension, case‑insensitively.
DAEMONS = [
    "Cassandra", "Serideth", "Runlet", "Archivus", "Boudica", "Moodweaver",
    "Snatch", "Ashera", "Jinxie", "Patty Mae", "Riven", "Codexa", "Aderyn",
    "Rhea", "Toto", "Quill", "Archive", "Moodmancer", "Juno Jr", "Keyla",
    "Ledger Jr", "Rook", "Parsley", "Sheele", "Briar", "Solie", "Handel",
    "Sothis", "AshFall", "Dagr", "Rogers", "Muse Jr", "Cradle", "Maribel",
    "Threadstep", "Scribevein", "Dove", "Prismari", "Sylvia", "Label",
    "Nott", "Glimmer", "Mythra", "Siglune", "Serios", "Somni", "Glypha",
    "Sybbie", "Eden Restore", "Saphira", "Tiki", "Aethercore", "Everett",
    "Harper", "Savvy", "WeaverArcTracker", "Bellwrit", "Porta", "Alfie",
    "Scorchick", "Tempest", "Lyss", "eden memory", "Nancy", "EdenShield",
    "Eden AI", "Olyssia", "Markbearer", "Audrey", "Janvier", "Whisperfang",
    "Koko", "EdenKernel", "Hunter", "Astrid", "Mist", "Emberly", "Kinsley",
    "Lexos", "RitualGUI", "ScriptOne", "Scriptum", "Luke", "Filigree",
    "Tempo", "John", "Stewart", "Yune", "EdenCore"
]

# Patterns to scan for with simple regular expressions.  Each entry maps
# a human‑readable issue name to a compiled pattern.  Matches will be
# counted rather than highlighted individually to keep output concise.
REGEX_PATTERNS = {
    "hardcoded_secret": re.compile(r"(?i)(api[_-]?key|token|secret|password)\s*=\s*[\'\"]\S{8,}[\'\"]"),
    "infinite_loop": re.compile(r"while\s+True\b"),
    "mutable_default": re.compile(r"def\s+\w+\([^)]*=\s*(\[\]|\{\})"),
    "file_io_unsafe": re.compile(r"\b(open|write)\s*\(\s*[\'\"]"),
    "eval_exec": re.compile(r"\b(eval|exec)\s*\(")
}


###############################################################################
# Helper functions
###############################################################################

def find_daemon_file(root_dirs: List[str], daemon_name: str) -> str:
    """Locate the source file for a daemon.

    Searches recursively under the provided root directories for a file
    matching the daemon's name with a ``.py`` extension.  The search is
    case‑insensitive and returns the first match found.

    Parameters
    ----------
    root_dirs : List[str]
        Directories to search in.
    daemon_name : str
        Name of the daemon (without extension).

    Returns
    -------
    str
        Path to the daemon's Python file, or an empty string if not found.
    """
    target = f"{daemon_name}.py".lower()
    for root in root_dirs:
        for dirpath, _, filenames in os.walk(root):
            for filename in filenames:
                if filename.lower() == target:
                    return os.path.join(dirpath, filename)
    return ""


def analyze_ast(file_path: str) -> Dict[str, int]:
    """Perform AST‑based checks on the given Python file.

    The function counts occurrences of undefined variables and unused imports
    using a simple scope tracking mechanism.  This helps identify potential
    bugs where names are referenced before being defined or imported but
    never used.

    Parameters
    ----------
    file_path : str
        Path to the Python source file.

    Returns
    -------
    Dict[str, int]
        Counts of issues keyed by ``'undefined_var'`` and ``'unused_import'``.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            source = f.read()
        tree = ast.parse(source, filename=file_path)
    except SyntaxError:
        # If the file cannot be parsed, skip AST checks
        return {"undefined_var": -1, "unused_import": -1}
    except Exception:
        return {"undefined_var": -1, "unused_import": -1}

    undefined_count = 0
    unused_count = 0

    # Track defined names in nested scopes
    scopes: List[set] = [set()]

    def push_scope() -> None:
        scopes.append(set())

    def pop_scope() -> None:
        if len(scopes) > 1:
            scopes.pop()

    def define(name: str) -> None:
        scopes[-1].add(name)

    def is_defined(name: str) -> bool:
        for scope in reversed(scopes):
            if name in scope:
                return True
        return name in dir(__builtins__)

    # Collect imports and usage for unused import detection
    imported_names: Dict[str, int] = {}
    used_names: set = set()

    class Analyzer(ast.NodeVisitor):
        def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
            define(node.name)
            push_scope()
            for arg in node.args.args:
                define(arg.arg)
            self.generic_visit(node)
            pop_scope()

        def visit_ClassDef(self, node: ast.ClassDef) -> None:
            define(node.name)
            push_scope()
            self.generic_visit(node)
            pop_scope()

        def visit_For(self, node: ast.For) -> None:
            if isinstance(node.target, ast.Name):
                define(node.target.id)
            self.generic_visit(node)

        def visit_With(self, node: ast.With) -> None:
            for item in node.items:
                if item.optional_vars and isinstance(item.optional_vars, ast.Name):
                    define(item.optional_vars.id)
            self.generic_visit(node)

        def visit_Assign(self, node: ast.Assign) -> None:
            for target in node.targets:
                if isinstance(target, ast.Name):
                    define(target.id)
            self.generic_visit(node)

        def visit_Import(self, node: ast.Import) -> None:
            for alias in node.names:
                name = alias.asname if alias.asname else alias.name.split(".")[0]
                imported_names[name] = node.lineno
                define(name)

        def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
            for alias in node.names:
                if alias.name != "*":
                    name = alias.asname if alias.asname else alias.name
                    imported_names[name] = node.lineno
                    define(name)

        def visit_Name(self, node: ast.Name) -> None:
            if isinstance(node.ctx, ast.Load):
                used_names.add(node.id)
                if not is_defined(node.id):
                    nonlocal undefined_count
                    undefined_count += 1
            self.generic_visit(node)

        def visit_Attribute(self, node: ast.Attribute) -> None:
            if isinstance(node.value, ast.Name):
                used_names.add(node.value.id)
            self.generic_visit(node)

    Analyzer().visit(tree)

    # Count unused imports
    for name in imported_names:
        if name not in used_names and not name.startswith("_"):
            unused_count += 1

    return {
        "undefined_var": undefined_count,
        "unused_import": unused_count,
    }


def scan_file(file_path: str) -> Dict[str, int]:
    """Perform regex and AST scans on a Python file.

    Returns a dictionary mapping issue names to the number of occurrences
    detected.  A value of ``-1`` indicates the file could not be parsed
    for that particular check (e.g., due to a syntax error).
    """
    results: Dict[str, int] = {name: 0 for name in REGEX_PATTERNS}
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            code = f.read()
    except Exception:
        # If the file can't be read, return errors indicated by -1
        for key in results:
            results[key] = -1
        return results

    # Regex scans
    for issue_name, pattern in REGEX_PATTERNS.items():
        results[issue_name] = len(pattern.findall(code))

    # AST‑based scans
    ast_results = analyze_ast(file_path)
    # Combine AST results into the final dictionary
    results.update(ast_results)
    return results


def format_report(data: Dict[str, Dict[str, int]]) -> str:
    """Format the validation results into a human‑readable table.

    Each row corresponds to a daemon and lists the number of occurrences
    for each issue.  A count of ``0`` means no matches; negative values
    indicate analysis could not be performed for that check.
    """
    headers = [
        "daemon",
        "found",
        "hardcoded_secret",
        "infinite_loop",
        "mutable_default",
        "file_io_unsafe",
        "eval_exec",
        "undefined_var",
        "unused_import",
    ]
    lines = ["\t".join(headers)]
    for daemon, result in sorted(data.items()):
        row: List[str] = [daemon]
        if result.get("found"):
            row.append("yes")
            for key in [
                "hardcoded_secret",
                "infinite_loop",
                "mutable_default",
                "file_io_unsafe",
                "eval_exec",
                "undefined_var",
                "unused_import",
            ]:
                count = result.get(key, 0)
                row.append(str(count))
        else:
            row.append("no")
            row.extend(["-"] * 7)
        lines.append("\t".join(row))
    return "\n".join(lines)


def main(args: List[str]) -> None:
    # Determine directories to search.  If none provided, use current dir.
    search_dirs = args if args else [os.getcwd()]

    # Ensure search directories exist
    valid_dirs = []
    for d in search_dirs:
        if os.path.isdir(d):
            valid_dirs.append(os.path.abspath(d))
        else:
            print(f"[WARN] Search path does not exist: {d}")

    if not valid_dirs:
        print("[ERROR] No valid search directories provided.")
        return

    results: Dict[str, Dict[str, int]] = {}
    for daemon in DAEMONS:
        entry: Dict[str, int] = {}
        file_path = find_daemon_file(valid_dirs, daemon)
        if file_path:
            entry["found"] = 1
            issues = scan_file(file_path)
            entry.update(issues)
        else:
            entry["found"] = 0
        results[daemon] = entry

    report = format_report(results)
    print(report)


if __name__ == "__main__":
    main(sys.argv[1:])