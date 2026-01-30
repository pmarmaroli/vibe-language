# VL Architecture Guide

**Version:** 0.1.3  
**Last Updated:** January 30, 2026

This document explains the VL project structure and architecture for contributors.

---

## Project Structure

```
vibe-language/
├── README.md, LICENSE.md, CONTRIBUTING.md  # Project documentation
├── vl.bat, vl                              # CLI entry points (Windows/Unix)
│
├── src/vl/                                 # VL Python package
│   ├── __init__.py                         # Package exports
│   ├── __main__.py                         # CLI entry (python -m vl.cli)
│   ├── cli.py                              # Command-line interface
│   ├── compiler.py                         # Main compiler orchestrator
│   ├── lexer.py                            # Lexical analyzer (tokenizer)
│   ├── parser.py                           # Syntax analyzer (AST builder)
│   ├── type_checker.py                     # Type validation & inference
│   ├── ast_nodes.py                        # AST node definitions
│   ├── errors.py                           # Error classes
│   ├── config.py                           # Configuration settings
│   ├── logging_config.py                   # Logging setup
│   └── codegen/                            # Code generators
│       ├── __init__.py                     # Codegen exports
│       ├── base.py                         # BaseCodeGenerator (abstract)
│       ├── python.py                       # Python code generator
│       ├── javascript.py                   # JavaScript code generator
│       ├── typescript.py                   # TypeScript code generator
│       ├── c.py                            # C code generator
│       └── rust.py                         # Rust code generator
│
├── tests/                                  # Test suite
│   ├── unit/                               # Unit tests
│   │   ├── test_config.py                  # Configuration system tests
│   │   └── test_type_checker.py            # Type checker tests
│   ├── integration/                        # Integration tests
│   │   ├── test_edge_cases.py              # Edge case handling
│   │   ├── test_execution.py               # Code execution validation
│   │   ├── test_final_validation.py        # Comprehensive validation
│   │   ├── test_js_codegen.py              # JavaScript codegen tests
│   │   ├── test_py_passthrough.py          # Python FFI tests
│   │   └── test_cli.rs                     # CLI integration (Rust test)
│   ├── codegen/                            # Code generation tests
│   │   ├── test_codegen_all.py             # All targets × constructs (65 tests)
│   │   └── test_multi_target_boolean.py    # Boolean optimization (11 tests)
│   └── benchmarks/                         # Performance benchmarks
│       ├── token_efficiency/               # Token efficiency benchmarks
│       ├── run_benchmarks.py               # Benchmark runner
│       ├── test_robustness.py              # Robustness testing
│       ├── test_strengths.py               # Strength analysis
│       └── test_examples.py                # Example validation
│
├── examples/                               # VL example programs
│   ├── basic/                              # Basic examples
│   │   ├── hello.vl                        # Hello world
│   │   ├── functions.vl                    # Function definitions
│   │   ├── loops.vl                        # Loop constructs
│   │   ├── test_cli.vl                     # CLI test example
│   │   └── test_syntax.vl                  # Syntax test example
│   ├── data/                               # Data processing examples
│   │   ├── data.vl                         # Basic data operations
│   │   ├── csv_processor.vl                # CSV processing
│   │   ├── data_pipeline.vl                # Pipeline operations
│   │   ├── api.vl                          # API calls
│   │   ├── api_calls.vl                    # HTTP requests
│   │   └── scraper.vl                      # Web scraping
│   └── ui/                                 # UI examples
│       └── ui.vl                           # UI components
│
├── docs/                                   # Documentation
│   ├── architecture.md                     # This file
│   ├── specification.md                    # Language specification
│   └── roadmap.md                          # Development roadmap
│
├── .github/workflows/                      # CI/CD
│   └── test.yml                            # GitHub Actions workflow
│
└── vibe-vscode/                            # VS Code extension
    ├── package.json                        # Extension manifest
    ├── language-configuration.json         # Language config
    └── syntaxes/vl.tmLanguage.json         # Syntax highlighting

```

---

## Architecture Overview

### Compilation Pipeline

```
VL Source Code (.vl file)
    ↓
[Lexer] → Tokens
    ↓
[Parser] → Abstract Syntax Tree (AST)
    ↓
[Type Checker] → Type Validation (optional)
    ↓
[Code Generator] → Target Language Code
    ↓
Output (Python/JS/TS/C/Rust)
```

### Core Components

