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
        self.parsing_pipeline_operation = False  # Flag to prevent nested pipeline parsing
    
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
        """Consume token of expected type or raise error with helpful message"""
        if self.current_token and self.current_token.type == token_type:
            return self.advance()
        
        # Build helpful error message with context
        got = self.current_token.type.name if self.current_token else 'EOF'
        line = self.current_token.line if self.current_token else '?'
        col = self.current_token.column if self.current_token else '?'
        
        error_msg = f"Expected {token_type.name}, got {got}"
        
        # Add context-specific suggestions
        suggestions = []
        if token_type == TokenType.PIPE:
            suggestions.append("VL uses | to separate statements and clauses")
            suggestions.append("Example: fn:name|i:int|o:int|ret:value")
        elif token_type == TokenType.COLON:
            suggestions.append("VL uses : after keywords")
            suggestions.append("Example: fn:name, v:var, ret:value")
        elif token_type == TokenType.IDENTIFIER:
            suggestions.append("Expected a variable or function name here")
            if got in ["INPUT", "OUTPUT", "DATA", "FILTER", "MAP"]:
                suggestions.append(f"'{got}' is a reserved keyword, try a different name")
        
        if suggestions:
            error_msg += f"\nHint: {suggestions[0]}"
            if len(suggestions) > 1:
                error_msg += f"\n      {suggestions[1]}"
        
        raise self.error(error_msg)
    
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
        loop_count = 0
        max_loops = 1000  # Safety limit
        while (self.current_token and self.current_token.type not in (TokenType.EXPORT, TokenType.EOF) and 
               loop_count < max_loops):
            loop_count += 1
            
            if self.current_token.type == TokenType.NEWLINE:
                self.skip_newlines()
                continue
            
            # Handle PIPE separator at top level (e.g. v:x=1|v:y=2)
            if self.match(TokenType.PIPE):
                self.advance()
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
        
        # Direct function call with @ syntax
        if self.match(TokenType.AT):
            return self.parse_direct_call()
        
        # Function definition
        if self.match(TokenType.FN):
            return self.parse_function_def()
        
        # Variable definition (explicit v: prefix)
        elif self.match(TokenType.VAR):
            return self.parse_variable_def()
        
        # Implicit variable definition: name=value (no v: prefix)
        # Also handles compound assignment: name+=value, name-=value, etc.
        # Also handles implicit function calls: func(args)
        elif self.match(TokenType.IDENTIFIER):
            next_tok = self.peek(1)
            if next_tok and next_tok.type in (TokenType.EQUALS, TokenType.PLUS_EQUALS, 
                                               TokenType.MINUS_EQUALS, TokenType.TIMES_EQUALS,
                                               TokenType.DIV_EQUALS):
                return self.parse_implicit_variable_or_compound()
            # Implicit function call: func(args) or obj.method(args)
            elif next_tok and next_tok.type in (TokenType.LPAREN, TokenType.DOT):
                return self.parse_implicit_call()
        
        # Return statement
        if self.match(TokenType.RET):
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
        
        # Parse body (statements separated by | or newlines)
        body = []
        while not self.match(TokenType.EOF, TokenType.EXPORT):
            if self.match(TokenType.NEWLINE):
                self.skip_newlines()
                continue
                
            # If we hit another core keyword that shouldn't be inside a function without context?
            # Actually, functions can contain any statement.
            # But we need to know when the function ends.
            # VL relies on indentation? No, it's not whitespace sensitive in that way.
            # It relies on specific delimiters.
            # BUT the prompt example shows multi-line indentation.
            # If VL is truly "universal" and uses `|`, maybe indentation is syntactic sugar?
            # For now, let's just consume until we hit something that clearly ends it.
            # But wait, `fn` doesn't have an `end` token.
            # The previous logic broke on NEWLINE.
            # If we allow NEWLINE, what stops it?
            # `EXPORT` stops it. `EOF` stops it.
            # Another `FN`?
            if self.match(TokenType.FN):
                 break
            
            # Additional safety: If we see META or DEPS, break
            if self.match(TokenType.META, TokenType.DEPS):
                break
                
            stmt = self.parse_statement()
            if stmt:
                body.append(stmt)
            
            # Only consume PIPE if it's a statement separator, not a pipeline operation  
            if self.match(TokenType.PIPE):
                # Check if this is a pipeline operation (|filter:, |map:, etc.)
                next_tok = self.peek()
                if next_tok and next_tok.type in (TokenType.FILTER, TokenType.MAP, TokenType.PARSE):
                    # This PIPE is part of a pipeline expression, don't consume it here
                    # It should have been consumed by the expression parser
                    pass
                else:
                    # This is a statement separator, consume it
                    self.advance()

        
        return FunctionDef(
            line=token.line, column=token.column,
            name=name,
            input_types=input_types,
            output_type=output_type,
            body=body
        )
    
    def parse_function_expr(self) -> FunctionExpr:
        """Parse: fn:name|i:type,type|o:type|body - Function as expression inside objects"""
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
        
        # Parse body - for function expressions, stop at } or , (object delimiters)
        body = []
        while not self.match(TokenType.EOF, TokenType.RBRACE, TokenType.COMMA):
            if self.match(TokenType.NEWLINE):
                self.skip_newlines()
                continue
            
            stmt = self.parse_statement()
            if stmt:
                body.append(stmt)
            
            # Consume pipe separators within the function body
            if self.match(TokenType.PIPE):
                next_tok = self.peek()
                if next_tok and next_tok.type in (TokenType.FILTER, TokenType.MAP, TokenType.PARSE):
                    pass  # Pipeline operation, don't consume
                else:
                    self.advance()
        
        return FunctionExpr(
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
    
    def parse_implicit_variable_or_compound(self) -> Union[VariableDef, 'CompoundAssignment']:
        """Parse: name=value (implicit variable) or name+=value (compound assignment)"""
        token = self.current_token
        name = self.expect(TokenType.IDENTIFIER).value
        
        # Check for compound assignment operators
        if self.match(TokenType.PLUS_EQUALS):
            self.advance()
            value = self.parse_expression()
            return CompoundAssignment(
                line=token.line, column=token.column,
                name=name, operator='+', value=value
            )
        elif self.match(TokenType.MINUS_EQUALS):
            self.advance()
            value = self.parse_expression()
            return CompoundAssignment(
                line=token.line, column=token.column,
                name=name, operator='-', value=value
            )
        elif self.match(TokenType.TIMES_EQUALS):
            self.advance()
            value = self.parse_expression()
            return CompoundAssignment(
                line=token.line, column=token.column,
                name=name, operator='*', value=value
            )
        elif self.match(TokenType.DIV_EQUALS):
            self.advance()
            value = self.parse_expression()
            return CompoundAssignment(
                line=token.line, column=token.column,
                name=name, operator='/', value=value
            )
        
        # Simple assignment: name=value
        self.expect(TokenType.EQUALS)
        value = self.parse_expression()
        
        return VariableDef(
            line=token.line, column=token.column,
            name=name,
            type_annotation=None,
            value=value
        )
    
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
    
    def parse_implicit_call(self) -> DirectCall:
        """Parse: function(args) or obj.method(args) - Implicit call without @ prefix"""
        token = self.current_token
        # Parse the entire expression (identifier with possible member access and call)
        function_expr = self.parse_expression()
        
        return DirectCall(
            line=token.line, column=token.column,
            function=function_expr
        )
    
    def parse_direct_call(self) -> DirectCall:
        """Parse: @function(args) - Direct function call without variable assignment"""
        token = self.expect(TokenType.AT)
        function_expr = self.parse_expression()
        
        return DirectCall(
            line=token.line, column=token.column,
            function=function_expr
        )
    
    def parse_if_stmt(self) -> IfStmt:
        """Parse: if:condition?true_expr:false_expr
        Supports early returns: if:condition?ret:value:ret:other"""
        token = self.expect(TokenType.IF)
        self.expect(TokenType.COLON)
        
        condition = self.parse_expression()
        self.expect(TokenType.QUESTION)
        
        # Parse true branch - could be ret:value or just value
        if self.match(TokenType.RET):
            self.advance()
            self.expect(TokenType.COLON)
            true_value = self.parse_expression()
            true_expr = ReturnStmt(line=token.line, column=token.column, value=true_value)
        else:
            true_expr = self.parse_expression()
        
        self.expect(TokenType.COLON)
        
        # Parse false branch - could be ret:value or just value
        if self.match(TokenType.RET):
            self.advance()
            self.expect(TokenType.COLON)
            false_value = self.parse_expression()
            false_expr = ReturnStmt(line=token.line, column=token.column, value=false_value)
        else:
            false_expr = self.parse_expression()
        
        return IfStmt(
            line=token.line, column=token.column,
            condition=condition,
            true_expr=true_expr,
            false_expr=false_expr
        )
    
    def parse_if_expr(self) -> IfStmt:
        """Parse if as expression: if:condition?true_expr:false_expr
        Same as parse_if_stmt since IfStmt is actually an expression in VL"""
        return self.parse_if_stmt()
    
    def parse_for_loop(self) -> ForLoop:
        """Parse: for:var,iterable|body"""
        token = self.expect(TokenType.FOR)
        self.expect(TokenType.COLON)
        
        # Allow keywords as variable names in loop context (i, o, etc.)
        if self.match(TokenType.IDENTIFIER):
            variable = self.advance().value
        elif self.current_token:
            # Accept keywords as identifiers in this context
            variable = self.advance().value
        else:
            raise self.error("Expected variable name in for loop")
        
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
        
        # Parse chained operations (filter, map, etc.)
        operations = []
        while self.match(TokenType.PIPE):
            # Look ahead to see if it's a data operation
            next_token = self.peek(1)
            if next_token and next_token.type in (TokenType.FILTER, TokenType.MAP, TokenType.PARSE):
                self.advance() # consume PIPE
                if self.match(TokenType.FILTER):
                    operations.append(self.parse_filter_op())
                elif self.match(TokenType.MAP):
                    operations.append(self.parse_map_op())
                elif self.match(TokenType.PARSE):
                    operations.append(self.parse_parse_op())
            else:
                break
        
        return APICall(
            line=token.line, column=token.column,
            method=method,
            endpoint=endpoint,
            options=options,
            is_async=is_async,
            operations=operations
        )
    
    def parse_api_call_expr(self) -> APICall:
        """Parse API call as expression (same as statement)"""
        return self.parse_api_call()
    
    def parse_filter_op(self) -> FilterOp:
        token = self.expect(TokenType.FILTER)
        self.expect(TokenType.COLON)
        condition = self.parse_expression()
        return FilterOp(line=token.line, column=token.column, condition=condition)

    def parse_map_op(self) -> MapOp:
        token = self.expect(TokenType.MAP)
        self.expect(TokenType.COLON)
        # TODO: Better map parsing for fields vs expression
        # For now, assume expression
        expr = self.parse_expression()
        return MapOp(line=token.line, column=token.column, fields=None, expression=expr)

    def parse_parse_op(self) -> ParseOp:
        token = self.expect(TokenType.PARSE)
        self.expect(TokenType.COLON)
        format = self.expect(TokenType.IDENTIFIER).value
        return ParseOp(line=token.line, column=token.column, format=format)

    def parse_ui_component(self) -> UIComponent:
        """Parse: ui:name|state:...|props:...|on:...|render:..."""
        token = self.expect(TokenType.UI)
        self.expect(TokenType.COLON)
        
        name = self.expect(TokenType.IDENTIFIER).value
        
        # Parse optional clauses
        props = []
        state_vars = []
        handlers = []
        render_element = None
        
        while self.match(TokenType.PIPE):
            self.advance()
            
            # Skip empty pipes
            if self.match(TokenType.PIPE, TokenType.NEWLINE, TokenType.EOF):
                continue
            
            # Parse state declaration
            if self.match(TokenType.STATE):
                self.advance()
                self.expect(TokenType.COLON)
                # Simple format: state:name=value or state:name:type=value
                state_name = self.expect(TokenType.IDENTIFIER).value
                state_type = None
                
                if self.match(TokenType.COLON):
                    self.advance()
                    # Accept type tokens or identifiers
                    if self.current_token:
                        state_type = self.advance().value
                
                if self.match(TokenType.EQUALS):
                    self.advance()
                    state_value = self.parse_expression()
                    state_vars.append((state_name, state_type, state_value))
                continue
            
            # Parse props declaration
            if self.match(TokenType.PROPS):
                self.advance()
                self.expect(TokenType.COLON)
                # Simple format: props:name:type
                prop_name = self.expect(TokenType.IDENTIFIER).value
                prop_type = None
                if self.match(TokenType.COLON):
                    self.advance()
                    # Accept type tokens or identifiers
                    if self.current_token:
                        prop_type = self.advance().value
                props.append((prop_name, prop_type))
                continue
            
            # Parse event handlers
            if self.match(TokenType.ON):
                self.advance()
                self.expect(TokenType.COLON)
                handler_name = self.expect(TokenType.IDENTIFIER).value
                handlers.append(handler_name)
                continue
            
            # Parse render clause
            if self.match(TokenType.RENDER):
                self.advance()
                self.expect(TokenType.COLON)
                render_element = self.expect(TokenType.IDENTIFIER).value
                continue
            
            # Break if we hit something that's not part of UI component
            break
        
        return UIComponent(
            line=token.line, column=token.column,
            name=name,
            props=props,
            state_vars=state_vars,
            body=[]  # body now stores render info
        )
    
    def parse_data_pipeline(self) -> DataPipeline:
        """Parse: data:source|operation|operation|..."""
        token = self.expect(TokenType.DATA)
        self.expect(TokenType.COLON)
        
        source = self.parse_expression()
        
        operations = []
        max_ops = 100  # Safety limit
        while self.match(TokenType.PIPE) and not self.match(TokenType.NEWLINE, TokenType.EOF) and len(operations) < max_ops:
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
                # TODO support map:field1,field2 syntax
                transformation = self.parse_expression()
                operations.append(MapOp(
                    line=self.current_token.line,
                    column=self.current_token.column,
                    fields=None,
                    expression=transformation
                ))
            elif self.match(TokenType.GROUPBY):
                self.advance()
                self.expect(TokenType.COLON)
                field = self.expect(TokenType.IDENTIFIER).value
                operations.append(GroupByOp(
                    line=self.current_token.line,
                    column=self.current_token.column,
                    field=field
                ))
            elif self.match(TokenType.AGG):
                self.advance()
                self.expect(TokenType.COLON)
                func = self.expect(TokenType.IDENTIFIER).value
                operations.append(AggregateOp(
                    line=self.current_token.line,
                    column=self.current_token.column,
                    function=func,
                    field=None
                ))
            elif self.match(TokenType.SORT):
                self.advance()
                self.expect(TokenType.COLON)
                field = self.expect(TokenType.IDENTIFIER).value
                operations.append(SortOp(
                    line=self.current_token.line,
                    column=self.current_token.column,
                    field=field,
                    order='asc'
                ))
        
        return DataPipeline(
            line=token.line, column=token.column,
            source=source,
            operations=operations
        )
    
    def parse_data_pipeline_expr(self) -> DataPipeline:
        """Parse data pipeline as expression (same as statement)"""
        return self.parse_data_pipeline()
    
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
        return self.parse_logical()
    
    def parse_logical(self) -> Expression:
        """Parse logical AND/OR operators"""
        left = self.parse_comparison()
        
        while self.match(TokenType.AND, TokenType.OR):
            op_token = self.advance()
            right = self.parse_comparison()
            left = Operation(
                line=op_token.line, column=op_token.column,
                operator=op_token.value,
                operands=[left, right]
            )
        
        return left
    
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
        
        return self.parse_postfix()

    def parse_postfix(self) -> Expression:
        """Parse postfix expressions (calls, member access, pipeline operations)"""
        expr = self.parse_primary()
        
        while True:
            # Member access: obj.prop
            if self.match(TokenType.DOT):
                self.advance()
                prop_token = self.expect(TokenType.IDENTIFIER)
                expr = MemberAccess(
                    line=expr.line,
                    column=expr.column,
                    object=expr,
                    property=prop_token.value
                )
            
            # Function call: func(args)
            elif self.match(TokenType.LPAREN):
                self.advance()
                args = []
                while not self.match(TokenType.RPAREN):
                    args.append(self.parse_expression())
                    if self.match(TokenType.COMMA):
                        self.advance()
                self.expect(TokenType.RPAREN)
                
                expr = FunctionCall(
                    line=expr.line,
                    column=expr.column,
                    callee=expr,
                    arguments=args
                )
            
            # Pipeline operations: expr|filter:...|map:...  
            elif self.match(TokenType.PIPE) and not self.parsing_pipeline_operation:
                peek_tok = self.peek(1)  # Look ahead to next token
                if peek_tok and peek_tok.type in (TokenType.FILTER, TokenType.MAP, TokenType.PARSE):
                    # Parse pipeline operations starting from current expression
                    operations = []
                    max_ops = 100  # Safety limit
                    self.parsing_pipeline_operation = True  # Set flag
                    try:
                        while (self.match(TokenType.PIPE) and self.peek(1) and 
                               self.peek(1).type in (TokenType.FILTER, TokenType.MAP, TokenType.PARSE) and
                               len(operations) < max_ops):
                            self.advance()  # consume PIPE, now at operation token
                            
                            # Now current token is FILTER, MAP, or PARSE
                            if self.current_token.type == TokenType.FILTER:
                                operations.append(self.parse_filter_op())
                            elif self.current_token.type == TokenType.MAP:
                                operations.append(self.parse_map_op())
                            elif self.current_token.type == TokenType.PARSE:
                                operations.append(self.parse_parse_op())
                        
                        # Create a DataPipeline with the expression as source
                        expr = DataPipeline(
                            line=expr.line,
                            column=expr.column,
                            source=expr,
                            operations=operations
                        )
                    finally:
                        self.parsing_pipeline_operation = False  # Clear flag
                else:
                    # PIPE but not a pipeline operation, stop parsing postfix
                    break
            
            else:
                break
                
        return expr
    
    def parse_primary(self) -> Expression:
        """Parse primary expressions (literals, identifiers, etc.)"""
        token = self.current_token
        
        # Number literal (and check for range: 0..10)
        if self.match(TokenType.NUMBER):
            self.advance()
            value = float(token.value) if '.' in token.value else int(token.value)
            num_literal = NumberLiteral(
                line=token.line, column=token.column,
                value=value
            )
            
            # Check for range operator (..)
            if self.match(TokenType.DOTDOT):
                self.advance()
                end_expr = self.parse_primary()  # Parse the end value
                return RangeExpr(
                    line=token.line, column=token.column,
                    start=num_literal,
                    end=end_expr
                )
            
            return num_literal
        
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
        
        # Direct function call (@func(args))
        if self.match(TokenType.AT):
            self.advance()
            func_name = self.expect(TokenType.IDENTIFIER).value
            self.expect(TokenType.LPAREN)
            
            args = []
            while not self.match(TokenType.RPAREN):
                args.append(self.parse_expression())
                if self.match(TokenType.COMMA):
                    self.advance()
            self.expect(TokenType.RPAREN)
            
            # Create FunctionCall with Identifier as callee
            callee = Identifier(line=token.line, column=token.column, name=func_name)
            return FunctionCall(
                line=token.line, column=token.column,
                callee=callee,
                arguments=args
            )
        
        # Operation (op:+(...))
        if self.match(TokenType.OP):
            return self.parse_operation_expr()
        
        # If expression (if:condition?true:false)
        if self.match(TokenType.IF):
            return self.parse_if_expr()
        
        # Data pipeline expression (data:source|filter:...)
        if self.match(TokenType.DATA):
            return self.parse_data_pipeline_expr()
        
        # API call as expression (api:GET,url)
        if self.match(TokenType.API, TokenType.ASYNC):
            return self.parse_api_call_expr()
        
        # Identifier (variable or function name)
        if self.match(TokenType.IDENTIFIER):
            name = self.advance().value
            
            # Just identifier
            return Identifier(
                line=token.line, column=token.column,
                name=name
            )
        
        # Single-letter keywords can be used as identifiers in expressions (i, j, o, etc.)
        # This allows loop variables and function parameters
        if self.current_token and len(self.current_token.value) <= 2:
            # Allow short keywords as identifiers (i, o, v, etc.)
            if self.current_token.type in (TokenType.INPUT, TokenType.OUTPUT, TokenType.VAR):
                name = self.advance().value
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
        """Parse: {key:value,key2:value2} - values can include fn: for methods"""
        token = self.expect(TokenType.LBRACE)
        
        pairs = []
        while not self.match(TokenType.RBRACE):
            key = self.expect(TokenType.IDENTIFIER).value
            self.expect(TokenType.COLON)
            
            # Check if value is a function expression (fn:name|...)
            if self.match(TokenType.FN):
                value = self.parse_function_expr()
            else:
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
