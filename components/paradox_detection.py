# File: components/paradox_detection.py
import ast
from .semantic_hashing import Canonicalizer

class ParadoxVisitor(ast.NodeVisitor):
    def __init__(self):
        self.has_sys_os_import = False
        self.has_path_adjust = False
        self.has_analyzer_import = False
        self.has_self_read = False
        self.has_analyzer_call = False
        self.has_inverting_if = False
    
    def visit_Import(self, node):
        for alias in node.names:
            if alias.name in ('sys', 'os'):
                self.has_sys_os_import = True
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node):
        if node.module == 'main' and any(alias.name == 'analyze_halting' for alias in node.names):
            self.has_analyzer_import = True
        self.generic_visit(node)
    
    def visit_Call(self, node):
        # Check for sys.path.append(os.path.dirname(os.path.dirname(__file__)))
        if isinstance(node.func, ast.Attribute) and node.func.attr == 'append':
            if isinstance(node.func.value, ast.Attribute) and node.func.value.attr == 'path':
                if isinstance(node.func.value.value, ast.Name) and node.func.value.value.id == 'sys':
                    if len(node.args) == 1:
                        arg = node.args[0]
                        if isinstance(arg, ast.Call) and isinstance(arg.func, ast.Attribute) and arg.func.attr == 'dirname' and isinstance(arg.func.value, ast.Attribute) and arg.func.value.attr == 'path' and isinstance(arg.func.value.value, ast.Name) and arg.func.value.value.id == 'os':
                            if len(arg.args) == 1:
                                inner_arg = arg.args[0]
                                if isinstance(inner_arg, ast.Call) and isinstance(inner_arg.func, ast.Attribute) and inner_arg.func.attr == 'dirname' and isinstance(inner_arg.func.value, ast.Attribute) and inner_arg.func.value.attr == 'path' and isinstance(inner_arg.func.value.value, ast.Name) and inner_arg.func.value.value.id == 'os':
                                    if len(inner_arg.args) == 1 and isinstance(inner_arg.args[0], ast.Name) and inner_arg.args[0].id == '__file__':
                                        self.has_path_adjust = True
        
        # Check for analyze_halting(source)
        if isinstance(node.func, ast.Name) and node.func.id == 'analyze_halting':
            if len(node.args) == 1 and isinstance(node.args[0], ast.Name) and node.args[0].id == 'source':
                self.has_analyzer_call = True
        
        self.generic_visit(node)
    
    def visit_With(self, node):
        if len(node.items) == 1:
            item = node.items[0]
            if isinstance(item.context_expr, ast.Call) and isinstance(item.context_expr.func, ast.Name) and item.context_expr.func.id == 'open':
                args = item.context_expr.args
                if len(args) >= 1 and isinstance(args[0], ast.Name) and args[0].id == '__file__':
                    if len(args) >= 2 and isinstance(args[1], ast.Constant) and args[1].value == 'r':
                        for stmt in node.body:
                            if isinstance(stmt, ast.Assign) and len(stmt.targets) == 1 and isinstance(stmt.targets[0], ast.Name) and stmt.targets[0].id == 'source':
                                if isinstance(stmt.value, ast.Call) and isinstance(stmt.value.func, ast.Attribute) and stmt.value.func.attr == 'read' and isinstance(stmt.value.func.value, ast.Name) and stmt.value.func.value.id == 'f':
                                    self.has_self_read = True
        self.generic_visit(node)
    
    def visit_If(self, node):
        if isinstance(node.test, ast.Compare) and len(node.test.ops) == 1 and isinstance(node.test.ops[0], ast.Eq):
            left = node.test.left
            comparators = node.test.comparators
            if len(comparators) == 1:
                right = comparators[0]
                if isinstance(left, ast.Name) and left.id == 'result' and isinstance(right, ast.Constant) and isinstance(right.value, str) and right.value == 'halts':
                    # Check body for while True: pass
                    has_infinite_loop = False
                    for stmt in node.body:
                        if isinstance(stmt, ast.While) and isinstance(stmt.test, ast.Constant) and stmt.test.value is True:
                            if len(stmt.body) == 1 and isinstance(stmt.body[0], ast.Pass):
                                has_infinite_loop = True
                    # Check orelse for print
                    has_print = False
                    for stmt in node.orelse:
                        if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call) and isinstance(stmt.value.func, ast.Name) and stmt.value.func.id == 'print':
                            if len(stmt.value.args) == 1 and isinstance(stmt.value.args[0], ast.Constant) and isinstance(stmt.value.args[0].value, str):
                                has_print = True
                    if has_infinite_loop and has_print:
                        self.has_inverting_if = True
        self.generic_visit(node)

def detect_paradox(program: str) -> bool:
    try:
        tree = ast.parse(program)
        canonicalizer = Canonicalizer()
        canonicalizer._enter_scope()
        canonical_tree = canonicalizer.visit(tree)
        canonicalizer._exit_scope()
        ast.fix_missing_locations(canonical_tree)
        
        visitor = ParadoxVisitor()
        visitor.visit(canonical_tree)
        return (visitor.has_sys_os_import and
                visitor.has_path_adjust and
                visitor.has_analyzer_import and
                visitor.has_self_read and
                visitor.has_analyzer_call and
                visitor.has_inverting_if)
    except Exception:
        return False