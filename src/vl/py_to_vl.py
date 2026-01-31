"""
Python to VL Converter
Converts Python AST to VL source code

Usage:
    from vl.py_to_vl import PythonToVLConverter
    
    converter = PythonToVLConverter()
    vl_code = converter.convert(python_code)
"""

import ast
from typing import List, Optional, Any


class PythonToVLConverter:
    """
    Converts Python source code to VL source code
    
    Strategy:
    1. Parse Python code into AST
    2. Walk AST and generate VL constructs
    3. Handle Python-specific idioms (comprehensions, decorators, etc.)
    """
    
    def __init__(self):
        self.indent_level = 0
        self.output: List[str] = []
        self.imports: List[str] = []
        self.has_typing = False
        self.param_map: dict = {}  # Maps Python param names to VL i0, i1, etc.
        self.renamed_vars: dict = {}  # Maps Python var names that conflict with VL keywords
    
    def convert(self, python_code: str) -> str:
        """
        Convert Python source code to VL
        
        Args:
            python_code: Python source code as string
            
        Returns:
            VL source code as string
        """
        try:
            tree = ast.parse(python_code)
            return self._convert_module(tree)
        except SyntaxError as e:
            raise ValueError(f"Invalid Python syntax: {e}")
    
    def _convert_module(self, node: ast.Module) -> str:
        """Convert Python module to VL program"""
        self.output = []
        self.imports = []
        self.has_typing = False
        
        # First pass: collect imports and detect typing usage
        for stmt in node.body:
            if isinstance(stmt, (ast.Import, ast.ImportFrom)):
                self._collect_import(stmt)
        
        # Add VL metadata
        # Note: VL metadata format is meta:key,value pairs
        # For now, keep it simple or omit it
        # self.output.append("meta:name,converted_from_python")
        
        # Add dependencies if needed
        if self.imports:
            deps_str = ','.join(self.imports)
            self.output.append(f"deps:[{deps_str}]")
        
        self.output.append("")
        
        # Second pass: convert statements
        for stmt in node.body:
            if not isinstance(stmt, (ast.Import, ast.ImportFrom)):
                self._convert_statement(stmt)
        
        return '\n'.join(self.output)
    
    def _collect_import(self, node: ast.AST) -> None:
        """Collect import information"""
        if isinstance(node, ast.Import):
            for alias in node.names:
                self.imports.append(alias.name)
                if alias.name == 'typing':
                    self.has_typing = True
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                self.imports.append(node.module)
                if node.module == 'typing':
                    self.has_typing = True
    
    def _convert_statement(self, stmt: ast.AST) -> None:
        """Convert a Python statement to VL"""
        if isinstance(stmt, ast.ClassDef):
            self._convert_class(stmt)
        elif isinstance(stmt, ast.FunctionDef):
            self._convert_function(stmt)
        elif isinstance(stmt, ast.Assign):
            self._convert_assignment(stmt)
        elif isinstance(stmt, ast.AugAssign):
            self._convert_aug_assignment(stmt)
        elif isinstance(stmt, ast.Expr):
            self._convert_expr_statement(stmt)
        elif isinstance(stmt, ast.If):
            self._convert_if(stmt)
        elif isinstance(stmt, ast.While):
            self._convert_while(stmt)
        elif isinstance(stmt, ast.For):
            self._convert_for(stmt)
        elif isinstance(stmt, ast.Return):
            self._convert_return(stmt)
        elif isinstance(stmt, ast.With):
            self._convert_with(stmt)
        elif isinstance(stmt, ast.Try):
            self._convert_try(stmt)
        elif isinstance(stmt, (ast.Import, ast.ImportFrom)):
            # Already handled in first pass
            pass
        else:
            # Fallback: use Python passthrough
            self.output.append(f"{self._indent()}# TODO: Unsupported statement type: {type(stmt).__name__}")
    
    def _convert_class(self, node: ast.ClassDef) -> None:
        """Convert Python class to VL class"""
        # Handle decorators
        for decorator in node.decorator_list:
            decorator_str = self._convert_decorator(decorator)
            self.output.append(f"{self._indent()}{decorator_str}")
        
        # Class definition: class:name or class:name[BaseClass]
        class_line = f"{self._indent()}class:{node.name}"
        if node.bases:
            base_names = [self._convert_expr(base) for base in node.bases]
            class_line += f"[{','.join(base_names)}]"
        self.output.append(class_line)
        
        # Class body
        self.indent_level += 1
        for stmt in node.body:
            if isinstance(stmt, ast.FunctionDef):
                self._convert_function(stmt, is_method=True)
            else:
                self._convert_statement(stmt)
        self.indent_level -= 1
        self.output.append("")  # blank line after class
    
    def _convert_decorator(self, node: ast.AST) -> str:
        """Convert a decorator node to VL @decorator syntax"""
        if isinstance(node, ast.Name):
            return f"@{node.id}"
        elif isinstance(node, ast.Call):
            func_name = self._convert_expression(node.func)
            if node.args:
                args_str = ",".join(self._convert_expression(arg) for arg in node.args)
                return f"@{func_name}({args_str})"
            else:
                return f"@{func_name}()"
        else:
            return f"@{self._convert_expression(node)}"
    
    def _convert_function(self, node: ast.FunctionDef, is_method: bool = False) -> None:
        """Convert Python function to VL function"""
        # Handle decorators (skip for methods since __init__ etc may have special decorators)
        if not is_method:
            for decorator in node.decorator_list:
                decorator_str = self._convert_decorator(decorator)
                self.output.append(f"{self._indent()}{decorator_str}")
        
        # Extract function signature
        name = node.name
        param_types = []
        return_type = None
        
        # Build parameter name mapping: Python names -> VL indices (i0, i1, etc.)
        self.param_map = {}
        param_start = 0
        
        # For methods, skip 'self' parameter
        args_to_process = node.args.args
        if is_method and args_to_process and args_to_process[0].arg == 'self':
            args_to_process = args_to_process[1:]
        
        for idx, arg in enumerate(args_to_process):
            self.param_map[arg.arg] = f'i{idx}'
        
        # Process parameters - get types only
        for arg in args_to_process:
            # Check for type annotations
            if arg.annotation:
                param_types.append(self._convert_type_annotation(arg.annotation))
            else:
                param_types.append('any')
        
        # Check for return type annotation
        if node.returns:
            return_type = self._convert_type_annotation(node.returns)
        else:
            return_type = 'any'
        
        # Build VL function signature: F:name|type1,type2|returntype|
        if param_types:
            types_str = ','.join(param_types)
            self.output.append(f"{self._indent()}F:{name}|{types_str}|{return_type}|")
        else:
            self.output.append(f"{self._indent()}F:{name}||{return_type}|")
        
        # Convert function body - collect body statements first
        self.indent_level += 1
        body_statements = []
        for stmt in node.body:
            # Capture the current output position
            start_len = len(self.output)
            self._convert_statement(stmt)
            # Get the statements that were added
            new_stmts = self.output[start_len:]
            body_statements.extend(new_stmts)
            # Remove them from output temporarily
            self.output = self.output[:start_len]
        
        self.indent_level -= 1
        
        # Check if we can do single-line format (only one statement)
        # But avoid single-line for methods with 'self' references as they need proper parsing
        has_self_ref = any('self' in stmt for stmt in body_statements)
        if len(body_statements) == 1 and not (is_method and has_self_ref):
            # Single-line format: F:name|types|type|statement
            stmt = body_statements[0].strip()
            # Remove existing signature line and replace with single-line version
            self.output.pop()  # Remove the multi-line signature
            if param_types:
                types_str = ','.join(param_types)
                self.output.append(f"{self._indent()}F:{name}|{types_str}|{return_type}|{stmt}")
            else:
                self.output.append(f"{self._indent()}F:{name}||{return_type}|{stmt}")
        else:
            # Multi-line format: need to use proper indentation
            # Re-add body statements with proper pipe formatting
            # All statements except the LAST one must end with |
            self.indent_level += 1
            for i, stmt in enumerate(body_statements):
                is_last = (i == len(body_statements) - 1)
                if not is_last:
                    # Not the last statement - must end with |
                    if not stmt.rstrip().endswith('|'):
                        stmt = stmt.rstrip() + '|'
                else:
                    # Last statement - must NOT end with | (this terminates the function)
                    if stmt.rstrip().endswith('|'):
                        stmt = stmt.rstrip()[:-1]
                self.output.append(stmt)
            self.indent_level -= 1
        self.param_map = {}  # Clear mapping after function
        self.output.append("")
        self.output.append("")  # Extra blank line to help parser
    
    def _convert_assignment(self, node: ast.Assign) -> None:
        """Convert Python assignment to VL"""
        if len(node.targets) == 1:
            target = node.targets[0]
            if isinstance(target, ast.Name):
                var_name = target.id
                # Avoid VL keyword conflicts by renaming single-letter keywords
                vl_keywords = {'i', 'o', 'v', 't', 'fn', 'if', 'for', 'ret'}
                if var_name in vl_keywords:
                    new_name = f'{var_name}_var'
                    self.renamed_vars[var_name] = new_name
                    var_name = new_name
                value = self._convert_expression(node.value)
                self.output.append(f"{self._indent()}{var_name}={value}")
            elif isinstance(target, ast.Subscript):
                # Array/object indexing
                obj = self._convert_expression(target.value)
                index = self._convert_expression(target.slice)
                value = self._convert_expression(node.value)
                self.output.append(f"{self._indent()}{obj}[{index}]={value}")
    
    def _convert_aug_assignment(self, node: ast.AugAssign) -> None:
        """Convert augmented assignment (+=, -=, etc.)"""
        if isinstance(node.target, ast.Name):
            var_name = node.target.id
            # Use renamed variable if it exists
            if var_name in self.renamed_vars:
                var_name = self.renamed_vars[var_name]
            op = self._convert_operator(node.op)
            value = self._convert_expression(node.value)
            self.output.append(f"{self._indent()}{var_name}{op}={value}")
    
    def _convert_expr_statement(self, node: ast.Expr) -> None:
        """Convert expression statement"""
        expr = self._convert_expression(node.value)
        self.output.append(f"{self._indent()}{expr}")
    
    def _convert_if(self, node: ast.If) -> None:
        """Convert if statement to VL"""
        # Check if this is a simple if-return pattern (can be inline)
        if (len(node.body) == 1 and isinstance(node.body[0], ast.Return) and
            len(node.orelse) == 1 and isinstance(node.orelse[0], ast.Return)):
            # Convert to inline ternary: if:condition?value:other
            condition = self._convert_expression(node.test)
            true_val = self._convert_expression(node.body[0].value) if node.body[0].value else ''
            false_val = self._convert_expression(node.orelse[0].value) if node.orelse[0].value else ''
            self.output.append(f"{self._indent()}ret:if:{condition}?{true_val}:{false_val}")
        else:
            # Multi-line if/else
            condition = self._convert_expression(node.test)
            self.output.append(f"{self._indent()}if:{condition}")
            
            self.indent_level += 1
            for stmt in node.body:
                self._convert_statement(stmt)
            self.indent_level -= 1
            
            if node.orelse:
                self.output.append(f"{self._indent()}else:")
                self.indent_level += 1
                for stmt in node.orelse:
                    self._convert_statement(stmt)
                self.indent_level -= 1
    
    def _convert_while(self, node: ast.While) -> None:
        """Convert while loop to VL"""
        condition = self._convert_expression(node.test)
        self.output.append(f"{self._indent()}while:{condition}")
        
        self.indent_level += 1
        for stmt in node.body:
            self._convert_statement(stmt)
        self.indent_level -= 1
    
    def _convert_for(self, node: ast.For) -> None:
        """Convert for loop to VL"""
        if isinstance(node.target, ast.Name):
            var_name = node.target.id
            iterable = self._convert_expression(node.iter)
            # VL syntax: for:var,iterable
            self.output.append(f"{self._indent()}for:{var_name},{iterable}")
            
            self.indent_level += 1
            for stmt in node.body:
                self._convert_statement(stmt)
            self.indent_level -= 1
    
    def _convert_return(self, node: ast.Return) -> None:
        """Convert return statement"""
        if node.value:
            value = self._convert_expression(node.value)
            self.output.append(f"{self._indent()}ret:{value}")
        else:
            self.output.append(f"{self._indent()}ret:")
    
    def _convert_expression(self, expr: ast.AST) -> str:
        """Convert Python expression to VL"""
        if isinstance(expr, ast.Constant):
            return self._convert_constant(expr)
        elif isinstance(expr, ast.Name):
            # Check if this is a parameter name that needs mapping
            if expr.id in self.param_map:
                return self.param_map[expr.id]
            # Check if this is a renamed variable
            if expr.id in self.renamed_vars:
                return self.renamed_vars[expr.id]
            return expr.id
        elif isinstance(expr, ast.BinOp):
            return self._convert_binop(expr)
        elif isinstance(expr, ast.Compare):
            return self._convert_compare(expr)
        elif isinstance(expr, ast.BoolOp):
            return self._convert_boolop(expr)
        elif isinstance(expr, ast.UnaryOp):
            return self._convert_unaryop(expr)
        elif isinstance(expr, ast.Call):
            return self._convert_call(expr)
        elif isinstance(expr, ast.List):
            return self._convert_list(expr)
        elif isinstance(expr, ast.Dict):
            return self._convert_dict(expr)
        elif isinstance(expr, ast.Subscript):
            return self._convert_subscript(expr)
        elif isinstance(expr, ast.ListComp):
            return self._convert_list_comprehension(expr)
        elif isinstance(expr, ast.Attribute):
            return self._convert_attribute(expr)
        elif isinstance(expr, ast.Tuple):
            # Tuples not directly supported - convert to array
            elements = [self._convert_expression(e) for e in expr.elts]
            return f"[{','.join(elements)}]"
        else:
            return f"# TODO: Unsupported expression: {type(expr).__name__}"
    
    def _convert_constant(self, node: ast.Constant) -> str:
        """Convert constant value"""
        value = node.value
        if isinstance(value, str):
            # Escape quotes
            escaped = value.replace("'", "\\'")
            return f"'{escaped}'"
        elif isinstance(value, bool):
            return 'true' if value else 'false'
        elif value is None:
            return 'null'
        else:
            return str(value)
    
    def _convert_binop(self, node: ast.BinOp) -> str:
        """Convert binary operation"""
        left = self._convert_expression(node.left)
        right = self._convert_expression(node.right)
        op = self._convert_operator(node.op)
        return f"{left}{op}{right}"
    
    def _convert_compare(self, node: ast.Compare) -> str:
        """Convert comparison"""
        left = self._convert_expression(node.left)
        
        # Handle 'in' operator
        if isinstance(node.ops[0], ast.In):
            right = self._convert_expression(node.comparators[0])
            # VL syntax: in:element,container
            return f"in:{left},{right}"
        
        op = self._convert_comparator(node.ops[0])
        right = self._convert_expression(node.comparators[0])
        return f"{left}{op}{right}"
    
    def _convert_boolop(self, node: ast.BoolOp) -> str:
        """Convert boolean operation (and/or)"""
        op = '&&' if isinstance(node.op, ast.And) else '||'
        values = [self._convert_expression(v) for v in node.values]
        return f"({op.join(values)})"
    
    def _convert_unaryop(self, node: ast.UnaryOp) -> str:
        """Convert unary operation"""
        operand = self._convert_expression(node.operand)
        if isinstance(node.op, ast.Not):
            return f"!{operand}"
        elif isinstance(node.op, ast.USub):
            return f"-{operand}"
        elif isinstance(node.op, ast.UAdd):
            return f"+{operand}"
        return operand
    
    def _convert_call(self, node: ast.Call) -> str:
        """Convert function call"""
        func_name = self._convert_expression(node.func)
        args = [self._convert_expression(arg) for arg in node.args]
        
        if args:
            args_str = ','.join(args)
            return f"{func_name}({args_str})"
        else:
            return f"{func_name}()"
    
    def _convert_list(self, node: ast.List) -> str:
        """Convert list literal"""
        elements = [self._convert_expression(e) for e in node.elts]
        return f"[{','.join(elements)}]"
    
    def _convert_dict(self, node: ast.Dict) -> str:
        """Convert dict literal"""
        pairs = []
        for key, value in zip(node.keys, node.values):
            key_str = self._convert_expression(key)
            value_str = self._convert_expression(value)
            pairs.append(f"{key_str}:{value_str}")
        return f"{{{','.join(pairs)}}}"
    
    def _convert_subscript(self, node: ast.Subscript) -> str:
        """Convert subscript (array/object access)"""
        value = self._convert_expression(node.value)
        # Handle division in subscript
        if isinstance(node.slice, ast.BinOp):
            index = self._convert_expression(node.slice)
            # Wrap complex expressions in parens
            return f"{value}[{index}]"
        index = self._convert_expression(node.slice)
        return f"{value}[{index}]"
    
    def _convert_list_comprehension(self, node: ast.ListComp) -> str:
        """Convert list comprehension - use built-in Python list comp syntax"""
        # VL supports Python passthrough for complex expressions
        # Generate the Python list comprehension directly
        if len(node.generators) == 1:
            gen = node.generators[0]
            if isinstance(gen.target, ast.Name):
                var_name = gen.target.id
                iterable = self._convert_expression(gen.iter)
                expr = self._convert_expression(node.elt)
                
                # Generate Python-style list comprehension
                if gen.ifs:
                    condition = self._convert_expression(gen.ifs[0])
                    return f"[{expr} for {var_name} in {iterable} if {condition}]"
                else:
                    return f"[{expr} for {var_name} in {iterable}]"
        
        # Fallback for complex comprehensions
        return "[item for item in []]"  # Empty list as fallback
    
    def _convert_attribute(self, node: ast.Attribute) -> str:
        """Convert attribute access (e.g., obj.attr)"""
        value = self._convert_expression(node.value)
        attr = node.attr
        return f"{value}.{attr}"
    
    def _convert_operator(self, op: ast.AST) -> str:
        """Convert operator to VL syntax"""
        if isinstance(op, ast.Add):
            return '+'
        elif isinstance(op, ast.Sub):
            return '-'
        elif isinstance(op, ast.Mult):
            return '*'
        elif isinstance(op, ast.Div):
            return '/'
        elif isinstance(op, ast.FloorDiv):
            # Floor division - wrap in parens to avoid ambiguity
            return '//'
        elif isinstance(op, ast.Mod):
            return '%'
        elif isinstance(op, ast.Pow):
            return '**'
        else:
            return '?'
    
    def _convert_comparator(self, op: ast.AST) -> str:
        """Convert comparison operator"""
        if isinstance(op, ast.Eq):
            return '=='
        elif isinstance(op, ast.NotEq):
            return '!='
        elif isinstance(op, ast.Lt):
            return '<'
        elif isinstance(op, ast.LtE):
            return '<='
        elif isinstance(op, ast.Gt):
            return '>'
        elif isinstance(op, ast.GtE):
            return '>='
        else:
            return '?'
    
    def _convert_type_annotation(self, annotation: ast.AST) -> str:
        """Convert Python type annotation to VL type (single-char format)"""
        if isinstance(annotation, ast.Name):
            type_map = {
                'str': 'S',
                'int': 'I',
                'float': 'N',
                'bool': 'B',
                'list': 'A',
                'dict': 'O',
                'Any': 'any',
                'None': 'V',
                'void': 'V'
            }
            return type_map.get(annotation.id, 'any')
        elif isinstance(annotation, ast.Subscript):
            # Handle List[T], Dict[K, V], etc.
            if isinstance(annotation.value, ast.Name):
                if annotation.value.id in ['List', 'list']:
                    return 'A'
                elif annotation.value.id in ['Dict', 'dict']:
                    return 'O'
        return 'any'
    
    def _convert_with(self, node: ast.With) -> None:
        """Convert with statement using py: passthrough - use @@@ as line separator"""
        # Convert the entire with block to Python code
        python_code = ast.unparse(node)
        # Use @@@ as line separator (@ is a valid VL token)
        single_line = python_code.replace('\n', '@@@').replace('    ', '  ')
        self.output.append(f"{self._indent()}py:{single_line}")
    
    def _convert_try(self, node: ast.Try) -> None:
        """Convert try/except statement using py: passthrough - use @@@ as line separator"""
        # Convert the entire try block to Python code
        python_code = ast.unparse(node)
        # Use @@@ as line separator
        single_line = python_code.replace('\n', '@@@').replace('    ', '  ')
        self.output.append(f"{self._indent()}py:{single_line}")
    
    def _embed_python_block(self, python_code: str) -> None:
        """Embed a block of Python code in VL using Python passthrough"""
        # Split into lines and add proper indentation
        lines = python_code.split('\n')
        for line in lines:
            if line.strip():  # Skip empty lines
                self.output.append(f"{self._indent()}{line}")
    
    def _indent(self) -> str:
        """Get current indentation"""
        return '  ' * self.indent_level


def convert_python_to_vl(python_code: str) -> str:
    """
    Convenience function to convert Python code to VL
    
    Args:
        python_code: Python source code as string
        
    Returns:
        VL source code as string
    """
    converter = PythonToVLConverter()
    return converter.convert(python_code)


if __name__ == '__main__':
    # Test the converter
    test_code = """
def add(x: int, y: int) -> int:
    return x + y

def greet(name: str) -> str:
    message = 'Hello, ' + name
    return message

result = add(5, 3)
print(result)
"""
    
    converter = PythonToVLConverter()
    vl_code = converter.convert(test_code)
    print(vl_code)
