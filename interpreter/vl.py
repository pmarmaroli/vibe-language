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

    # For now, just show we read the file
    if args.debug:
        print(f"[DEBUG] Read {len(source_code)} characters from {args.file}")
        print(f"[DEBUG] Source:\n{source_code}\n")
        print(f"[DEBUG] Token count: {len(tokens)}")
    
    print(f"VL Interpreter v{__version__}")
    print(f"Loaded: {args.file}")
    
    # TODO: 
    # 2. Parse (Parser -> AST)
    # 3. Execute (Interpreter)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
