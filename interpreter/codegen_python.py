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
    
    def _generate_variable(self, node: VariableDef):
        """Generate Python variable assignment"""
        value = self._generate_expression(node.value)
        type_hint = f": {node.type_annotation.name}" if node.type_annotation else ""
        self._emit(f"{node.name}{type_hint} = {value}")
    
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
        self._emit(self._generate_expression(node.true_expr))
        self.indent_level -= 1
        self._emit("else:")
        self.indent_level += 1
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

    def _generate_expression(self, node: Expression) -> str:
        """Generate Python expression"""
        if isinstance(node, NumberLiteral):
            return str(node.value)
        
        elif isinstance(node, StringLiteral):
            if '${' in node.value:
                value = node.value.replace('${', '{')
                return f"f'{value}'"
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
            pairs = ', '.join([f"'{k}': {self._generate_expression(v)}" 
                              for k, v in node.pairs])
            return f"{{{pairs}}}"
        
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
