# VL Interpreter

This directory contains the reference implementation of the VL (Vibe Language) interpreter written in Python.

## Status

**Version:** 0.1.0-alpha  
**Phase:** Foundation - Active Development

### What's Working ✅ (v0.1.2 - 100% Operational)

- ✅ **Lexer/Tokenizer** - Converts VL source code into tokens
- ✅ **Parser** - Converts tokens into Abstract Syntax Tree (AST)
- ✅ **VL → Python compiler** - Generate Python code from VL (100% operational)
- ✅ **VL → JavaScript compiler** - Generate JavaScript ES6+ code (100% operational)
  - All core language constructs
  - Data pipelines (filter, map, groupBy, agg, sort)
  - API calls (fetch)
  - File operations (Node.js fs module)
  - UI components (React)
  - Test coverage: 14/14 tests (100%)
- ✅ **Interpreter** - Executes the AST via Python transpilation
- ✅ **Command-line interface** - `vl.py` with `--target` flag (python|js)
- ✅ **CLI wrappers** - `vl.bat` (Windows) and `vl` (Unix/Linux)
- ✅ **Type annotations** - List[Any], Dict[str, Any] with auto-imports
- ✅ **Array/object indexing** - arr[0], obj['key'], nested indexing
- ✅ **Data pipelines** - Fixed item keyword scoping, nested pipeline flattening
- ✅ **Python FFI** - Call Python libraries with py: prefix
- ✅ **Execution validation** - 100% of generated code runs correctly
- ✅ **VS Code extension** - Basic syntax highlighting for .vl files
- ✅ **Comprehensive test suite** - 51/51 tests passing (100%)

### What's In Progress 🚧

- 🚧 **JavaScript compiler** - Loops, data pipelines, API calls
- 🚧 **Error handling** - Meaningful error messages
- 🚧 **Standard library** - Built-in functions
- 📋 **TypeScript compiler** - Type-safe JavaScript generation
- 📋 **Debugger** - Step-through debugging
- 📋 **REPL** - Interactive shell

---

## Quick Start

### Prerequisites

- Python 3.8 or higher
- No external dependencies (uses only Python standard library)

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