#### 1. Lexer (lexer.py)
- Converts raw VL source into tokens
- Handles keywords, operators, literals, identifiers
- Tracks line/column for error reporting
- Supports string interpolation with `${...}`

#### 2. Parser (parser.py)
- Recursive descent parser with operator precedence
- Builds Abstract Syntax Tree (AST)
- Handles all VL constructs: functions, pipelines, UI components
- Error recovery for better IDE integration

#### 3. Type Checker (type_checker.py)
- Optional type validation
- Type inference for annotated variables
- Function signature checking
- Compatible with Python's typing system

#### 4. Code Generators (codegen/)
All generators inherit from `BaseCodeGenerator`:
- **Python**: Optimized with `all()`/`any()` for boolean chains
- **JavaScript**: ES6+ with native operators
- **TypeScript**: Type-safe with full type annotations
- **C**: ANSI C with standard library
- **Rust**: Safe Rust with std library

#### 5. Configuration (config.py)
Centralized settings:
- `BOOLEAN_CHAIN_MIN_LENGTH = 3` - Optimization threshold
- `OPTIMIZE_BOOLEAN_CHAINS = True` - Enable optimizations
- Target-specific settings (file extensions, type hints, etc.)

---

## Key Design Decisions

### Multi-Target IR Philosophy
VL is an intermediate representation (like LLVM or WebAssembly) that compiles to multiple targets. Each codegen optimizes for its target's idioms.

### BaseCodeGenerator Pattern
All code generators inherit from an abstract base class to eliminate duplication:
- Common indentation management
- Shared helper methods
- Consistent dispatch patterns

### Configuration System
Runtime-configurable behavior allows optimization tuning without code changes. Codegen classes read config dynamically (not at import time).

