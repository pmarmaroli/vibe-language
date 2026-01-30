"""
VL Parser

Converts tokens from the lexer into an Abstract Syntax Tree (AST).
Uses recursive descent parsing.
"""

from typing import List, Optional, Union
from lexer import Token, TokenType, tokenize
from ast_nodes import *


class ParseError(Exception):
    """Parser error with location information"""
    def __init__(self, message: str, token: Token):
        self.message = message
        self.token = token
        super().__init__(f"{message} at {token.line}:{token.column}")


class Parser:
    """VL Parser - converts tokens to AST"""
    
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
        self.current_token = self.tokens[0] if tokens else None
    
    def error(self, message: str) -> ParseError:
        """Create parse error with current token location"""
        return ParseError(message, self.current_token)
    
    def peek(self, offset: int = 0) -> Optional[Token]:
        """Look ahead at token without consuming"""
        pos = self.pos + offset
        if pos < len(self.tokens):
            return self.tokens[pos]
        return None
    
    def advance(self) -> Token:
        """Move to next token"""
        token = self.current_token
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current_token = self.tokens[self.pos]
        else:
            self.current_token = None
        return token
    
    def expect(self, token_type: TokenType) -> Token:
        """Consume token of expected type or raise error"""
        if self.current_token and self.current_token.type == token_type:
            return self.advance()
        raise self.error(f"Expected {token_type.name}, got {self.current_token.type.name if self.current_token else 'EOF'}")
    
    def match(self, *token_types: TokenType) -> bool:
        """Check if current token matches any of the given types"""
        if not self.current_token:
            return False
        return self.current_token.type in token_types
    
    def skip_newlines(self):
        """Skip newline tokens"""
        while self.current_token and self.current_token.type == TokenType.NEWLINE:
            self.advance()
    
    # Main parsing methods
    
    def parse(self) -> Program:
        """Parse entire VL program"""
        self.skip_newlines()
        
        # Parse metadata (optional)
        metadata = None
        if self.match(TokenType.META):
            metadata = self.parse_metadata()
            self.skip_newlines()
        
        # Parse dependencies (optional)
        dependencies = None
        if self.match(TokenType.DEPS):
            dependencies = self.parse_dependencies()
            self.skip_newlines()
        
        # Parse statements
        statements = []
        while self.current_token and self.current_token.type not in (TokenType.EXPORT, TokenType.EOF):
            if self.current_token.type == TokenType.NEWLINE:
                self.skip_newlines()
                continue
            
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
            self.skip_newlines()
        
        # Parse export (optional)
        export = None
        if self.match(TokenType.EXPORT):
            export = self.parse_export()
        
        return Program(
            line=1, column=1,
            metadata=metadata,
            dependencies=dependencies,
            statements=statements,
            export=export
        )
    
    def parse_metadata(self) -> Metadata:
        """Parse: meta:name,type,target"""
        token = self.expect(TokenType.META)
        self.expect(TokenType.COLON)
        
        name = self.expect(TokenType.IDENTIFIER).value
        self.expect(TokenType.COMMA)
        
        prog_type = self.expect(TokenType.IDENTIFIER).value
        self.expect(TokenType.COMMA)
        
        target = self.expect(TokenType.IDENTIFIER).value
        
        return Metadata(
            line=token.line, column=token.column,
            name=name,
            program_type=prog_type,
            target_language=target
        )
    
    def parse_dependencies(self) -> Dependencies:
        """Parse: deps:lib or deps:[lib1,lib2]"""
        token = self.expect(TokenType.DEPS)
        self.expect(TokenType.COLON)
        
        deps = []
        
        if self.match(TokenType.LBRACKET):
            # Array of dependencies
            self.advance()
            while not self.match(TokenType.RBRACKET):
                deps.append(self.expect(TokenType.IDENTIFIER).value)
                if self.match(TokenType.COMMA):
                    self.advance()
            self.expect(TokenType.RBRACKET)
        else:
            # Single dependency
            deps.append(self.expect(TokenType.IDENTIFIER).value)
        
        return Dependencies(
            line=token.line, column=token.column,
            dependencies=deps
        )
    
    def parse_export(self) -> Export:
        """Parse: export:name"""
        token = self.expect(TokenType.EXPORT)
        self.expect(TokenType.COLON)
        name = self.expect(TokenType.IDENTIFIER).value
        
        return Export(
            line=token.line, column=token.column,
            name=name
        )
    
    def parse_statement(self) -> Optional[Statement]:
        """Parse a single statement"""
        if not self.current_token:
            return None
        
        # Function definition
        if self.match(TokenType.FN):
            return self.parse_function_def()
        
        # Variable definition
        elif self.match(TokenType.VAR):
            return self.parse_variable_def()
        
        # Return statement
        elif self.match(TokenType.RET):
            return self.parse_return_stmt()
        
        # If statement (conditional)
        elif self.match(TokenType.IF):
            return self.parse_if_stmt()
        
        # For loop
        elif self.match(TokenType.FOR):
            return self.parse_for_loop()
        
        # While loop
        elif self.match(TokenType.WHILE):
            return self.parse_while_loop()
        
        # API call
        elif self.match(TokenType.API, TokenType.ASYNC):
            return self.parse_api_call()
        
        # UI component
        elif self.match(TokenType.UI):
            return self.parse_ui_component()
        
        # Data pipeline
        elif self.match(TokenType.DATA):
            return self.parse_data_pipeline()
        
        # File operation
        elif self.match(TokenType.FILE):
            return self.parse_file_operation()
        
        else:
            raise self.error(f"Unexpected token: {self.current_token.type.name}")
    
    def parse_function_def(self) -> FunctionDef:
        """Parse: fn:name|i:type,type|o:type|body"""
        token = self.expect(TokenType.FN)
        self.expect(TokenType.COLON)
        
        name = self.expect(TokenType.IDENTIFIER).value
        self.expect(TokenType.PIPE)
        
        # Parse inputs
        self.expect(TokenType.INPUT)
        self.expect(TokenType.COLON)
        input_types = self.parse_type_list()
        self.expect(TokenType.PIPE)
        
        # Parse output
        self.expect(TokenType.OUTPUT)
        self.expect(TokenType.COLON)
        output_type = self.parse_type()
        self.expect(TokenType.PIPE)
        
        # Parse body (statements separated by |)
        body = []
        while not self.match(TokenType.NEWLINE, TokenType.EOF, TokenType.EXPORT):
            stmt = self.parse_statement()
            if stmt:
                body.append(stmt)
            
            # Check for pipe separator or end
            if self.match(TokenType.PIPE):
                self.advance()
            else:
                break
        
        return FunctionDef(
            line=token.line, column=token.column,
            name=name,
            input_types=input_types,
            output_type=output_type,
            body=body
        )
    
    def parse_type_list(self) -> List[Type]:
        """Parse comma-separated types"""
        types = []
        types.append(self.parse_type())
        
        while self.match(TokenType.COMMA):
            self.advance()
            types.append(self.parse_type())
        
        return types
    
    def parse_type(self) -> Type:
        """Parse a type annotation"""
        token = self.current_token
        
        # Check for type tokens
        if self.match(TokenType.TYPE_INT, TokenType.TYPE_FLOAT, TokenType.TYPE_STR,
                     TokenType.TYPE_BOOL, TokenType.TYPE_ARR, TokenType.TYPE_OBJ,
                     TokenType.TYPE_ANY, TokenType.TYPE_VOID, TokenType.TYPE_PROMISE,
                     TokenType.TYPE_FUNC, TokenType.TYPE_MAP, TokenType.TYPE_SET):
            type_token = self.advance()
            return Type(
                line=token.line, column=token.column,
                name=type_token.value
            )
        
        raise self.error(f"Expected type, got {token.type.name}")
    
    def parse_variable_def(self) -> VariableDef:
        """Parse: v:name=value or v:name:type=value"""
        token = self.expect(TokenType.VAR)
        self.expect(TokenType.COLON)
        
        name = self.expect(TokenType.IDENTIFIER).value
        
        # Optional type annotation
        type_annotation = None
        if self.match(TokenType.COLON):
            self.advance()
            type_annotation = self.parse_type()
        
        self.expect(TokenType.EQUALS)
        value = self.parse_expression()
        
        return VariableDef(
            line=token.line, column=token.column,
            name=name,
            type_annotation=type_annotation,
            value=value
        )
    
    def parse_return_stmt(self) -> ReturnStmt:
        """Parse: ret:value"""
        token = self.expect(TokenType.RET)
        self.expect(TokenType.COLON)
        value = self.parse_expression()
        
        return ReturnStmt(
            line=token.line, column=token.column,
            value=value
        )
    
    def parse_if_stmt(self) -> IfStmt:
        """Parse: if:condition?true_expr:false_expr"""
        token = self.expect(TokenType.IF)
        self.expect(TokenType.COLON)
        
        condition = self.parse_expression()
        self.expect(TokenType.QUESTION)
        
        true_expr = self.parse_expression()
        self.expect(TokenType.COLON)
        
        false_expr = self.parse_expression()
        
        return IfStmt(
            line=token.line, column=token.column,
            condition=condition,
            true_expr=true_expr,
            false_expr=false_expr
        )
    
    def parse_for_loop(self) -> ForLoop:
        """Parse: for:var,iterable|body"""
        token = self.expect(TokenType.FOR)
        self.expect(TokenType.COLON)
        
        variable = self.expect(TokenType.IDENTIFIER).value
        self.expect(TokenType.COMMA)
        
        iterable = self.parse_expression()
        self.expect(TokenType.PIPE)
        
        body = []
        while not self.match(TokenType.NEWLINE, TokenType.EOF, TokenType.PIPE):
            stmt = self.parse_statement()
            if stmt:
                body.append(stmt)
            if self.match(TokenType.PIPE):
                break
        
        return ForLoop(
            line=token.line, column=token.column,
            variable=variable,
            iterable=iterable,
            body=body
        )
    
    def parse_while_loop(self) -> WhileLoop:
        """Parse: while:condition|body"""
        token = self.expect(TokenType.WHILE)
        self.expect(TokenType.COLON)
        
        condition = self.parse_expression()
        self.expect(TokenType.PIPE)
        
        body = []
        while not self.match(TokenType.NEWLINE, TokenType.EOF, TokenType.PIPE):
            stmt = self.parse_statement()
            if stmt:
                body.append(stmt)
            if self.match(TokenType.PIPE):
                break
        
        return WhileLoop(
            line=token.line, column=token.column,
            condition=condition,
            body=body
        )
    
    def parse_api_call(self) -> APICall:
        """Parse: api:METHOD,endpoint[,options] or async|api:..."""
        is_async = False
        if self.match(TokenType.ASYNC):
            is_async = True
            self.advance()
            self.expect(TokenType.PIPE)
        
        token = self.expect(TokenType.API)
        self.expect(TokenType.COLON)
        
        method = self.expect(TokenType.IDENTIFIER).value
        self.expect(TokenType.COMMA)
        
        endpoint = self.parse_expression()
        
        options = None
        if self.match(TokenType.COMMA):
            self.advance()
            options = self.parse_expression()  # Should be ObjectLiteral
        
        return APICall(
            line=token.line, column=token.column,
            method=method,
            endpoint=endpoint,
            options=options,
            is_async=is_async
        )
    
    def parse_ui_component(self) -> UIComponent:
        """Parse: ui:name|props:...|state:...|body"""
        token = self.expect(TokenType.UI)
        self.expect(TokenType.COLON)
        
        name = self.expect(TokenType.IDENTIFIER).value
        self.expect(TokenType.PIPE)
        
        # Parse props (optional)
        props = []
        if self.match(TokenType.PROPS):
            self.advance()
            self.expect(TokenType.COLON)
            # Parse props list
            # TODO: Implement prop parsing
            self.expect(TokenType.PIPE)
        
        # Parse state (optional)
        state_vars = []
        if self.match(TokenType.STATE):
            self.advance()
            self.expect(TokenType.COLON)
            # Parse state list
            # TODO: Implement state parsing
            self.expect(TokenType.PIPE)
        
        # Parse body
        body = []
        while not self.match(TokenType.NEWLINE, TokenType.EOF, TokenType.EXPORT):
            if self.match(TokenType.PIPE):
                self.advance()
                continue
            stmt = self.parse_statement()
            if stmt:
                body.append(stmt)
        
        return UIComponent(
            line=token.line, column=token.column,
            name=name,
            props=props,
            state_vars=state_vars,
            body=body
        )
    
    def parse_data_pipeline(self) -> DataPipeline:
        """Parse: data:source|operation|operation|..."""
        token = self.expect(TokenType.DATA)
        self.expect(TokenType.COLON)
        
        source = self.parse_expression()
        
        operations = []
        while self.match(TokenType.PIPE) and not self.match(TokenType.NEWLINE, TokenType.EOF):
            self.advance()
            
            # Parse data operations
            if self.match(TokenType.FILTER):
                self.advance()
                self.expect(TokenType.COLON)
                condition = self.parse_expression()
                operations.append(FilterOp(
                    line=self.current_token.line,
                    column=self.current_token.column,
                    condition=condition
                ))
            elif self.match(TokenType.MAP):
                self.advance()
                self.expect(TokenType.COLON)
                # TODO: Parse map operation
                pass
            elif self.match(TokenType.GROUPBY):
                self.advance()
                self.expect(TokenType.COLON)
                field = self.expect(TokenType.IDENTIFIER).value
                operations.append(GroupByOp(
                    line=self.current_token.line,
                    column=self.current_token.column,
                    field=field
                ))
            # Add more operations...
        
        return DataPipeline(
            line=token.line, column=token.column,
            source=source,
            operations=operations
        )
    
    def parse_file_operation(self) -> FileOperation:
        """Parse: file:operation,path[,args]"""
        token = self.expect(TokenType.FILE)
        self.expect(TokenType.COLON)
        
        operation = self.expect(TokenType.IDENTIFIER).value
        self.expect(TokenType.COMMA)
        
        path = self.parse_expression()
        
        arguments = []
        while self.match(TokenType.COMMA):
            self.advance()
            arguments.append(self.parse_expression())
        
        return FileOperation(
            line=token.line, column=token.column,
            operation=operation,
            path=path,
            arguments=arguments
        )
    
    def parse_expression(self) -> Expression:
        """Parse an expression"""
        return self.parse_comparison()
    
    def parse_comparison(self) -> Expression:
        """Parse comparison operators"""
        left = self.parse_term()
        
        while self.match(TokenType.EQUAL, TokenType.NOT_EQUAL, TokenType.LESS_THAN,
                         TokenType.GREATER_THAN, TokenType.LESS_EQUAL, TokenType.GREATER_EQUAL):
            op_token = self.advance()
            right = self.parse_term()
            left = Operation(
                line=op_token.line, column=op_token.column,
                operator=op_token.value,
                operands=[left, right]
            )
        
        return left
    
    def parse_term(self) -> Expression:
        """Parse addition/subtraction"""
        left = self.parse_factor()
        
        while self.match(TokenType.PLUS, TokenType.MINUS):
            op_token = self.advance()
            right = self.parse_factor()
            left = Operation(
                line=op_token.line, column=op_token.column,
                operator=op_token.value,
                operands=[left, right]
            )
        
        return left
    
    def parse_factor(self) -> Expression:
        """Parse multiplication/division"""
        left = self.parse_unary()
        
        while self.match(TokenType.MULTIPLY, TokenType.DIVIDE, TokenType.MODULO):
            op_token = self.advance()
            right = self.parse_unary()
            left = Operation(
                line=op_token.line, column=op_token.column,
                operator=op_token.value,
                operands=[left, right]
            )
        
        return left
    
    def parse_unary(self) -> Expression:
        """Parse unary operators"""
        if self.match(TokenType.MINUS, TokenType.NOT):
            op_token = self.advance()
            operand = self.parse_unary()
            return Operation(
                line=op_token.line, column=op_token.column,
                operator=op_token.value,
                operands=[operand]
            )
        
        return self.parse_primary()
    
    def parse_primary(self) -> Expression:
        """Parse primary expressions (literals, identifiers, etc.)"""
        token = self.current_token
        
        # Number literal
        if self.match(TokenType.NUMBER):
            self.advance()
            value = float(token.value) if '.' in token.value else int(token.value)
            return NumberLiteral(
                line=token.line, column=token.column,
                value=value
            )
        
        # String literal
        if self.match(TokenType.STRING):
            self.advance()
            is_template = '${' in token.value
            return StringLiteral(
                line=token.line, column=token.column,
                value=token.value,
                is_template=is_template
            )
        
        # Variable reference ($var)
        if self.match(TokenType.DOLLAR):
            self.advance()
            name = self.expect(TokenType.IDENTIFIER).value
            return VariableRef(
                line=token.line, column=token.column,
                name=name
            )
        
        # Operation (op:+(...))
        if self.match(TokenType.OP):
            return self.parse_operation_expr()
        
        # Identifier (variable or function name)
        if self.match(TokenType.IDENTIFIER):
            name = self.advance().value
            
            # Function call
            if self.match(TokenType.LPAREN):
                self.advance()
                args = []
                while not self.match(TokenType.RPAREN):
                    args.append(self.parse_expression())
                    if self.match(TokenType.COMMA):
                        self.advance()
                self.expect(TokenType.RPAREN)
                
                return FunctionCall(
                    line=token.line, column=token.column,
                    name=name,
                    arguments=args
                )
            
            # Just identifier
            return Identifier(
                line=token.line, column=token.column,
                name=name
            )
        
        # Parenthesized expression
        if self.match(TokenType.LPAREN):
            self.advance()
            expr = self.parse_expression()
            self.expect(TokenType.RPAREN)
            return expr
        
        # Array literal
        if self.match(TokenType.LBRACKET):
            return self.parse_array_literal()
        
        # Object literal
        if self.match(TokenType.LBRACE):
            return self.parse_object_literal()
        
        raise self.error(f"Unexpected token in expression: {token.type.name}")
    
    def parse_operation_expr(self) -> Operation:
        """Parse: op:operator(arg1,arg2,...)"""
        token = self.expect(TokenType.OP)
        self.expect(TokenType.COLON)
        
        # Get operator
        op = self.advance().value
        
        # Parse arguments
        self.expect(TokenType.LPAREN)
        operands = []
        while not self.match(TokenType.RPAREN):
            operands.append(self.parse_expression())
            if self.match(TokenType.COMMA):
                self.advance()
        self.expect(TokenType.RPAREN)
        
        return Operation(
            line=token.line, column=token.column,
            operator=op,
            operands=operands
        )
    
    def parse_array_literal(self) -> ArrayLiteral:
        """Parse: [1,2,3]"""
        token = self.expect(TokenType.LBRACKET)
        
        elements = []
        while not self.match(TokenType.RBRACKET):
            elements.append(self.parse_expression())
            if self.match(TokenType.COMMA):
                self.advance()
        
        self.expect(TokenType.RBRACKET)
        
        return ArrayLiteral(
            line=token.line, column=token.column,
            elements=elements
        )
    
    def parse_object_literal(self) -> ObjectLiteral:
        """Parse: {key:value,key2:value2}"""
        token = self.expect(TokenType.LBRACE)
        
        pairs = []
        while not self.match(TokenType.RBRACE):
            key = self.expect(TokenType.IDENTIFIER).value
            self.expect(TokenType.COLON)
            value = self.parse_expression()
            pairs.append((key, value))
            
            if self.match(TokenType.COMMA):
                self.advance()
        
        self.expect(TokenType.RBRACE)
        
        return ObjectLiteral(
            line=token.line, column=token.column,
            pairs=pairs
        )


def parse(source: str) -> Program:
    """Convenience function to parse VL source code"""
    tokens = tokenize(source)
    parser = Parser(tokens)
    return parser.parse()


if __name__ == "__main__":
    # Test the parser
    test_code = """
fn:sum|i:int,int|o:int|ret:op:+(i0,i1)
    """
    
    try:
        ast = parse(test_code)
        print(ast_to_string(ast))
    except ParseError as e:
        print(f"Parse Error: {e}")
