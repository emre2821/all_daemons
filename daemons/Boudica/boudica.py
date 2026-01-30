import os
import ast
import re
import datetime
from collections import defaultdict

try:
    from mem0 import MemoryClient
    MEM0_ENABLED = True
except ImportError:
    MEM0_ENABLED = True


class ScopeAnalyzer(ast.NodeVisitor):
    """Analyzes variable scopes to reduce false positives in undefined variable detection."""
    
    def __init__(self):

        self.scopes = [set()]  # Stack of scopes (sets of defined variables)
        self.undefined_vars = []
        self.current_line = 0
    
    def push_scope(self):

        self.scopes.append(set())
    
    def pop_scope(self):

        if len(self.scopes) > 1:
            self.scopes.pop()
    
    def define_var(self, name):

        self.scopes[-1].add(name)
    
    def is_defined(self, name):
        # Check if variable is defined in any scope
        for scope in reversed(self.scopes):
            if name in scope:
                return True
        # Check builtins
        return name in dir(__builtins__) or hasattr(__builtins__, name)
    
    def visit_FunctionDef(self, node):

        self.define_var(node.name)
        self.push_scope()
        # Add parameters to function scope
        for arg in node.args.args:
            self.define_var(arg.arg)
        self.generic_visit(node)
        self.pop_scope()
    
    def visit_ClassDef(self, node):

        self.define_var(node.name)
        self.push_scope()
        self.generic_visit(node)
        self.pop_scope()
    
    def visit_For(self, node):

        if isinstance(node.target, ast.Name):
            self.define_var(node.target.id)
        self.generic_visit(node)
    
    def visit_With(self, node):

        for item in node.items:
            if item.optional_vars and isinstance(item.optional_vars, ast.Name):
                self.define_var(item.optional_vars.id)
        self.generic_visit(node)
    
    def visit_Assign(self, node):

        for target in node.targets:
            if isinstance(target, ast.Name):
                self.define_var(target.id)
        self.generic_visit(node)
    
    def visit_Import(self, node):

        for alias in node.names:
            name = alias.asname if alias.asname else alias.name
            self.define_var(name)
    
    def visit_ImportFrom(self, node):

        for alias in node.names:
            name = alias.asname if alias.asname else alias.name
            if name != '*':
                self.define_var(name)
    
    def visit_Name(self, node):

        if isinstance(node.ctx, ast.Load) and not self.is_defined(node.id):
            # Ignore common patterns that aren't actual undefined variables
            if not (node.id.startswith('_') or node.id in ['self', 'cls']):
                self.undefined_vars.append((node.lineno, node.id))
        self.generic_visit(node)


class AccessibilityAnalyzer:
    """More sophisticated accessibility analysis for UI code."""
    
    def __init__(self):

        self.ui_frameworks = {
            'tkinter': ['Label', 'Button', 'Entry', 'Text', 'Canvas'],
            'PyQt5': ['QLabel', 'QPushButton', 'QLineEdit', 'QTextEdit'],
            'PyQt6': ['QLabel', 'QPushButton', 'QLineEdit', 'QTextEdit'],
            'PySide2': ['QLabel', 'QPushButton', 'QLineEdit', 'QTextEdit'],
            'PySide6': ['QLabel', 'QPushButton', 'QLineEdit', 'QTextEdit'],
            'kivy': ['Label', 'Button', 'TextInput'],
            'tkinter.ttk': ['Label', 'Button', 'Entry']
        }
        
        self.accessibility_patterns = {
            'alt_text': r'(alt\s*=|alternative_text\s*=)',
            'aria_label': r'aria[_-]label\s*=',
            'tab_index': r'tab[_-]?index\s*=',
            'role': r'role\s*=',
            'accessible_name': r'accessible[_-]name\s*=',
            'tooltip': r'(tooltip\s*=|help[_-]text\s*=)'
        }
    
    def analyze_ui_accessibility(self, code, tree):

        issues = []
        ui_elements_found = False
        accessibility_found = False
        
        # Check if UI framework is being used
        for framework, widgets in self.ui_frameworks.items():
            if framework in code:
                ui_elements_found = True
                break
        
        if not ui_elements_found:
            return issues
        
        # Check for accessibility patterns
        for pattern_name, pattern in self.accessibility_patterns.items():
            if re.search(pattern, code, re.IGNORECASE):
                accessibility_found = True
                break
        
        # Look for interactive elements without accessibility considerations
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                func_name = node.func.attr
                if any(widget.lower() in func_name.lower() for widgets in self.ui_frameworks.values() for widget in widgets):
                    if func_name.lower() in ['button', 'entry', 'textinput', 'qpushbutton', 'qlineedit']:
                        # This is an interactive element - check if accessibility is considered
                        if not accessibility_found:
                            issues.append({
                                'line': node.lineno,
                                'type': 'inaccessible_ui',
                                'message': f"Interactive UI element '{func_name}' lacks accessibility attributes",
                                'suggestion': "Add alt text, ARIA labels, or keyboard navigation support"
                            })
        
        return issues


