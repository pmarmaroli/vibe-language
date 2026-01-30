"""
VL to Python Code Generator
Converts VL AST to Python source code
"""

from ast_nodes import *
from typing import List, Any


class PythonCodeGenerator:
    """
    Generates Python code from VL AST
    
    Usage:
        generator = PythonCodeGenerator(ast)
        python_code = generator.generate()
    """
    
    def __init__(self, ast: Program):
        self.ast = ast
        self.indent_level = 0
        self.output = []
    
    def generate(self) -> str:
        """Generate Python code from AST"""
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
            self._emit(f"# VL Program: {node.metadata.name}")
            self._emit(f"# Type: {node.metadata.program_type}")
            self._emit(f"# Target: {node.metadata.target_language}")
            self._emit('')
        
        # Dependencies (imports)
        if node.dependencies:
            for dep in node.dependencies.dependencies:
                self._emit(f"import {dep}")
            self._emit('')
        
        # Statements (functions, variables, etc.)
        for stmt in node.statements:
            self._generate_statement(stmt)
            self._emit('')
        
        # Export (if any)
        if node.export:
            self._emit(f"# Exported: {node.export.name}")
    
    def _generate_statement(self, node):
        """Generate code for a statement"""
        if isinstance(node, FunctionDef):
            self._generate_function(node)
        elif isinstance(node, VariableDef):
            self._generate_variable(node)
        elif isinstance(node, CompoundAssignment):
            self._generate_compound_assignment(node)
        elif isinstance(node, ReturnStmt):
            self._generate_return(node)
        elif isinstance(node, DirectCall):
            self._generate_direct_call(node)
        elif isinstance(node, IfStmt):
            self._generate_if_stmt(node)
        elif isinstance(node, ForLoop):
            self._generate_for_loop(node)
        elif isinstance(node, WhileLoop):
            self._generate_while_loop(node)
        elif isinstance(node, APICall):
            self._generate_api_call(node)
        elif isinstance(node, DataPipeline):
            self._generate_data_pipeline(node)
        elif isinstance(node, FileOperation):
            self._generate_file_operation(node)
        elif isinstance(node, UIComponent):
            self._generate_ui_component(node)
        else:
            self._emit(f"# TODO: Unsupported statement type: {type(node).__name__}")
    
    def _generate_function(self, node: FunctionDef):
        """Generate Python function definition"""
        # Implicit parameter naming i0, i1... based on input types
        params = []
        for idx, typ in enumerate(node.input_types):
             params.append(f"i{idx}: {typ.name}")
        
        params_str = ', '.join(params)
        self._emit(f"def {node.name}({params_str}) -> {node.output_type.name}:")
        
        self.indent_level += 1
        
        # Function body
        if node.body:
            for stmt in node.body:
                self._generate_statement(stmt)
        else:
            self._emit("pass")
        
        self.indent_level -= 1
    
    def _generate_function_expr(self, node: FunctionExpr) -> str:
        """Generate Python lambda or inline function for function expressions"""
        # Implicit parameter naming i0, i1... based on input types
        params = ', '.join([f"i{idx}" for idx in range(len(node.input_types))])
        
        # For simple single-expression returns, use lambda
        if len(node.body) == 1 and isinstance(node.body[0], ReturnStmt):
            return_expr = self._generate_expression(node.body[0].value)
            return f"lambda {params}: {return_expr}"
        
        # For complex bodies, we'd need to define a function inline
        # For now, generate a lambda that calls a nested function pattern
        # This is a simplified implementation
        if node.body:
            # Try to generate as lambda if body is simple enough
            body_parts = []
            for stmt in node.body:
                if isinstance(stmt, ReturnStmt):
                    body_parts.append(self._generate_expression(stmt.value))
            if body_parts:
                return f"lambda {params}: {body_parts[-1]}"
        
        return f"lambda {params}: None  # Complex function body"
    
    def _generate_variable(self, node: VariableDef):
        """Generate Python variable assignment"""
        value = self._generate_expression(node.value)
        type_hint = f": {node.type_annotation.name}" if node.type_annotation else ""
        self._emit(f"{node.name}{type_hint} = {value}")
    
    def _generate_compound_assignment(self, node: CompoundAssignment):
        """Generate Python compound assignment (+=, -=, *=, /=)"""
        value = self._generate_expression(node.value)
        self._emit(f"{node.name} {node.operator}= {value}")
    
    def _generate_return(self, node: ReturnStmt):
        """Generate Python return statement"""
        value = self._generate_expression(node.value)
        self._emit(f"return {value}")
    
    def _generate_direct_call(self, node: DirectCall):
        """Generate Python direct function call (without assignment)"""
        function_code = self._generate_expression(node.function)
        self._emit(function_code)

    def _generate_if_stmt(self, node: IfStmt):
        """Generate Python if statement"""
        condition = self._generate_expression(node.condition)
        self._emit(f"if {condition}:")
        self.indent_level += 1
        # Handle both expressions and return statements
        if isinstance(node.true_expr, ReturnStmt):
            self._generate_return(node.true_expr)
        else:
            self._emit(self._generate_expression(node.true_expr))
        self.indent_level -= 1
        self._emit("else:")
        self.indent_level += 1
        if isinstance(node.false_expr, ReturnStmt):
            self._generate_return(node.false_expr)
        else:
            self._emit(self._generate_expression(node.false_expr))
        self.indent_level -= 1
    
    def _generate_for_loop(self, node: ForLoop):
        """Generate Python for loop"""
        iterable = self._generate_expression(node.iterable)
        self._emit(f"for {node.variable} in {iterable}:")
        
        self.indent_level += 1
        for stmt in node.body:
            self._generate_statement(stmt)
        self.indent_level -= 1
    
    def _generate_while_loop(self, node: WhileLoop):
        """Generate Python while loop"""
        condition = self._generate_expression(node.condition)
        self._emit(f"while {condition}:")
        
        self.indent_level += 1
        for stmt in node.body:
            self._generate_statement(stmt)
        self.indent_level -= 1
    
    def _generate_api_call(self, node: APICall):
        """Generate Python API call"""
        method = node.method.lower()
        endpoint = self._generate_expression(node.endpoint)
        self._emit(f"# API Call: {node.method}")
        self._emit(f"requests.{method}({endpoint})")
    
    def _generate_api_call_expr(self, node: APICall) -> str:
        """Generate API call as expression (for assignment/return)"""
        method = node.method.lower()
        endpoint = self._generate_expression(node.endpoint)
        return f"requests.{method}({endpoint})"

    def _generate_data_pipeline(self, node: DataPipeline):
        """Generate Python data processing pipeline"""
        source = self._generate_expression(node.source)
        self._emit(f"# Data pipeline from: {source}")
        self._emit(f"data = {source}")
        
        for op in node.operations:
            if isinstance(op, FilterOp):
                 self._emit(f"data = [x for x in data if {self._generate_expression(op.condition)}]")
            elif isinstance(op, MapOp):
                 if op.expression:
                     self._emit(f"data = [{self._generate_expression(op.expression)} for x in data]")
    
    def _generate_data_pipeline_expr(self, node: DataPipeline) -> str:
        """Generate data pipeline as an expression (for return statements)"""
        # Generate the source expression
        source_expr = self._generate_expression(node.source)
        
        # Build the pipeline by chaining comprehensions
        # Start with the source
        result = source_expr
        
        # Apply each operation in sequence
        for op in node.operations:
            if isinstance(op, FilterOp):
                condition = self._generate_expression(op.condition)
                result = f"[x for x in {result} if ({condition})]"
            elif isinstance(op, MapOp):
                if op.expression:
                    expr = self._generate_expression(op.expression)
                    result = f"[({expr}) for x in {result}]"
        
        return result
    
    def _generate_file_operation(self, node: FileOperation):
        """Generate Python file I/O operations"""
        op = node.operation
        path = self._generate_expression(node.path)
        
        if op == 'read':
            self._emit(f"with open({path}, 'r') as f:")
            self._emit(f"    content = f.read()")
        elif op == 'write':
            if node.arguments:
                content = self._generate_expression(node.arguments[0])
                self._emit(f"with open({path}, 'w') as f:")
                self._emit(f"    f.write({content})")
    
    def _generate_ui_component(self, node: UIComponent):
        """Generate React/UI component (basic support)"""
        self._emit(f"# UI Component: {node.name}")
        
        # Generate as a React functional component
        self._emit(f"def {node.name}(props):")
        self.indent_level += 1
        
        # Generate state hooks if any
        for state_name, state_type, state_value in node.state_vars:
            value = self._generate_expression(state_value) if state_value else "None"
            self._emit(f"# State: {state_name} = {value}")
        
        # Simple placeholder return
        self._emit(f"return None  # React JSX would go here")
        
        self.indent_level -= 1

    def _generate_expression(self, node: Expression) -> str:
        """Generate Python expression"""
        if isinstance(node, NumberLiteral):
            return str(node.value)
        
        elif isinstance(node, RangeExpr):
            start = self._generate_expression(node.start)
            end = self._generate_expression(node.end)
            return f"range({start}, {end})"
        
        elif isinstance(node, StringLiteral):
            if '${' in node.value:
                # Parse complex expressions in template strings
                result = self._process_string_template(node.value)
                return result
            else:
                return f"'{node.value}'"
        
        elif isinstance(node, BooleanLiteral):
            return 'True' if node.value else 'False'
        
        elif isinstance(node, Identifier):
            return node.name
        
        elif isinstance(node, VariableRef):
            return node.name 
        
        elif isinstance(node, FunctionCall):
            callee = self._generate_expression(node.callee)
            args = ', '.join([self._generate_expression(arg) for arg in node.arguments])
            return f"{callee}({args})"
            
        elif isinstance(node, MemberAccess):
            obj = self._generate_expression(node.object)
            return f"{obj}.{node.property}"

        elif isinstance(node, Operation):
            return self._generate_operation(node)
            
        elif isinstance(node, ArrayLiteral):
            elements = ', '.join([self._generate_expression(e) for e in node.elements])
            return f"[{elements}]"
        
        elif isinstance(node, ObjectLiteral):
            pair_strs = []
            for k, v in node.pairs:
                if isinstance(v, FunctionExpr):
                    # Generate lambda or method reference for function expressions
                    pair_strs.append(f"'{k}': {self._generate_function_expr(v)}")
                else:
                    pair_strs.append(f"'{k}': {self._generate_expression(v)}")
            return f"{{{', '.join(pair_strs)}}}"
        
        elif isinstance(node, FunctionExpr):
            return self._generate_function_expr(node)
        
        elif isinstance(node, IfStmt):
            # If statement can be used as expression (ternary)
            # Handle ReturnStmt in branches (can't be ternary if returns are involved)
            if isinstance(node.true_expr, ReturnStmt) or isinstance(node.false_expr, ReturnStmt):
                # This should be handled as a statement, not expression
                return "None  # ERROR: If with return branches should not be in expression context"
            condition = self._generate_expression(node.condition)
            true_val = self._generate_expression(node.true_expr)
            false_val = self._generate_expression(node.false_expr)
            return f"({true_val} if {condition} else {false_val})"
        
        elif isinstance(node, DataPipeline):
            # Data pipeline as expression
            return self._generate_data_pipeline_expr(node)
        
        elif isinstance(node, APICall):
            # API call as expression
            return self._generate_api_call_expr(node)
        
        else:
            return f"None # TODO: {type(node).__name__}"
    
    def _generate_operation(self, node: Operation) -> str:
        """Generate Python operation"""
        operator_map = {
            '+': '+', '-': '-', '*': '*', '/': '/', '%': '%',
            '**': '**', '==': '==', '!=': '!=',
            '<': '<', '>': '>', '<=': '<=', '>=': '>=',
            '&&': 'and', '||': 'or', '!': 'not',
        }
        
        op = operator_map.get(node.operator, node.operator)
        
        if len(node.operands) == 1:
            operand = self._generate_expression(node.operands[0])
            return f"{op} {operand}"
        elif len(node.operands) == 2:
            left = self._generate_expression(node.operands[0])
            right = self._generate_expression(node.operands[1])
            return f"({left} {op} {right})"
        else:
            operands = ', '.join([self._generate_expression(o) for o in node.operands])
            return f"{op}({operands})"
    
    def _process_string_template(self, template: str) -> str:
        """Process string template with complex VL expressions in ${...}"""
        import re
        from lexer import Lexer
        from parser import Parser
        
        result_parts = []
        last_end = 0
        
        # Find all ${...} blocks, respecting nesting
        i = 0
        while i < len(template):
            if i < len(template) - 1 and template[i:i+2] == '${':
                # Found start of interpolation
                # Add any literal text before this
                if i > last_end:
                    result_parts.append(repr(template[last_end:i]))
                
                # Find matching closing brace
                depth = 1
                j = i + 2
                while j < len(template) and depth > 0:
                    if template[j] == '{':
                        depth += 1
                    elif template[j] == '}':
                        depth -= 1
                    j += 1
                
                if depth == 0:
                    # Extract the VL expression
                    vl_expr = template[i+2:j-1]
                    
                    # Parse and generate Python code for it
                    try:
                        lexer = Lexer(vl_expr)
                        tokens = lexer.tokenize()
                        parser = Parser(tokens)
                        
                        # Parse as expression (could be if, op, identifier, etc.)
                        expr_node = parser.parse_expression()
                        py_expr = self._generate_expression(expr_node)
                        
                        result_parts.append(f"({py_expr})")
                    except Exception:
                        # Fallback to simple identifier
                        result_parts.append(f"{{{vl_expr}}}")
                    
                    last_end = j
                    i = j
                else:
                    i += 1
            else:
                i += 1
        
        # Add any remaining literal text
        if last_end < len(template):
            result_parts.append(repr(template[last_end:]))
        
        # Combine into Python f-string
        if len(result_parts) == 0:
            return "''"
        elif len(result_parts) == 1 and result_parts[0].startswith("'"):
            return result_parts[0]
        else:
            # Build f-string with proper formatting
            combined = 'f"' + ''.join([
                part[1:-1] if part.startswith("'") else '{' + part + '}'
                for part in result_parts
            ]) + '"'
            return combined


if __name__ == "__main__":
    # Test with a simple AST
    from ast_nodes import *
    
    # Create a simple function: fn:sum|i:int,int|o:int|ret:op:+(i0,i1)
    metadata = MetadataNode("sum_function", "function", "python")
    param1 = ParameterNode("i0", "int")
    param2 = ParameterNode("i1", "int")
    
    op_node = OperationNode("+", [
        IdentifierNode("i0"),
        IdentifierNode("i1")
    ])
    
    return_node = ReturnNode(op_node)
    
    func = FunctionDefNode(
        name="sum",
        parameters=[param1, param2],
        return_type="int",
        body=[return_node]
    )
    
    program = ProgramNode(
        metadata=metadata,
        dependencies=[],
        statements=[func],
        export="sum"
    )
    
    generator = PythonCodeGenerator(program)
    output = generator.generate()
    
    print("Generated Python code:")
    print(output)
