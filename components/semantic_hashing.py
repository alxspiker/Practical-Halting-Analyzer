import ast
import hashlib

class Canonicalizer(ast.NodeTransformer):
    """
    Transforms a Python AST into a canonical form by:
    1. Removing docstrings.
    2. Renaming all local variables, arguments, and function names to a standard,
       predictable sequence (e.g., func_0, arg_0, var_0).
    """
    def __init__(self):
        self.func_counter = 0
        self.var_counters = {}  # A stack of counters for nested scopes
        self.name_maps = {}     # A stack of name mappings for nested scopes

    def _get_scope_id(self):
        """Returns a unique identifier for the current scope."""
        return len(self.name_maps)

    def _enter_scope(self):
        scope_id = self._get_scope_id()
        self.name_maps[scope_id] = {}
        self.var_counters[scope_id] = 0

    def _exit_scope(self):
        scope_id = self._get_scope_id() - 1
        del self.name_maps[scope_id]
        del self.var_counters[scope_id]

    def _add_to_map(self, old_name, prefix):
        scope_id = self._get_scope_id() - 1
        if old_name not in self.name_maps[scope_id]:
            new_name = f"{prefix}_{self.var_counters[scope_id]}"
            self.name_maps[scope_id][old_name] = new_name
            self.var_counters[scope_id] += 1

    def visit_FunctionDef(self, node):
        """Handle function definitions to manage scopes and rename names."""
        # Rename the function itself at the outer scope
        self._add_to_map(node.name, "func")
        node.name = self.name_maps[self._get_scope_id() - 1][node.name]

        # Enter a new scope for the function body
        self._enter_scope()
        
        # Rename arguments
        for arg in node.args.args:
            self._add_to_map(arg.arg, "arg")
            arg.arg = self.name_maps[self._get_scope_id() - 1][arg.arg]
            
        # Rename local variables by finding all assignments
        for body_node in ast.walk(node):
            if isinstance(body_node, ast.Assign):
                for target in body_node.targets:
                    if isinstance(target, ast.Name):
                        self._add_to_map(target.id, "var")

        # Process the body with the new name map
        self.generic_visit(node)
        
        # Exit the scope
        self._exit_scope()
        return node

    def visit_Name(self, node):
        """Rename variables based on the current scope's map."""
        # Go from inner scope to outer to find the name
        for i in range(len(self.name_maps) - 1, -1, -1):
            if node.id in self.name_maps[i]:
                node.id = self.name_maps[i][node.id]
                break
        return node
    
    def visit_Expr(self, node):
        """Remove docstrings."""
        if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
            return None
        return self.generic_visit(node)

def get_semantic_hash(program: str) -> str:
    """
    Returns a hash of the program's canonical form.
    Returns a simple hash if canonicalization fails.
    """
    try:
        tree = ast.parse(program)
        canonicalizer = Canonicalizer()
        
        # Create a top-level scope for the module
        canonicalizer._enter_scope()
        canonical_tree = canonicalizer.visit(tree)
        canonicalizer._exit_scope()
        
        # Remove empty nodes (from deleted docstrings)
        ast.fix_missing_locations(canonical_tree)
        
        canonical_code = ast.unparse(canonical_tree)
        return hashlib.sha256(canonical_code.encode('utf-8')).hexdigest()
    except Exception:
        # Fallback to lexical hashing if canonicalization fails
        return hashlib.sha256(program.encode('utf-8')).hexdigest()