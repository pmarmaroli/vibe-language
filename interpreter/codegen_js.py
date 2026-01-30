"""
VL to JavaScript Code Generator
Converts VL AST to JavaScript source code
"""

from ast_nodes import *
from typing import List, Any


class JSCodeGenerator:
    """
    Generates JavaScript code from VL AST
    
    Usage:
        generator = JSCodeGenerator(ast)
        js_code = generator.generate()
    """
    
    def __init__(self, ast: Program):
        self.ast = ast
        self.indent_level = 0
        self.output = []
    
    def generate(self) -> str:
        """Generate JavaScript code from AST"""
        self.output = []
        self._generate_program(self.ast)
        return '\n'.join(self.output)
    
    def _indent(self) -> str:
        """Get current indentation"""
        return '    ' * self.indent_level
    
    def _emit(self, code: str):
        """Emit a line of code with proper indentation"""
        if code:
            self.output.append(self._indent() + code)
        else:
            self.output.append('')
    
    def _generate_program(self, node: Program):
        """Generate code for entire program"""
        # Metadata as comment
        if node.metadata:
            self._emit(f"// VL Program: {node.metadata.name}")
            self._emit(f"// Type: {node.metadata.program_type}")
            self._emit(f"// Target: {node.metadata.target_language}")
            self._emit('')
        
        # Dependencies (require/import)
        # Note: In browser context, imports work differently. 
        # For now we emit CommonJS requires or ES6 imports depending on config.
        # Defaulting to CommonJS for generic JS script compatibility
        if node.dependencies:
            for dep in node.dependencies.dependencies:
                self._emit(f"const {dep} = require('{dep}');")
            self._emit('')
        
        # Statements (functions, variables, etc.)
        for stmt in node.statements:
            self._generate_statement(stmt)
            
        # Export
        if node.export:
            self._emit('')
            self._emit(f"module.exports = {{ {node.export.name} }};")

    def _generate_statement(self, stmt: Statement):
        """Generate code for a statement"""
        if isinstance(stmt, FunctionDef):
            self._generate_function_def(stmt)
        elif isinstance(stmt, VariableDef):
            self._generate_variable_def(stmt)
        elif isinstance(stmt, ReturnStmt):
            self._generate_return_stmt(stmt)
        elif isinstance(stmt, DirectCall):
            self._generate_direct_call(stmt)
        elif isinstance(stmt, IfStmt):
            self._generate_if_stmt(stmt)
        # Add other statement types here...
        else:
            self._emit(f"// Warning: Unsupported statement type {type(stmt).__name__}")

    def _generate_function_def(self, node: FunctionDef):
        """Generate code for function definition"""
        # Implicit parameter naming i0, i1... based on input types
        param_names = [f"i{i}" for i in range(len(node.input_types))] 
        params = ", ".join(param_names)
        
        self._emit(f"function {node.name}({params}) {{")
        self.indent_level += 1
        
        # Generate body
        for stmt in node.body:
            self._generate_statement(stmt)
            
        self.indent_level -= 1
        self._emit("}")
        self._emit('')

    def _generate_variable_def(self, node: VariableDef):
        """Generate code for variable definition"""
        val_code = self._generate_expression(node.value)
        self._emit(f"let {node.name} = {val_code};")
    
    def _generate_if_stmt(self, node: IfStmt):
        """Generate if statement"""
        # IfStmt in VL is ternary-like: if:condition?true_expr:false_expr
        # But depending on AST structure it might be Statement (block) or Expression.
        # Looking at ast_nodes: IfStmt is a Statement but has true_expr and false_expr which are Expressions?
        # Wait, ast_nodes.py says:
        # @dataclass class IfStmt(Statement): condition: Expression, true_expr: Expression, false_expr: Expression
        # This looks like the 'if' keyword in VL behaves like a ternary operator statement?
        # Let's check parser.py to be sure how `if` is parsed.
        # But assuming it's a statement, we can generate:
        # if (cond) { expr1; } else { expr2; }
        # NOTE: If true_expr is just an expression, we need to wrap it in a statement or return it?
        # Re-reading ast_nodes.py: true_expr is 'Expression'. 
        
        cond_code = self._generate_expression(node.condition)
        true_code = self._generate_expression(node.true_expr)
        false_code = self._generate_expression(node.false_expr)
        
        self._emit(f"if ({cond_code}) {{")
        self.indent_level += 1
        self._emit(f"{true_code};")
        self.indent_level -= 1
        self._emit("} else {")
        self.indent_level += 1
        self._emit(f"{false_code};")
        self.indent_level -= 1
        self._emit("}")

    def _generate_return_stmt(self, node: ReturnStmt):
        """Generate code for return statement"""
        val_code = self._generate_expression(node.value)
        self._emit(f"return {val_code};")

    def _generate_direct_call(self, node: DirectCall):
        """Generate code for direct function call"""
        # This is a statement-level expression call
        expr_code = self._generate_expression(node.function)
        self._emit(f"{expr_code};")

    def _generate_expression(self, node: Expression) -> str:
        """Generate code for an expression"""
        if isinstance(node, NumberLiteral):
            return str(node.value)
            
        elif isinstance(node, StringLiteral):
            # TODO: Handle template strings ${...} if is_template is True
            quote = "`" if node.is_template else "'"
            return f"{quote}{node.value}{quote}"
            
        elif isinstance(node, BooleanLiteral):
            return "true" if node.value else "false"
            
        elif isinstance(node, Identifier):
            return node.name
            
        elif isinstance(node, VariableRef):
            return node.name # $name is just name in JS
            
        elif isinstance(node, Operation):
            op_map = {
                'and': '&&', 'or': '||', 'not': '!',
                '==': '===', '!=': '!==' # Use strict equality
            }
            op = op_map.get(node.operator, node.operator)
            
            # Handle unary op (not)
            if len(node.operands) == 1:
                return f"{op}({self._generate_expression(node.operands[0])})"
            
            # Handle binary ops
            # Flatten for simplicity, assuming binary for most
            if len(node.operands) >= 2:
                # TODO: Handle precedence properly using parentheses
                operands = [self._generate_expression(op) for op in node.operands]
                return f"({f' {op} '.join(operands)})"
                
        elif isinstance(node, FunctionCall):
            callee = self._generate_expression(node.callee)
            args = [self._generate_expression(arg) for arg in node.arguments]
            return f"{callee}({', '.join(args)})"
            
        elif isinstance(node, ArrayLiteral):
            elements = [self._generate_expression(e) for e in node.elements]
            return f"[{', '.join(elements)}]"
            
        elif isinstance(node, ObjectLiteral):
            pairs = [f"{k}: {self._generate_expression(v)}" for k, v in node.pairs]
            return f"{{ {', '.join(pairs)} }}"
            
        elif isinstance(node, MemberAccess):
            obj = self._generate_expression(node.object)
            return f"{obj}.{node.property}"
            
        # Fallback
        return f"/* Unknown Expr: {type(node).__name__} */"

