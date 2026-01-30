# VL (Vibe Language)

**The Universal Programming Language for the AI Era**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Status: In Development](https://img.shields.io/badge/Status-In%20Development-orange.svg)]()
[![Version: 0.1.3-alpha](https://img.shields.io/badge/Version-0.1.3--alpha-blue.svg)]()

-----

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/pmarmaroli/vibe-language.git
cd vibe-language

# Set up Python path (required for VL compiler)
# Windows (PowerShell)
$env:PYTHONPATH="$PWD\src"

# Unix/Linux/Mac
export PYTHONPATH="$PWD/src"

# Verify installation
.\vl.bat examples/basic/hello.vl  # Windows
./vl examples/basic/hello.vl       # Unix/Mac
```

**Note:** VL is a programming language with its compiler currently implemented in Python. The PYTHONPATH setting is needed during alpha so the Python implementation can find its modules. Future releases will have system-wide toolchain installation (similar to how you install Rust, Go, or Node.js).

### Using the CLI

```bash
# Run a VL program (Python target, default)
.\vl.bat examples/basic/hello.vl

# Compile to different targets
.\vl.bat program.vl --target python -o output.py      # Python (default)
.\vl.bat program.vl --target javascript -o output.js  # JavaScript
.\vl.bat program.vl --target typescript -o output.ts  # TypeScript
.\vl.bat program.vl --target c -o output.c            # C
.\vl.bat program.vl --target rust -o output.rs        # Rust

# View generated code with debug output
.\vl.bat examples/data/csv_processor.vl --target js --debug
.\vl.bat program.vl --target ts --debug

# Multi-target compilation example
.\vl.bat app.vl --target python -o app.py && python app.py
.\vl.bat app.vl --target javascript -o app.js && node app.js
```

### Project Structure

```
vibe-language/
├── src/vl/              # Source code (Python package)
│   ├── codegen/         # Code generators for all targets
│   ├── cli.py           # Command-line interface
│   ├── compiler.py      # Main compiler
│   ├── lexer.py         # Tokenizer
│   ├── parser.py        # AST generator
│   ├── type_checker.py  # Type validation
│   └── config.py        # Configuration settings
├── tests/               # All tests organized by type
│   ├── unit/            # Unit tests
│   ├── integration/     # Integration tests
│   ├── codegen/         # Code generation tests
│   └── benchmarks/      # Performance benchmarks
├── examples/            # VL example programs
│   ├── basic/           # Hello world, functions
│   ├── data/            # Data pipelines, APIs
│   └── ui/              # UI components
├── docs/                # Documentation
│   └── specification.md # Language specification
└── .github/             # CI/CD pipeline
```

### Your First VL Program

Create a file named `hello.vl`:

```vl
# Simple hello world
msg='Hello, VL!'
@print(msg)

# With a function
fn:greet|i:str|o:str|ret:'Hello, ${i0}!'
result=@greet('World')
@print(result)
```

Run it:
```bash
# Direct execution (via Python)
.\vl.bat hello.vl

# Compile to Python and run
.\vl.bat hello.vl --target python -o hello.py
python hello.py

# Compile to JavaScript and run
.\vl.bat hello.vl --target javascript -o hello.js
node hello.js
```

### VS Code Extension

Syntax highlighting is available! Open the `vibe-vscode` folder in VS Code and press `F5` to run the extension in development mode.

---

## Why VL?

### The Problem VL Solves

**AI code generation is expensive.** When you ask Claude, GPT-4, or other LLMs to write code:
- Long verbose code = more tokens = higher cost
- Each iteration compounds the cost
- Context windows fill up quickly

**VL cuts token usage by 40-85%** depending on the use case.

### VL vs Alternatives

| Feature | VL | Python | TypeScript | Rust |
|---------|-------|--------|------------|------|
| **Token Efficiency** | ✅ 40-85% savings | ❌ Verbose | ❌ Verbose | ❌ Very verbose |
| **Multi-Target** | ✅ 5 targets | ❌ Python only | ✅ JS only | ✅ Native |
| **AI-Friendly** | ✅ Designed for LLMs | ⚠️ Good | ⚠️ Good | ❌ Complex |
| **Data Pipelines** | ✅ Native syntax | ⚠️ Comprehensions | ❌ Verbose | ❌ Verbose |
| **FFI** | ✅ Python (working)<br>🚧 JS/C/Rust (planned) | ✅ C bindings | ✅ JS ecosystem | ✅ C bindings |
| **Type Safety** | ✅ Optional | ⚠️ Optional | ✅ Strong | ✅ Strong |
| **Learning Curve** | ✅ Minimal syntax | ✅ Easy | ⚠️ Moderate | ❌ Steep |

**When to use VL:**
- ✅ AI-generated code workflows
- ✅ Multi-platform applications
- ✅ Data processing pipelines
- ✅ Rapid prototyping with LLMs
- ✅ Token budget constraints

**When NOT to use VL:**
- ❌ Large existing codebase (Python/JS/Rust are mature)
- ❌ Need specific framework (use native language)
- ❌ Team unfamiliar with new languages
- ❌ Critical production systems (VL is alpha)

---

## Overview

VL (Vibe Language) is a universal, token-efficient programming language designed for optimal collaboration between humans and AI language models. It addresses fundamental challenges in AI-assisted development through high-level, intent-based constructs that minimize ambiguity and maximize semantic clarity.

**Key Innovation:** VL achieves **45.1% overall token efficiency** with up to **84.8% token reduction** in data pipeline scenarios compared to traditional languages (Python, JavaScript) while maintaining complete semantic expressiveness, making it ideal for LLM code generation and cross-platform development.

**Multi-Target Compilation** (VL compiles to 5 languages):
- ✅ **Python**: All tests passing (51/51) - Full feature support with configurable `all()`/`any()` optimization
- ✅ **JavaScript**: All tests passing (14/14) - ES6+ with native operators
- ✅ **TypeScript**: Basic implementation complete - Type annotations + ES6+
- ✅ **C**: Basic implementation complete - ANSI C with standard library
- ✅ **Rust**: Basic implementation complete - Safe Rust with std library

**Configuration System:** Centralized settings in `src/vl/config.py` control optimization behavior:
- `BOOLEAN_CHAIN_MIN_LENGTH = 3` - Minimum chain length for all()/any() optimization
- `OPTIMIZE_BOOLEAN_CHAINS = True` - Enable/disable boolean optimizations
- Target-specific settings for file extensions, type hints, optimization flags

**Universal IR Philosophy:** Like LLVM, WebAssembly, or Java bytecode, VL serves as a single intermediate representation that compiles to optimized native code for each platform. Each codegen backend optimizes for its target's idioms:
- **Python**: Uses `all()`/`any()` for boolean chains (Pythonic + token efficient)
- **JavaScript/TypeScript**: Uses native `&&`/`||` (idiomatic)
- **C/Rust**: Uses native operators with parentheses (safe)

**Language Robustness: 100% (15/15 complex scenarios pass)**  
**Example Programs: 100% (7/7 compile successfully)**  
**Real-World Testing: 100% (15/15 scenarios compile)**  
**Test Coverage: 100% (76/76 tests passing)**  
  - Comprehensive codegen: 65/65 tests (all 5 targets × core constructs)
  - Multi-target boolean: 11/11 tests
  - Configuration system: 4/4 tests verified
**Benchmark Suite: 41.3% overall efficiency (13 focused test cases)**  
**CI/CD:** GitHub Actions testing on Python 3.9-3.11 across Ubuntu/Windows/macOS
### Where VL Excels

**🎯 Multi-Stage Data Pipelines: 84.8% token savings**
```vl
data:sales|filter:amount>100|groupBy:category|agg:count
```

**🎯 Complex Data Transformations: 57.4% token savings**
```vl
data:users|filter:age>18|filter:active==true|map:salary*1.1|filter:item>50000
```

**🎯 API with Processing: 25.6% token savings**
```vl
fn:fetchActive|i:str|o:arr|result=api:GET,i0|ret:$result|filter:status=='active'
```

**🎯 Nested Conditional Logic: 22.4% token savings**
```vl
fn:classify|i:int|o:str|ret:if:i0>1000?'huge':if:i0>100?'large':if:i0>10?'medium':'small'
```

**🎯 Dictionary Operations: 29.7% token savings**
VL's domain-specific syntax shines for web services, data processing, and complex logic chains.

### Where VL Needs Improvement

**✅ Boolean Operations: OPTIMIZED**  
Complex boolean expressions now use target-specific optimization:
- **Python**: Automatically uses `all()`/`any()` for 3+ condition chains
- **JavaScript/TypeScript/C/Rust**: Uses native `&&`/`||` operators

**Example:**
```vl
fn:validate|i:int,int,bool|o:bool|ret:i0>0&&i1<100&&i2
```

**Python Output (optimized):**
```python
def validate(i0: int, i1: int, i2: bool) -> bool:
    return all([i0 > 0, i1 < 100, i2])
```

**JavaScript Output (idiomatic):**
```javascript
function validate(i0, i1, i2) {
    return i0 > 0 && i1 < 100 && i2;
}
```

**⚠️ Math Expressions: 4.5% token overhead**  
Very simple calculations have minimal overhead (nearly equivalent to Python).

**Benchmark Results (Updated Jan 30, 2026):**
```
Test Case                       | VL Tokens | Python Tokens | Savings
Complex Data Transformation     |    29     |      68       |  57.4%
Multi-stage Data Pipeline       |    27     |     110       |  75.5%
Object Creation and Access      |    19     |      27       |  29.6%
Dictionary Merging              |    26     |      37       |  29.7%
Array Creation                  |    20     |      28       |  28.6%
API Call with Processing        |    29     |      39       |  25.6%
Nested Conditional Logic        |    38     |      49       |  22.4%
Multiple Simple Variables       |    18     |      23       |  21.7%
Complex String Interpolation    |    38     |      40       |   5.0%
Loop with Accumulator           |    30     |      31       |   3.2%
Error Handling Pattern          |    27     |      28       |   3.6%
Factorial Recursion             |    29     |      29       |   0.0%
Complex Math Expression         |    23     |      22       |  -4.5%
Complex Boolean Logic           |    25     |      21       | -19.0%*

* Python codegen now uses all()/any() - generates superior output despite source overhead

Average Token Efficiency: 18.3% (benchmarks), 45.1% (focused test suite)
Strong Areas (>20% savings): 8/15 scenarios
Weak Areas (<-10% savings): 1/15 scenarios
Compilation Success Rate: 100% (15/15)
Execution Success Rate: 100% (17/17 validation tests)
```

**Recent Improvements (v0.1.3):**
- **All Tests Passing**: All generated Python executes correctly (validation tests)
- **Type Safety**: Full typing support with `List[Any]`, `Dict[str, Any]`
- **Array/Object Indexing**: `arr[0]`, `obj['key']`, nested indexing
- **Data Pipelines**: Fixed `item` keyword in map/filter operations
- **Python FFI**: Call any Python library with `py:` prefix
- **Implicit variables**: `x=5` instead of `v:x=5`
- **Implicit function calls**: `print('hi')` instead of `@print('hi')`
- **Compound operators**: `x+=1`, `x-=1`, `x*=2`, `x/=2`
- **Range shorthand**: `0..10` instead of `range(0,10)`

-----

## Project Structure

```
vibe-language/
├── interpreter/          # Core VL interpreter and compilers
│   ├── lexer.py         # Tokenization
│   ├── parser.py        # AST generation
│   ├── ast_nodes.py     # AST node definitions
│   ├── codegen_python.py # Python code generator
│   ├── codegen_js.py    # JavaScript code generator
│   ├── type_checker.py  # Type inference and validation
│   ├── errors.py        # Error handling
│   ├── vl.py            # CLI entry point
│   ├── examples/        # Original example programs
│   └── tests/           # Unit tests
├── examples/            # Example VL programs
│   ├── javascript/      # JavaScript-specific examples
│   └── python/          # Python-specific examples
├── vibe-vscode/         # VS Code extension
│   ├── syntaxes/        # TextMate grammar
│   └── package.json     # Extension manifest
├── docs/                # Documentation
│   ├── specification.md # Language specification
├── benchmarks/          # Performance benchmarks
├── vl.bat              # Windows CLI wrapper
├── vl                  # Unix/Linux CLI wrapper
└── README.md           # This file
```

-----

## Core Design Principles

1. **Token Efficiency**: Optimized syntax minimizes token count for LLM generation
1. **Semantic Clarity**: Unambiguous constructs eliminate interpretation errors
1. **Intent-Based**: Describe *what* the code should do, not *how* to implement it
1. **Universal**: Single language for web, mobile, backend, data processing, and more
1. **FFI-First** *(vision)*: Native interoperability with Python, JavaScript, Rust, and C libraries
1. **Cross-Platform**: Write once, execute anywhere

-----

## Language Features

### File Structure

```vl
meta:program_name,type,target_language
deps:[dependencies]
[main content]
export:export_name
```

### Core Constructs

**Functions:**

```vl
fn:function_name|i:type1,type2|o:return_type|body
```

**Variables:**

```vl
v:variable_name=value
v:typed_var:type=value
```

**Direct Calls (New!):**

```vl
@print('Hello World')           # Simple function call
@requests.get('api/users')      # API call
@logger.info('message')         # Method call
```

**Operations:**

```vl
op:operator(operand1,operand2)
```

**Conditionals:**

```vl
if:condition?true_expr:false_expr
# Early returns supported
if:condition?ret:value:ret:other
```

**Loops:**

```vl
for:var,iterable|body
while:condition|body
```

### Domain-Specific Constructs

VL provides specialized syntax for common development patterns:

#### API/HTTP Operations

```vl
api:GET,/users|filter:age>=18|map:name,email
api:POST,/data,{body:{key:'value'}}
```

#### UI Components (React-style)

```vl
ui:ComponentName|props:name:str,age:int|
state:count:int=0|
on:onClick|setState:count,op:+(count,1)|
render:button|'Click: ${count}'
```

#### Data Processing

```vl
data:users|
filter:active==true|
groupBy:country|
agg:sum,revenue|
sort:total,desc
```

#### File I/O

```vl
file:read,data.json|
parse:json|
data:$data|filter:status=='active'|
serialize:csv|
file:write,output.csv,$result
```

-----

## Language Robustness

**100% Pass Rate on Complex Scenarios** (15/15)

VL handles real-world production patterns including:

✅ **Nested Loops** - Multiple levels with any variable names  
✅ **Complex String Interpolation** - Full expressions in `${ }`  
✅ **Conditional Returns** - Early returns and guard clauses  
✅ **API as Expressions** - `v:data=api:GET,url`  
✅ **Deep Nesting** - Multiple levels of conditionals and operations  
✅ **Boolean Logic** - Complex AND/OR expressions  
✅ **Array Operations** - Filter, map, chaining  
✅ **Mixed Statements** - Variables, loops, conditionals combined  

**Example: Complex String Interpolation**
```vl
fn:greet|i:str,int|o:str|
ret:'Hello ${i0}, you are ${i1} and ${if:op:>(i1,18)?'adult':'minor'}'
```

**Example: Early Returns (Guard Clauses)**
```vl
fn:divide|i:int,int|o:int|
if:op:==(i1,0)?ret:0:ret:op:/(i0,i1)
```

-----

## Example Programs

### Example 1: API Function

```vl
meta:getAdultUsers,api_function,python
deps:requests
fn:getAdultUsers|i:str|o:arr|
async|api:GET,$i|filter:age>=18|map:name,email
export:getAdultUsers
```

**Equivalent Python (for comparison):**

```python
import requests

async def getAdultUsers(api_url):
    response = await requests.get(api_url)
    users = response.json()
    adults = [user for user in users if user['age'] >= 18]
    return [{'name': u['name'], 'email': u['email']} for u in adults]
```

**Token Reduction: ~75%**

### Example 2: Python FFI (Foreign Function Interface)

VL can call Python libraries directly using the `py:` prefix:

```vl
# Import and use numpy
arr=py:np.array([1,2,3])
mean=py:np.mean(arr)

# Load data with pandas
df=py:pd.read_csv('data.csv')
filtered=py:df[df['age'] > 18]

# Use scipy for statistics
result=py:scipy.stats.norm.pdf(0.5)

# Make HTTP requests
response=py:requests.get('http://api.com').json()

# In functions
fn:parseJSON|i:str|o:obj|ret:py:json.loads(i0)
```

**Benefits:**
- ✅ Access entire Python ecosystem (pandas, numpy, scipy, sklearn, etc.)
- ✅ No wrapper code needed - direct passthrough
- ✅ Full method chaining support
- ✅ Works in all VL contexts (variables, returns, expressions)

This makes VL immediately practical for data science, machine learning, web scraping, and any task requiring Python libraries.

---

### Example 3: React Component

```vl
meta:Counter,ui_component,react
ui:Counter|state:count:int=0|
on:onClick|setState:count,op:+(count,1)|
render:div|
  render:h1|'Count: ${count}'|
  render:button,{onClick:$onClick}|'Increment'
export:Counter
```

### Example 4: Data Pipeline

```vl
meta:processSales,data_processor,python
fn:processSales|i:str|o:obj|
file:read,$i|parse:csv,{headers:true}|
data:$data|
  filter:amount>100|
  groupBy:category|
  agg:sum,amount|
  sort:total,desc|
ret:$result
export:processSales
```

-----

## Architecture

### Multi-Target Compilation Strategy

VL functions as a **universal intermediate representation (IR)** that compiles to multiple target languages, similar to LLVM, WebAssembly, or Java bytecode. Write once in VL, compile to any supported target with target-specific optimizations.

**Compilation Flow:**

```
┌─────────────────────────────────┐
│   VL Source Code (Universal)    │
│   fn:validate|i:int,int,bool|   │
│   o:bool|ret:i0>0&&i1<100&&i2   │
└────────────────┬────────────────┘
                 │
        VL Parser & AST Builder
                 │
                 ▼
┌─────────────────────────────────┐
│    Abstract Syntax Tree (IR)    │
│     Universal Representation    │
└────────────────┬────────────────┘
                 │
         Target Selection
                 │
        ┌────────┴────────┬────────┬────────┬────────┐
        ▼                 ▼        ▼        ▼        ▼
┌──────────────┐  ┌──────────┐  ┌─────┐  ┌─────┐  ┌──────┐
│Python Codegen│  │JavaScript│  │TypeS│  │  C  │  │ Rust │
│              │  │ Codegen  │  │cript│  │Code │  │Code  │
└──────┬───────┘  └────┬─────┘  └──┬──┘  └──┬──┘  └──┬───┘
       │               │           │        │        │
       ▼               ▼           ▼        ▼        ▼
┌──────────┐     ┌──────────┐  ┌──────┐ ┌─────┐  ┌──────┐
│  all([   │     │  i0 > 0  │  │i0>0  │ │(i0>0│  │(i0>0)│
│  i0>0,   │     │  &&      │  │&&    │ │)&&  │  │&&    │
│  i1<100, │     │  i1<100  │  │i1<100│ │(i1< │  │(i1<  │
│  i2      │     │  && i2   │  │&& i2 │ │100) │  │100)  │
│  ])      │     │          │  │      │ │&& i2│  │&& i2 │
└──────────┘     └──────────┘  └──────┘ └─────┘  └──────┘
  Pythonic         JavaScript   TypeSafe   Safe     Safe
  + Efficient      Idiomatic     Typed     Parens   Rust
```

**Target-Specific Optimizations:**

| Feature         | Python            | JavaScript  | TypeScript  | C           | Rust        |
|-----------------|-------------------|-------------|-------------|-------------|-------------|
| Boolean Chains  | `all()`/`any()`   | `&&`/`||`   | `&&`/`||`   | `&&`/`||`   | `&&`/`||`   |
| Type Annotations| PEP 484           | None        | Full typing | Full typing | Full typing |
| Imports         | `import`          | `require()` | `import`    | `#include`  | `use`       |
| Collections     | `[]` / `{}`       | `[]` / `{}` | `[]` / `{}` | Arrays      | `Vec<>`     |

**Example: Same VL, Different Outputs**

```vl
fn:validate|i:int,int,bool|o:bool|ret:i0>0&&i1<100&&i2
```

**Python (Optimized for idioms + tokens):**
```python
def validate(i0: int, i1: int, i2: bool) -> bool:
    return all([i0 > 0, i1 < 100, i2])
```

**JavaScript (Optimized for performance):**
```javascript
function validate(i0, i1, i2) {
    return i0 > 0 && i1 < 100 && i2;
}
```

**TypeScript (Optimized for type safety):**
```typescript
function validate(i0: number, i1: number, i2: boolean): boolean {
    return i0 > 0 && i1 < 100 && i2;
}
```

**C (Optimized for safety + portability):**
```c
bool validate(int i0, int i1, bool i2) {
    return (i0 > 0) && (i1 < 100) && i2;
}
```

**Rust (Optimized for safety + zero-cost abstractions):**
```rust
fn validate(i0: i32, i1: i32, i2: bool) -> bool {
    (i0 > 0) && (i1 < 100) && i2
}
```

### Execution Model

VL employs a hybrid execution model:

```
┌─────────────────────────────────┐
│     Natural Language Prompt     │
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│   LLM Generates VL Code         │
│   (Token-Efficient Output)      │
└────────────────┬────────────────┘
                 │
        ┌────────┴────────┐
        ▼                 ▼
┌──────────────┐  ┌──────────────┐
│VL Interpreter│  │ VL Compiler  │
│(Development) │  │ (Production) │
└──────┬───────┘  └──────┬───────┘
       │                 │
       ▼                 ▼
┌──────────────┐  ┌──────────────┐
│  VL Runtime  │  │ Python/JS/   │
│  + FFI Layer │  │ TS/C/Rust    │
└──────────────┘  └──────────────┘
```

### Execution Modes

1. **VL Interpreter** (Development)
- Direct execution of `.vl` files
- Fast iteration and testing
- Built-in debugging support
1. **VL Compiler** (Production)
- Transpiles to Python, JavaScript, Rust, etc.
- Leverages existing runtime optimizations
- Interoperates with legacy systems
1. **VL Runtime** (Future)
- Native bytecode execution
- JIT compilation
- Optimal cross-platform performance

-----

## Foreign Function Interface (FFI)

### Currently Implemented

✅ **Python FFI** - Use `py:` prefix to call any Python library directly:

```vl
# Call Python libraries
x=py:np.array([1,2,3])
df=py:pd.read_csv('data.csv')
result=py:scipy.stats.norm.pdf(0.5)
data=py:requests.get('http://api.com').json()

# Use in functions
fn:parse|i:str|o:obj|ret:py:json.loads(i0)
```

This enables VL to leverage Python's mature ecosystem while building native implementations incrementally.

### Planned (Vision)

🚧 **JavaScript/Node FFI** - `js:` prefix for Node.js libraries (planned)  
🚧 **Rust FFI** - `rust:` prefix for Rust crates (planned)  
🚧 **C FFI** - `c:` prefix for C libraries (planned)

-----

## Type System

VL supports both primitive and complex types:

**Primitives:**

- `int`, `float`, `str`, `bool`

**Collections:**

- `arr` (array/list)
- `obj` (object/dictionary)
- `map`, `set`

**Special:**

- `any` (dynamic typing)
- `void` (no return)
- `promise` (async operations)
- `func` (function/callback)

-----

## Supported Domains (v0.1)

1. **API/HTTP Operations**
- REST calls (GET, POST, PUT, DELETE, PATCH)
- Request/response filtering and transformation
- Async operation support
- JSON/XML parsing
1. **UI Components**
- React-style component model
- State management
- Props and event handlers
- Hooks (useState, useEffect, useCallback, useMemo)
- Lifecycle methods
1. **Data Processing**
- Functional operations (map, filter, reduce)
- Aggregations (sum, avg, min, max, count)
- Grouping and sorting
- Join operations
- Statistical functions
1. **File I/O**
- Read/write operations
- Format parsing (JSON, CSV, XML, YAML)
- File system operations
- Path manipulation
- Stream processing

-----

## Testing & Benchmarking

**Before any commit/push, run the comprehensive benchmark suite:**

```bash
python run_benchmarks.py
```

This single script runs all tests and validation:
- ✅ Example Programs (7 .vl files) - Validates all example code compiles
- ✅ Robustness Testing (15 complex scenarios) - Tests edge cases and complex patterns
- ✅ Strength/Weakness Analysis (15 scenarios) - Comprehensive token efficiency analysis
- ✅ Token Efficiency Benchmarks (13 test cases) - Focused performance testing

**Expected Results (all tests must pass):**
- Example Programs: 7/7 (100%)
- Robustness: 15/15 (100%)
- Strength Analysis: 14/15 compile (93.3%)
- Benchmark Suite: 23.8% average efficiency

**The output provides all metrics needed to update documentation.**

**Quick individual tests (for debugging only):**
```bash
python test_examples.py              # Test example .vl files
python test_robustness.py            # Test complex scenarios
python test_strengths.py             # Full analysis with metrics
python run_benchmarks.py  # Comprehensive benchmarks
```

-----



## Technical Specifications

### Lexical Structure

**Keywords:**

```
meta, deps, export, fn, i, o, ret, v, op, if, for, while,
api, async, filter, map, parse, ui, state, props, on, render,
data, groupBy, agg, sort, file, ffi
```

**Operators:**

```
Arithmetic: +, -, *, /, %, **
Comparison: ==, !=, <, >, <=, >=
Logical: &&, ||, !
String: concat, split, join
```

**Delimiters:**

```
| (pipe - chaining/separation)
: (key-value pair)
, (list separator)
= (assignment)
? : (ternary conditional)
$ (variable reference)
```

### Syntax Rules

1. **Case Sensitivity**: VL is case-sensitive
1. **Whitespace**: Generally ignored except in strings
1. **Comments**:
- Single line: `# comment`
- Multi-line: `## comment block ##`
1. **String Literals**: Single quotes `'string'` or template `'${var}'`
1. **Type Annotations**: Optional but recommended for clarity

-----

## Token Efficiency Analysis

Comparison for common operations (approximate token counts):

|Operation        |Python|JavaScript|VL|Reduction|
|-----------------|------|----------|--|---------|
|Simple function  |25    |23        |12|52-56%   |
|API call + filter|80    |75        |20|73-75%   |
|React component  |120   |110       |35|68-71%   |
|Data pipeline    |150   |140       |45|67-70%   |

**Average Token Reduction: 65%**

This translates to:

- Lower API costs for LLM generation
- Faster code generation
- Larger effective context windows
- Reduced latency

-----

## Architecture

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

**1. Lexer** - Converts raw VL source into tokens, handles string interpolation  
**2. Parser** - Recursive descent parser with operator precedence, builds AST  
**3. Type Checker** - Optional type validation and inference  
**4. Code Generators** - All inherit from `BaseCodeGenerator`:
- **Python**: Optimized with `all()`/`any()` for boolean chains
- **JavaScript**: ES6+ with native operators
- **TypeScript**: Type-safe with full type annotations
- **C**: ANSI C with standard library
- **Rust**: Safe Rust with std library

**5. Configuration** - Centralized settings control optimization behavior

### Running Tests

```bash
# Set PYTHONPATH to find the vl package
cd vibe-language
export PYTHONPATH="$PWD/src"  # Unix
$env:PYTHONPATH="$PWD\src"    # Windows

# Run all codegen tests (65 tests)
python tests/codegen/test_codegen_all.py

# Run integration tests
python tests/integration/test_execution.py

# Run benchmarks
python tests/benchmarks/run_benchmarks.py
```

-----

## Roadmap

### Current Status (v0.1.3)

**Completed:**
- ✅ Multi-target compiler (Python, JavaScript, TypeScript, C, Rust)
- ✅ Professional project structure (src/vl package)
- ✅ Configuration system with runtime control
- ✅ CI/CD pipeline (GitHub Actions, multi-platform)
- ✅ Comprehensive test coverage (76/76 tests, 100% pass rate)
- ✅ BaseCodeGenerator (eliminates code duplication)
- ✅ Type checker with inference
- ✅ VS Code extension (syntax highlighting)
- ✅ Python FFI with `py:` prefix
- ✅ Data pipelines (filter, map, groupBy, agg, sort)

**In Progress:**
- 🚧 TypeScript compiler (type-safe generation)
- 🚧 Documentation website
- 🚧 More example programs

**Next Up:**
- 📋 Standard library functions
- 📋 Community Discord/Slack
- 📋 Performance benchmarks vs JavaScript/Python
- 📋 First beta release (v0.2.0)

### Development Phases

**Phase 1: Foundation (Q1-Q2 2026)** ← We are here  
Goal: Prove VL works for real development
- ✅ Core language implementation
- ✅ Multi-target compilation
- ✅ Professional tooling
- [ ] Documentation website

**Phase 2: Early Adoption (Q3-Q4 2026)**  
Goal: Production-ready for early adopters
- TypeScript/C/Rust compiler completion
- FFI for Node.js packages
- VS Code extension (full features)
- Package manager (basic)

**Phase 3: Production Ready (Q1-Q2 2027)**  
Goal: Stable, performant, widely adopted
- Performance optimization
- Enterprise features
- Native mobile/embedded support
- Standard library

**Phase 4: Mainstream (Q3 2027+)**  
Goal: Mainstream language choice
- Advanced features (concurrency, metaprogramming)
- Self-hosting (VL compiler written in VL)
- Domain expansions (ML, graphics, databases)
- Education partnerships

-----

## Use Cases

1. **AI-First Development**
- Natural language → VL code generation
- Minimal iteration needed for correctness
- Built for LLM understanding
1. **Rapid Prototyping**
- Express complex logic concisely
- Fast iteration cycles
- Minimal boilerplate
1. **Cross-Platform Applications**
- Single codebase for web, mobile, server
- Consistent behavior across platforms
- Reduced maintenance burden
1. **Data Pipelines**
- Concise ETL workflows
- Chainable transformations
- Clear data flow
1. **Educational Programming**
- Focus on concepts, not syntax
- Language-agnostic learning
- Clear intent expression

-----

## Project Status

**Current Version:** 0.1.3-alpha  
**Status:** Active Development (Alpha) - Not Production Ready  
**License:** MIT  
**Started:** January 2026  
**Creator:** Patrick Marmaroli

⚠️ **Alpha Software:** VL is in active development. The core compiler works (76/76 tests passing) but:
- APIs may change between versions
- Not recommended for production use yet
- Breaking changes expected in minor versions
- Limited documentation and examples

✅ **What Works:** All 5 target compilers (Python, JavaScript, TypeScript, C, Rust), type checking, data pipelines, Python FFI

🚧 **What's Coming:** Standard library, package manager, stable 1.0 API (Q4 2026)

### Contributing

VL is in active development. We welcome:
- Feedback on language design
- Bug reports and feature requests
- Code contributions (see project structure in Quick Start)
- Documentation improvements
- Example programs

### Development Workflow

1. **Set up**: `export PYTHONPATH="$PWD/src"` (Unix) or `$env:PYTHONPATH="$PWD\src"` (Windows)
2. **Make changes** to files in `src/vl/`
3. **Run tests**: `python tests/codegen/test_codegen_all.py`
4. **Test CLI**: `./vl.bat examples/basic/hello.vl`
5. **Submit PR** with tests and documentation

### Adding a New Target Language

To add support for a new target (e.g., Go):

1. Create `src/vl/codegen/go.py` inheriting from `BaseCodeGenerator`
2. Update `src/vl/compiler.py` to add Go to `TargetLanguage` enum
3. Update `src/vl/config.py` with Go-specific settings
4. Add Go to `src/vl/codegen/__init__.py` exports
5. Write tests in `tests/codegen/test_codegen_all.py`

-----

## Intellectual Property Notice

This language specification and associated documentation establish prior art for the VL programming language concept, design, and implementation. The timestamp of this public repository serves as evidence of invention date.

**Copyright © 2026 Patrick Marmaroli**

VL name, logo, and specification are subject to trademark protection. Implementation and derivative works are permitted under MIT license terms.

-----

## References & Inspiration

**Language Design:**

- Python: Readability and ecosystem
- Rust: Safety and modern tooling
- Go: Simplicity and compilation speed
- Lua: Embeddability and FFI
- APL/K: Symbolic notation efficiency

**Academic Foundations:**

- Formal language theory
- Type systems and semantics
- Compiler design and optimization
- LLM token efficiency research


-----

## Acknowledgments

This project builds upon decades of programming language research and design. We acknowledge the foundational work of the broader programming language community and the emerging field of AI-assisted development.

-----