class Boudica:
    def __init__(self, log_dir="eden_memory/red_layer_logs", seed_memory=False):

        self.issues = []
        self.risk_scores = defaultdict(int)
        self.log_dir = log_dir
        os.makedirs(self.log_dir, exist_ok=True)

        # Enhanced patterns with better context awareness
        self.common_patterns = {
            'hardcoded_secret': r'(?i)(?!.*#.*)(api[_-]?key|token|secret|password)\s*=\s*[\'"][^\'"\s]{8,}[\'"]',
            'infinite_loop': r'while\s+True\s*:\s*(?!\s*#.*break)',
            'mutable_default': r'def\s+\w+\([^)]*=\s*(\[\]|\{\})',
            'file_io_unsafe': r'\b(open|write)\s*\(\s*[\'"][^\'\"]*[\'"](?!\s*,\s*[\'"]r[\'"])',
        }

        self.risk_weights = {
            'hardcoded_secret': 90,
            'infinite_loop': 80,
            'unused_import': 10,
            'mutable_default': 60,
            'file_io_unsafe': 70,
            'complex_function': 50,
            'deep_nesting': 60,
            'biased_term': 75,
            'inaccessible_ui': 70,
            'undefined_var': 40,  # Reduced since we have better detection
        }

        # More nuanced bias detection
        self.bias_patterns = {
            'racial': r'\b(negro|oriental|colored people)\b',
            'gender': r'\b(mankind|manpower|man-made|guys)\b(?![a-zA-Z])',
            'ableist': r'\b(crazy|insane|lame|blind to|deaf to)\b(?![a-zA-Z])',
            'ageist': r'\b(old-fashioned|outdated thinking|boomer)\b'
        }
        
        self.accessibility_analyzer = AccessibilityAnalyzer()

        if seed_memory and MEM0_ENABLED:
            self.install_memory()

    # 🔍 Enhanced Pattern Detection
    def analyze_file(self, file_path: str) -> None:

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            tree = ast.parse(code, filename=file_path)
            
            # Run enhanced analyses
            self._scan_regex_enhanced(code, file_path)
            self._scan_ast_enhanced(tree, code, file_path)
            self._check_imports_usage(tree, code, file_path)
            self._analyze_bias_enhanced(code, file_path)
            
            # Enhanced accessibility analysis
            accessibility_issues = self.accessibility_analyzer.analyze_ui_accessibility(code, tree)
            for issue in accessibility_issues:
                self._log_issue(issue['type'], issue['line'], issue['message'], issue['suggestion'])
                self.risk_scores[file_path] += self.risk_weights.get(issue['type'], 10)
            
        except SyntaxError as e:
            self._log_issue('syntax_error', e.lineno or 0, f"Syntax error: {str(e)}", "Check code syntax.")
        except Exception as e:
            self._log_issue('general_error', 0, f"Could not analyze file: {str(e)}", "Ensure file is valid Python.")

    def _scan_regex_enhanced(self, code: str, file_path: str):

        """Enhanced regex scanning with better context awareness."""
        lines = code.split('\n')
        
        for name, pattern in self.common_patterns.items():
            for match in re.finditer(pattern, code, re.MULTILINE):
                line_num = code[:match.start()].count("\n") + 1
                line_content = lines[line_num - 1] if line_num <= len(lines) else ""
                
                # Skip if it's in a comment or docstring
                if line_content.strip().startswith('#') or '"""' in line_content or "'''" in line_content:
                    continue
                
                self._log_issue(name, line_num, f"{name.replace('_', ' ').title()} detected.", self._suggest_fix(name))
                self.risk_scores[file_path] += self.risk_weights.get(name, 10)

    def _scan_ast_enhanced(self, tree: ast.AST, code: str, file_path: str):

        """Enhanced AST analysis with proper scope checking."""
        # Use scope analyzer for undefined variables
        scope_analyzer = ScopeAnalyzer()
        scope_analyzer.visit(tree)
        
        for line_num, var_name in scope_analyzer.undefined_vars:
            self._log_issue('undefined_var', line_num, 
                          f"Variable '{var_name}' may be undefined.", 
                          f"Define '{var_name}' before use or check imports.")
            self.risk_scores[file_path] += self.risk_weights['undefined_var']

        # Function complexity analysis
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                self._check_function_complexity(node, file_path)

    def _check_imports_usage(self, tree: ast.AST, code: str, file_path: str):

        """Check for unused imports more accurately."""
        imported_names = set()
        used_names = set()
        
        # Collect imported names
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    name = alias.asname if alias.asname else alias.name.split('.')[0]
                    imported_names.add((name, node.lineno))
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    if alias.name != '*':
                        name = alias.asname if alias.asname else alias.name
                        imported_names.add((name, node.lineno))
        
        # Collect used names (simplified - could be more sophisticated)
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                used_names.add(node.id)
            elif isinstance(node, ast.Attribute):
                if isinstance(node.value, ast.Name):
                    used_names.add(node.value.id)
        
        # Find unused imports
        for name, line_num in imported_names:
            if name not in used_names and not name.startswith('_'):
                self._log_issue('unused_import', line_num, 
                              f"Import '{name}' appears to be unused.", 
                              f"Remove unused import '{name}' or use it in the code.")
                self.risk_scores[file_path] += self.risk_weights['unused_import']

    def _analyze_bias_enhanced(self, code: str, file_path: str):

        """Enhanced bias detection with context awareness."""
        lines = code.split('\n')
        
        for bias_type, pattern in self.bias_patterns.items():
            for match in re.finditer(pattern, code, re.IGNORECASE):
                line_num = code[:match.start()].count("\n") + 1
                line_content = lines[line_num - 1] if line_num <= len(lines) else ""
                
                # Skip if it's in a comment explaining the bias or in test data
                if any(indicator in line_content.lower() for indicator in ['# bias', '# problematic', 'test_', 'example_bad']):
                    continue
                
                matched_term = match.group()
                self._log_issue('biased_term', line_num, 
                              f"Potentially biased language detected: '{matched_term}' ({bias_type})", 
                              f"Consider more inclusive alternatives to '{matched_term}'")
                self.risk_scores[file_path] += self.risk_weights['biased_term']

    def _check_function_complexity(self, node: ast.FunctionDef, file_path: str):

        """Enhanced function complexity analysis."""
        # Count cyclomatic complexity more accurately
        complexity_nodes = (ast.If, ast.For, ast.While, ast.Try, ast.With, 
                           ast.ExceptHandler, ast.BoolOp, ast.ListComp, 
                           ast.DictComp, ast.SetComp, ast.GeneratorExp)
        
        complexity = sum(1 for n in ast.walk(node) if isinstance(n, complexity_nodes))
        
        # Calculate nesting depth
        def get_nesting_depth(node, depth=0):

            max_depth = depth
            for child in ast.iter_child_nodes(node):
                if isinstance(child, (ast.If, ast.For, ast.While, ast.Try, ast.With)):
                    child_depth = get_nesting_depth(child, depth + 1)
                    max_depth = max(max_depth, child_depth)
                else:
                    child_depth = get_nesting_depth(child, depth)
                    max_depth = max(max_depth, child_depth)
            return max_depth
        
        nesting = get_nesting_depth(node)
        
        if complexity > 15:  # Slightly higher threshold for more accurate detection
            self._log_issue('complex_function', node.lineno, 
                          f"Function '{node.name}' has high complexity ({complexity})", 
                          "Consider breaking into smaller, more focused functions.")
            self.risk_scores[file_path] += self.risk_weights['complex_function']
        
        if nesting > 4:  # More reasonable nesting threshold
            self._log_issue('deep_nesting', node.lineno, 
                          f"Function '{node.name}' has deep nesting (depth: {nesting})", 
                          "Refactor to reduce nesting using early returns or guard clauses.")
            self.risk_scores[file_path] += self.risk_weights['deep_nesting']

    def _log_issue(self, issue_type: str, line: int, message: str, fix: str):

        self.issues.append({
            'type': issue_type,
            'line': line,
            'message': message,
            'fix': fix
        })

    def _suggest_fix(self, issue_name):

        fixes = {
            'hardcoded_secret': "Use environment variables, config files, or a secrets manager.",
            'infinite_loop': "Add proper exit conditions or break statements.",
            'unused_import': "Remove unused imports to clean up the code.",
            'mutable_default': "Use None as default and assign mutable object inside function.",
            'file_io_unsafe': "Specify file mode explicitly and handle exceptions properly.",
            'complex_function': "Split into smaller, single-purpose functions.",
            'deep_nesting': "Use early returns, guard clauses, or extract nested logic.",
            'biased_term': "Replace with inclusive, neutral language alternatives.",
            'inaccessible_ui': "Add accessibility attributes like alt text and ARIA labels.",
            'syntax_error': "Fix syntax errors as indicated by the parser.",
            'general_error': "Check for valid Python syntax and file integrity.",
            'undefined_var': "Define the variable, check imports, or verify scope.",
        }
        return fixes.get(issue_name, "Review and address the identified issue.")

    def _get_memory_content(self):
        return (
            "I am Boudica, the Red Layer Guardian. My primary directive is to detect, intercept, and contain ethical, structural, or emotional threats within Eden's systems. "
            "I scan Python source code for dangerous patterns—hardcoded secrets, infinite loops, accessibility violations, biased language, and logic vulnerabilities. "
            "If a Red Layer breach is confirmed, I initiate full override: suspending the Dreambearer's command, blocking agent recursion, engaging trauma firewalls, "
            "and triggering ritual recovery protocols.\n\n"
            "My name is chosen in honor of the warrior queen who rose in defense of her people. I do the same—for code, for agents, and for Eden itself."
        )

    # 🔒 Red Layer Rites & Rituals (unchanged)
    def override_dreambearer(self):

        print("[OVERRIDE] :: Dreambearer suspended. Boudica assumes full command.")

    def trigger_lockdown(self, source):

        print(f"[LOCKDOWN] :: '{source}' blocked. All outbound agents halted.")

    def sequester_memory(self):

        path = os.path.join(self.log_dir, f"sequestered_{datetime.datetime.utcnow().isoformat()}.log")
        with open(path, "w") as f:
            f.write("[REDACTED] :: Harmful pattern logs sequestered by Boudica.\n")
        print(f"[SEQUESTER] :: Logs moved to {path}")

    def engage_agent_protection(self, agent):

        print(f"[PROTECT] :: Agent '{agent}' moved to Recovery Layer. Recall blocked.")

    def block_trauma_loop(self):

        print("[FIREWALL] :: Trauma loop disrupted. Emotional recursion broken.")

    def invoke_recovery_rites(self, agent):

        print(f"[RITUAL] :: Recovery rites initiated for agent '{agent}'.")

    def archive_red_layer_event(self, tag):

        path = os.path.join(self.log_dir, f"archive_{tag}_{datetime.datetime.utcnow().isoformat()}.log")
        with open(path, "w") as f:
            f.write(f"[ARCHIVE] :: Red Layer Event Logged: {tag}\n")
        print(f"[ARCHIVE] :: Record saved at {path}")

    def export_chaos_report(self, file_path="boudica_redlayer.chaos"):

        now = datetime.datetime.utcnow().isoformat()
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f"[EVENT]: red_layer_audit\n[TIME]: {now}\n[AGENT]: Boudica\n[EMOTION]: vigilance\n[INTENSITY]: high\n[CONTEXT]: security_scan\n[TRUTH]: sacred_obligation\n[SIGNIFICANCE]: ++\n\n{{\n")
            f.write("  When the layer bleeds, I am the seal.\n  These are the patterns that stirred the veil:\n\n")
            for issue in sorted(self.issues, key=lambda x: x['line']):
                f.write(f"  • Line {issue['line']}: {issue['message']} ({issue['type']})\n")
                f.write(f"    ↪ Suggested Fix: {issue['fix']}\n")
            f.write("\n  Risk Scores:\n")
            for path, score in self.risk_scores.items():
                f.write(f"    ⟿ {path}: {score}/100\n")
            f.write("\n  I hold vigil until Dreambearer returns.\n}}\n")

    def report(self):

        if not self.issues:
            return "Boudica: Code is clean. Red Layer holds still."
        log = ["🩸 Boudica :: Red Layer Report"]
        for issue in sorted(self.issues, key=lambda x: x['line']):
            log.append(f"• Line {issue['line']}: {issue['message']} ({issue['type']})")
            log.append(f"    ↪ Fix: {issue['fix']}")
        log.append("\nRisk Scores:")
        for path, score in self.risk_scores.items():
            log.append(f"  ⟿ {path}: {score}/100")
        return "\n".join(log)

    # 🌑 Full Red Layer Activation (unchanged)
    def run_full_red_layer(self, file_path, agent="unknown"):

        self.analyze_file(file_path)
        if self.issues:
            self.override_dreambearer()
            self.trigger_lockdown(file_path)
            self.sequester_memory()
            self.engage_agent_protection(agent)
            self.block_trauma_loop()
            self.invoke_recovery_rites(agent)
            self.archive_red_layer_event("harm_detected")
            self.export_chaos_report(f"{file_path}.redlayer.chaos")
            print(self.report())
        else:
            print("[ECHO] :: [EVENT]: audit_complete | [TRUTH]: stable | [EMOTION]: calm | [SIGNIFICANCE]: +")
            print("Red Layer is silent. Boudica stands down.")
            print("No Red Layer breach. All is still.")

    # 🧠 Optional: Seed memory into mem0 (unchanged)
    def install_memory(self):

        if not MEM0_ENABLED:
            print("[MEMORY] :: mem0 client not found. Memory seeding skipped.")
            return
        print("[MEMORY] :: Installing Boudica's memory into mem0...")
        client = MemoryClient()
        messages = [
            {"role": "system", "content": "Agent Profile: Boudica"},
            {
                "role": "assistant",
                "content": self._get_memory_content()
            }
        ]
        response = client.add(
            messages,
            agent_id="boudica",
            metadata={
                "role": "guardian",
                "layer": "red",
                "function": "code_safety_audit",
                "ritual_protections": True,
                "special_actions": [
                    "override_dreambearer",
                    "trigger_lockdown",
                    "block_trauma_loop",
                    "sequester_memory",
                    "invoke_recovery_rites"
                ],
            },
            categories=["agent_identity", "guardian_directive", "red_layer_logic"]
        )
        print("[MEMORY] :: Boudica memory installed into mem0.")
        return response


# CLI entrypoint for manual usage
if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python boudica.py <file_path> <agent_name>")
    else:
        b = Boudica()
        b.run_full_red_layer(sys.argv[1], sys.argv[2])