### Test Organization
Tests organized by purpose:
- **unit/**: Test individual components
- **integration/**: Test complete workflows
- **codegen/**: Test all 5 targets comprehensively
- **benchmarks/**: Performance and efficiency metrics

---

## Running Tests

```bash
# Set PYTHONPATH to find the vl package
cd d:\Github\vibe-language
$env:PYTHONPATH="$PWD\src"

# Run all codegen tests (65 tests)
python tests/codegen/test_codegen_all.py

# Run boolean optimization tests (11 tests)
python tests/codegen/test_multi_target_boolean.py

# Run configuration tests
python tests/unit/test_config.py

# Run integration tests
python tests/integration/test_execution.py
python tests/integration/test_edge_cases.py

# Run benchmarks
python tests/benchmarks/run_benchmarks.py
```

---

## Adding a New Target

To add a new target language (e.g., Go):

1. **Create codegen file**: `src/vl/codegen/go.py`
2. **Inherit from BaseCodeGenerator**:
   ```python
   from ..ast_nodes import *
   from .base import BaseCodeGenerator
   
   class GoCodeGenerator(BaseCodeGenerator):
       def generate(self) -> str:
           # Implementation
   ```
3. **Update compiler.py**: Add Go to TargetLanguage enum and _generate_code()
4. **Update config.py**: Add Go target settings
5. **Add to __init__.py**: Export GoCodeGenerator
6. **Write tests**: Add Go tests to test_codegen_all.py

---

## Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for:
- Code style guidelines
- Pull request process
- Testing requirements
- Development workflow

---

## Status

**Version:** 0.1.3  
**Last Updated:** January 30, 2026  
**Test Coverage:** 76/76 tests passing (100%)

For more details, see:
- [Language Specification](specification.md)
- [Development Roadmap](roadmap.md)
- [Main README](../README.md)

- ✅ **BaseCodeGenerator** - Abstract base class for all code generators
- ✅ **Configuration System** - Centralized settings in `vl_config.py`
- ✅ **Logging Infrastructure** - Structured logging with `vl_logging.py`

**Multi-Target Code Generation (All 5 Targets Operational):**
- ✅ **VL → Python** - Optimized code with `all()`/`any()` (51/51 tests)
- ✅ **VL → JavaScript** - ES6+ with native operators (14/14 tests)
- ✅ **VL → TypeScript** - Type-safe with full type annotations
- ✅ **VL → C** - ANSI C with header management
- ✅ **VL → Rust** - Safe Rust with std library

**Language Features:**
- ✅ **All core language constructs** - Functions, variables, control flow, operators
- ✅ **Data pipelines** - filter, map, groupBy, agg, sort with item keyword scoping
- ✅ **API calls** - HTTP methods (GET, POST, etc.)
- ✅ **File operations** - Read/write with target-specific APIs
- ✅ **UI components** - React (JS/TS), placeholder (Python/C/Rust)
- ✅ **Type annotations** - Full type system with automatic imports
- ✅ **Array/object indexing** - Nested indexing support
- ✅ **Python FFI** - Call Python libraries with py: prefix

**Developer Experience:**
- ✅ **CLI** - `vl.py` with 5 target flags (python/py, javascript/js, typescript/ts, c, rust/rs)
- ✅ **CLI wrappers** - `vl.bat` (Windows) and `vl` (Unix/Linux)
- ✅ **VS Code extension** - Syntax highlighting for .vl files
- ✅ **CI/CD Pipeline** - GitHub Actions testing Python 3.9-3.11 on Ubuntu/Windows/macOS
- ✅ **Comprehensive test suite** - 76/76 tests passing (100%)
  - 65 comprehensive codegen tests (5 targets × constructs)
  - 11 multi-target boolean optimization tests
  - 4 configuration system tests

### What's In Progress 🚧

- 🚧 **Parser error recovery** - Continue parsing after errors for IDE integration
- 🚧 **Performance optimization** - Compilation speed benchmarks and profiling
- 🚧 **Standard library** - Built-in functions for common operations
- 📋 **Enhanced type inference** - Infer types without annotations
- 📋 **Debugger** - Step-through debugging support
- 📋 **REPL** - Interactive shell for quick testing
- 📋 **Language server** - LSP for VS Code IntelliSense

---

## Quick Start

### Prerequisites

- Python 3.8 or higher
- No external dependencies (uses only Python standard library)

### Project Structure

The VL codebase has been reorganized for clarity:

```
vibe-language/
├── src/vl/                  # VL source code (Python package)
│   ├── codegen/             # All code generators
│   │   ├── base.py          # Abstract base class
│   │   ├── python.py        # Python codegen
│   │   ├── javascript.py    # JavaScript codegen
│   │   ├── typescript.py    # TypeScript codegen
│   │   ├── c.py             # C codegen
│   │   └── rust.py          # Rust codegen
│   ├── cli.py               # Command-line interface
│   ├── compiler.py          # Compiler orchestrator
│   ├── lexer.py             # Lexical analyzer
│   ├── parser.py            # Syntax analyzer
│   ├── type_checker.py      # Type system
│   ├── config.py            # Configuration
│   └── logging_config.py    # Logging setup
├── tests/                   # Test suite
│   ├── unit/                # Unit tests (config, type checker)
│   ├── integration/         # Integration tests (execution, validation)
│   ├── codegen/             # Codegen tests (65 tests)
│   └── benchmarks/          # Performance benchmarks
├── examples/                # Example programs
│   ├── basic/               # Hello world, loops, functions
│   ├── data/                # Pipelines, CSV, APIs
│   └── ui/                  # UI components
└── docs/                    # Documentation
```

### Installation

No installation needed! The interpreter uses only Python standard library.

### Running VL Programs

```bash
# From the project root (using wrapper scripts)
cd vibe-language

# Windows
.\vl.bat examples/hello.vl
.\vl.bat program.vl --target js -o output.js

# Unix/Linux
./vl examples/hello.vl
./vl program.vl --target js -o output.js

# Or run directly
python interpreter/vl.py examples/hello.vl
python interpreter/vl.py program.vl --target js --debug
```

### Command-Line Options

```bash
vl.py [-h] [--version] [--debug] [--target {python,js}] 
      [--output OUTPUT] [--tokens-only] [--ast-only] [file]

Options:
  --target {python,js}  Target language (default: python)
  --output, -o OUTPUT   Output file for compiled code
  --debug              Show generated code and execution details
  --tokens-only        Show tokens only (debugging)
  --ast-only           Show AST only (debugging)
```

### Original Setup

```bash
# Clone the repository
git clone https://github.com/pmarmaroli/vibe-language.git
cd vibe-language/interpreter

# Test the lexer
python3 lexer.py
```

### Running VL Programs

```bash
# Run a VL program (when interpreter is complete)
python3 vl.py program.vl

# Show tokens only (debug)
python3 vl.py --tokens-only program.vl

# Show AST only (debug)
python3 vl.py --ast-only program.vl

# Enable debug output
python3 vl.py --debug program.vl
```

---

## Architecture

```
VL Source Code (.vl)
        ↓
    Lexer (lexer.py)
        ↓
    Tokens
        ↓
    Parser (parser.py)
        ↓
    AST (Abstract Syntax Tree)
        ↓
    Compiler (codegen_python.py)
        ↓
    Python Code
        ↓
    Execution (via exec/subprocess)
```

---

## File Structure

```
interpreter/
├── README.md              # This file
├── vl.py                  # Main entry point / CLI
├── lexer.py               # Tokenizer (DONE ✅)
├── parser.py              # Parser (DONE ✅)
├── ast_nodes.py           # AST node definitions (DONE ✅)
├── codegen_python.py      # VL → Python compiler (DONE ✅)
├── compiler.py            # Compiler Orchestrator (DONE ✅)
├── stdlib.py              # Standard library functions (PLANNED 📋)
├── errors.py              # Error classes and handling (PLANNED 📋)
├── test.vl                # Simple test program
├── examples/              # Example VL programs
│   ├── hello.vl
│   ├── functions.vl
│   ├── api.vl
│   ├── data.vl
│   └── ui.vl
└── tests/                 # Unit tests
    ├── test_lexer.py
    ├── test_parser.py
    └── test_interpreter.py
```

---

## Examples

### Example 1: Simple Function

**File:** `test.vl`
```vl
# Simple addition function
fn:sum|i:int,int|o:int|ret:op:+(i0,i1)
```

**Run:**
```bash
python3 vl.py test.vl
```

### Example 2: API Call

**File:** `examples/api.vl`
```vl
meta:getUsers,api_function,python
fn:getUsers|i:str|o:arr|api:GET,$i|filter:age>=18|map:name,email
export:getUsers
```

### Example 3: Data Processing

**File:** `examples/data.vl`
```vl
meta:analyzeData,data_processor,python
fn:analyzeData|i:arr|o:obj|
  data:$i|filter:value>0|groupBy:category|agg:sum,value|sort:total,desc
export:analyzeData
```

---

## Development

### Running Tests

```bash
# Test the lexer
python3 -m pytest tests/test_lexer.py

# Test the parser (when ready)
python3 -m pytest tests/test_parser.py

# Run all tests
python3 -m pytest tests/
```

### Testing the Lexer Manually

```bash
# Test with built-in example
python3 lexer.py

# Test with custom VL code
python3 -c "
from lexer import tokenize
code = \"fn:double|i:int|o:int|ret:op:*(i,2)\"
tokens = tokenize(code)
for token in tokens:
    print(token)
"
```

---

## Implementation Progress

### Phase 1: Lexer ✅ (DONE)

- [x] Token types defined
- [x] Tokenization algorithm
- [x] Keywords and operators
- [x] String literals with escape sequences
- [x] Number literals (int, float, scientific)
- [x] Comments (single-line)
- [x] Error reporting (line/column numbers)

**Coverage:**
- ✅ All VL keywords
- ✅ All operators
- ✅ All delimiters
- ✅ Identifiers
- ✅ Literals (numbers, strings, booleans)
- ✅ Comments

### Phase 2: Parser 🚧 (IN PROGRESS)

**Goal:** Convert tokens into Abstract Syntax Tree (AST)

**TODO:**
- [ ] AST node classes
- [ ] Recursive descent parser
- [ ] Expression parsing
- [ ] Statement parsing
- [ ] Type annotations
- [ ] Error recovery
- [ ] Syntax error messages

**Priority Order:**
1. Basic expressions (numbers, strings, identifiers)
2. Operations (arithmetic, comparison, logical)
3. Function definitions
4. Variable definitions
5. Control flow (if, for, while)
6. API calls
7. Data operations
8. File operations
9. UI components

### Phase 3: Interpreter 📋 (PLANNED)

**Goal:** Execute AST and produce results

**TODO:**
- [ ] Environment (variable scoping)
- [ ] Function execution
- [ ] Built-in operations
- [ ] Control flow execution
- [ ] API domain execution (mock)
- [ ] Data domain execution
- [ ] File domain execution
- [ ] Runtime error handling

### Phase 4: Compiler 📋 (PLANNED)

**Goal:** Compile VL → Python source code

**TODO:**
- [ ] Python code generator
- [ ] Target language abstraction
- [ ] Optimization passes
- [ ] Source maps
- [ ] Type inference
- [ ] FFI code generation

---

## Contributing

We welcome contributions! Here's how to help:

### Current Priorities

1. **Parser Implementation** (highest priority)
   - Help build the parser
   - Write parser tests
   - Improve error messages

2. **Examples & Documentation**
   - Create more .vl example files
   - Write tutorials
   - Document best practices

3. **Testing**
   - Write unit tests
   - Test edge cases
   - Report bugs

### Getting Started

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/parser-expressions`)
3. Make your changes
4. Add tests
5. Commit (`git commit -m 'Add expression parsing'`)
6. Push (`git push origin feature/parser-expressions`)
7. Open a Pull Request

See [CONTRIBUTING.md](../CONTRIBUTING.md) for detailed guidelines.

---

## Technical Details

### Lexer Implementation

The lexer uses a **single-pass scanning algorithm**:

1. Read source character by character
2. Recognize patterns (keywords, operators, literals)
3. Emit tokens with position information
4. Handle errors gracefully

**Key Features:**
- Zero-lookahead (efficient)
- Line/column tracking (for errors)
- Escape sequence handling
- Unicode support (UTF-8)

### Token Types

See `lexer.py` for complete `TokenType` enum. Major categories:

- **Keywords:** `fn`, `i`, `o`, `ret`, `api`, `data`, etc.
- **Types:** `int`, `float`, `str`, `arr`, `obj`, etc.
- **Operators:** `+`, `-`, `*`, `/`, `==`, `!=`, `&&`, etc.
- **Delimiters:** `:`, `|`, `,`, `=`, `$`, `()`, `[]`, `{}`
- **Literals:** Numbers, strings, identifiers

### Error Handling

Errors include line and column numbers:

```
SyntaxError: Unexpected character '&' at 5:12
```

### Performance

Current performance (Python implementation):
- **Lexing:** ~100,000 lines/second
- **Memory:** ~1MB per 10,000 lines

(These will improve with native implementation later)

---

## Design Decisions

### Why Python for Bootstrap?

**Pros:**
- Fast development
- Easy to understand
- Rich standard library
- Good debugging tools

**Cons:**
- Slower than native
- Additional dependency

**Plan:** Use Python for MVP, then self-host (VL interpreter in VL) later.

### Why Single-Pass Lexer?

- Simplicity
- Performance
- Sufficient for VL's simple syntax

### Why Recursive Descent Parser?

- Easy to understand and modify
- Good error recovery
- Matches VL's grammar naturally

---

## Known Issues

### Current Limitations

1. **No parser yet** - Can only tokenize, not execute
2. **Limited error messages** - Basic syntax errors only
3. **No type checking** - Planned for later
4. **No optimizations** - Interpreter will be slow initially

### Reporting Issues

Please report bugs on GitHub Issues with:
- VL code that triggers the bug
- Expected behavior
- Actual behavior
- Python version
- Operating system

---

## Roadmap

### Short-Term (Next 2-4 Weeks)

- [ ] Complete parser implementation
- [ ] Basic interpreter (core constructs)
- [ ] 10+ working examples
- [ ] Unit tests for lexer and parser

### Medium-Term (Next 2-3 Months)

- [ ] Complete interpreter (all domains)
- [ ] VL → Python compiler (MVP)
- [ ] Error handling
- [ ] 50+ examples

### Long-Term (6+ Months)

- [ ] VL → JavaScript compiler
- [ ] FFI implementation
- [ ] Performance optimizations
- [ ] Debugger
- [ ] REPL

---

## Performance Benchmarks

*Coming soon - will compare VL execution speed vs Python, JavaScript*

---

## FAQ

**Q: Why is the interpreter so slow?**  
A: This is a Python-based reference implementation. Performance will improve with native implementations.

**Q: Can I use this in production?**  
A: Not yet! This is alpha software. Use for experiments and learning only.

**Q: How can I contribute?**  
A: See [CONTRIBUTING.md](../CONTRIBUTING.md) or join the community chat.

**Q: When will the parser be done?**  
A: Target: February 2026. Follow progress on GitHub.

**Q: Why doesn't feature X work?**  
A: Check the "Implementation Progress" section above. Many features are planned but not yet implemented.

---

## Resources

- **Language Spec:** [../specification.md](../specification.md)
- **Roadmap:** [../roadmap.md](../roadmap.md)
- **Main README:** [../README.md](../README.md)
- **GitHub:** https://github.com/pmarmaroli/vibe-language

---

**Last Updated:** January 29, 2026  
**Maintainer:** Patrick Marmaroli  
**License:** MIT
