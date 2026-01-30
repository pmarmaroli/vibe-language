#!/usr/bin/env python3
"""
VL (Vibe Language) Interpreter
Main entry point for executing VL programs

Usage:
    python vl.py <file.vl>
    python vl.py --version
    python vl.py --help
"""

import sys
import argparse
from pathlib import Path
from lexer import tokenize, TokenType
from parser import Parser, ParseError
from codegen_python import PythonCodeGenerator

# Version info
__version__ = "0.1.0-alpha"
__author__ = "Patrick Marmaroli"

def main():
    """Main entry point for VL interpreter"""
    parser = argparse.ArgumentParser(
        description="VL (Vibe Language) Interpreter",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  vl.py program.vl              Run a VL program
  vl.py --version               Show version
  vl.py --debug program.vl      Run with debug output
        """
    )
    
    parser.add_argument(
        'file',
        nargs='?',
        type=str,
        help='VL source file to execute (.vl)'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version=f'VL Interpreter v{__version__}'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug output (show tokens, AST)'
    )
    
    parser.add_argument(
        '--tokens-only',
        action='store_true',
        help='Only tokenize and show tokens (for debugging)'
    )
    
    parser.add_argument(
        '--ast-only',
        action='store_true',
        help='Only parse and show AST (for debugging)'
    )
    
    args = parser.parse_args()
    
    # If no file provided, show help
    if not args.file:
        parser.print_help()
        sys.exit(1)
    
    # Check file exists
    vl_file = Path(args.file)
    if not vl_file.exists():
        print(f"Error: File not found: {args.file}", file=sys.stderr)
        sys.exit(1)
    
    if not vl_file.suffix == '.vl':
        print(f"Warning: File does not have .vl extension: {args.file}", file=sys.stderr)
    
    # Read source code
    try:
        source_code = vl_file.read_text(encoding='utf-8')
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(1)
    
    # 1. Tokenize (Lexer)
    try:
        tokens = tokenize(source_code)
    except Exception as e:
        print(f"Lexer Error: {e}", file=sys.stderr)
        sys.exit(1)

    # Handle --tokens-only flag
    if args.tokens_only:
        for token in tokens:
            if token.type != TokenType.NEWLINE:
                print(token)
        sys.exit(0)

    # 2. Parse (Parser -> AST)
    try:
        parser = Parser(tokens)
        ast = parser.parse()
    except ParseError as e:
        print(f"Parser Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected Parser Error: {e}", file=sys.stderr)
        # Check if debug mode to show full trace
        if args.debug:
            raise
        sys.exit(1)

    # Handle --ast-only flag
    if args.ast_only:
        print(ast)
        sys.exit(0)

    # 3. Code Generation (VL -> Python)
    try:
        generator = PythonCodeGenerator(ast)
        python_code = generator.generate()
    except Exception as e:
        print(f"Code Generation Error: {e}", file=sys.stderr)
        if args.debug:
            raise
        sys.exit(1)

    if args.debug:
        print(f"[DEBUG] Generated Python Code:\n{python_code}\n")
        print(f"[DEBUG] Executing code...\n")

    # 4. Execute
    try:
        # Create a new namespace for execution
        exec_globals = {"__name__": "__main__"}
        exec(python_code, exec_globals)
        
        # If there is a main function (or export), we might need to invoke it?
        # The prompt examples show top-level execution or function definitions.
        # If the user defines `fn:main|...` the generated python has `def main():...` 
        # but doesn't call it unless the VL code calls it.
        # Python doesn't auto-run `main`.
        # However, testing with `test.vl`: `fn:sum|...`. It doesn't run anything.
        # If the user wants to run something, they should write a top level statement or call.
        
    except Exception as e:
        print(f"Runtime Error: {e}", file=sys.stderr)
        sys.exit(1)
    
    if args.debug:
        print(f"\n[DEBUG] Execution finished.")

    
    return 0

if __name__ == "__main__":
    sys.exit(main())
