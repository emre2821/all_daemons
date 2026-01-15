import os
import json
import ast
import argparse
import textwrap
from pathlib import Path
from datetime import datetime

class SaphiraSynchronizer:
    """
    Saphira v3: A command-line tool to heal and audit daemon file structures.
    It intelligently creates missing files and synchronizes existing ones with the source code.
    """

    def __init__(self, root_path_str, logger_func=print):
        self.root_dir = Path(root_path_str)
        self.templates_dir = self.root_dir / "Saphira" / "templates"
        self.skip_dirs = {"_daemon_specialty_folders", "Saphira", "Corin"}
        self.log = logger_func
        self.templates = self._load_templates()

    def _load_templates(self):
        """Loads the base JSON templates for daemons."""
        try:
            return {
                "mirror": json.loads((self.templates_dir / "template.daemon_mirror.json").read_text()),
                "voice": json.loads((self.templates_dir / "template.daemon_voice.json").read_text()),
                "function": json.loads((self.templates_dir / "template.daemon_function.json").read_text()),
            }
        except FileNotFoundError as e:
            self.log(f"❌ CRITICAL: Template file not found at {e.path}. Saphira cannot function.")
            return None

    def _extract_intel_from_py(self, py_file: Path):
        """Safely parses a Python file to extract its docstring and function names."""
        if not py_file.exists():
            return None
        try:
            source = py_file.read_text(encoding="utf-8")
            tree = ast.parse(source)
            docstring = ast.get_docstring(tree) or "No description found."
            functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
            return {"docstring": textwrap.dedent(docstring).strip(), "functions": sorted(functions)}
        except Exception as e:
            self.log(f"⚠️  Could not parse {py_file.name}: {e}")
            return None

    def heal_missing_files(self, daemon_folder: Path, force: bool):
        """Generates any required .json files that do not exist."""
        daemon_name = daemon_folder.name
        py_intel = self._extract_intel_from_py(daemon_folder / f"{daemon_name.lower()}.py")
        if not py_intel:
            self.log(f"ℹ️  Skipping heal for {daemon_name}: No Python source file found.")
            return

        # Define required files and the logic to generate them
        generation_map = {
            "daemon_mirror.json": lambda: {**self.templates["mirror"], "name": daemon_name, "daemon_id": f"{daemon_name.lower()}_daemon", "description": py_intel["docstring"]},
            "daemon_voice.json": lambda: {**self.templates["voice"], "voice_id": f"{daemon_name.lower()}_voice"},
            "daemon_function.json": lambda: {**self.templates["function"], "functions": py_intel["functions"]},
        }

        for file_template, generator_func in generation_map.items():
            target_path = daemon_folder / f"{daemon_name.lower()}.{file_template}"
            if not target_path.exists():
                self.log(f"🔎 MISSING: Found missing '{target_path.name}' for {daemon_name}.")
                new_content = generator_func()
                self._write_file(target_path, new_content, force, "HEALED")

    def audit_existing_files(self, daemon_folder: Path, force: bool):
        """Audits existing files for content mismatches, like function lists."""
        daemon_name = daemon_folder.name
        function_path = daemon_folder / f"{daemon_name.lower()}.daemon_function.json"
        
        if not function_path.exists():
            return # Healing pass will handle this

        py_intel = self._extract_intel_from_py(daemon_folder / f"{daemon_name.lower()}.py")
        if not py_intel:
            self.log(f"ℹ️  Skipping audit for {daemon_name}: No Python source file found.")
            return

        # Compare function list
        try:
            recorded_data = json.loads(function_path.read_text(encoding="utf-8"))
            recorded_functions = set(recorded_data.get("functions", []))
            actual_functions = set(py_intel["functions"])

            if recorded_functions != actual_functions:
                newly_added = sorted(list(actual_functions - recorded_functions))
                removed = sorted(list(recorded_functions - actual_functions))
                self.log(f"⚖️  AUDIT: Function mismatch in '{daemon_name}'.", "WARN")
                if newly_added: self.log(f"    - ADDED: {newly_added}")
                if removed: self.log(f"    - REMOVED: {removed}")

                if force:
                    updated_content = {**recorded_data, "functions": py_intel["functions"]}
                    self._write_file(function_path, updated_content, force=True, action="SYNCED")

        except json.JSONDecodeError:
            self.log(f"⚠️  AUDIT: Could not parse {function_path.name}, skipping audit.", "ERROR")

    def _write_file(self, path: Path, content: dict, force: bool, action: str):
        """Writes a file, asking for confirmation unless in force mode."""
        parent_name = path.parent.name
        
        if not force:
            if input(f"    Create/overwrite '{path.name}' for '{parent_name}'? (y/n): ").lower() != 'y':
                self.log(f"❌ SKIPPED: User chose not to write file.")
                return

        # Create a backup before overwriting
        if path.exists():
            backup_path = path.with_suffix(path.suffix + f".saphira_bak_{datetime.now():%Y%m%d%H%M%S}")
            path.rename(backup_path)
            
        path.write_text(json.dumps(content, indent=4), encoding="utf-8")
        self.log(f"✔️ {action}: Wrote {path.name} for {parent_name}")

    def run(self, audit=False, force=False):
        """Main execution loop."""
        if not self.templates: return
        self.log("🌸 Saphira starting scan...")
        
        for folder in self.root_dir.iterdir():
            if folder.is_dir() and folder.name not in self.skip_dirs:
                self.log(f"\n--- Analyzing Daemon: {folder.name} ---")
                # First, heal any missing files
                self.heal_missing_files(folder, force)
                # Then, if requested, audit existing ones
                if audit:
                    self.audit_existing_files(folder, force)
        
        self.log("\n🌸 Saphira scan complete.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Saphira v3: The Daemon Synchronizer.")
    parser.add_argument("--audit", action="store_true", help="Audit existing files for sync issues (e.g., function lists).")
    parser.add_argument("--force", action="store_true", help="Run non-interactively, applying all fixes without prompting.")
    args = parser.parse_args()

    ROOT_DAEMONS_DIR = os.path.join(os.environ.get("EDEN_ROOT", os.getcwd()), "daemons")
    
    synchronizer = SaphiraSynchronizer(ROOT_DAEMONS_DIR)
    synchronizer.run(audit=args.audit, force=args.force)
