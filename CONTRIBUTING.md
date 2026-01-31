# Contributing to VL (Vibe Language)

Thank you for your interest in contributing to VL! We welcome contributions from the community and are excited to build this language together.

## 🎯 Project Vision

VL is a universal programming language optimized for AI-assisted development. Our goal is to create a token-efficient, unambiguous language that makes collaboration between humans and AI seamless.

## 🚀 Current Status

**Phase 1: Foundation (Q1 2026) - Active Development**

We are in active development with significant progress:
- ✅ VL → Python compiler (100% operational)
- ✅ VL → JavaScript compiler (in progress)
- ✅ VS Code extension (basic syntax highlighting)
- ✅ CLI tools and wrappers
- ✅ Python FFI support
- 🚧 JavaScript compiler completion
- 🚧 TypeScript compiler
- 🚧 Standard library

## 📋 How to Contribute

### Areas Where We Need Help

1. **Core Development**
   - Complete JavaScript compiler (loops, API calls, data pipelines)
   - TypeScript compiler implementation
   - Standard library functions
   - Enhanced FFI support (Node.js modules)
   - Performance optimizations

2. **Documentation**
   - More code examples across all domains
   - Tutorial content
   - API documentation
   - Video demonstrations
   - Translation to other languages

3. **Tooling**
   - VS Code extension enhancements (IntelliSense, code completion)
   - Syntax highlighting for other editors (Sublime, Atom, Vim)
   - Online playground/REPL
   - Testing framework improvements
   - Package manager design

4. **Community**
   - Blog posts and articles
   - Video tutorials
   - Social media content
   - Conference talks
   - Language comparisons and benchmarks

### Getting Started

1. **Read the Documentation**
   - Review the [README.md](README.md) for project overview
   - Read the [Language Specification](docs/specification.md)
   - Check the [Roadmap](docs/roadmap.md) for current status
   - Review [TESTING.md](TESTING.md) for testing guidelines
   - See [CHANGELOG.md](CHANGELOG.md) for recent changes

2. **Set Up Development Environment**
```bash
# Clone the repository
git clone https://github.com/yourusername/vibe-language.git
cd vibe-language

# Test the CLI
.\vl.bat --version

# Run tests
python -m pytest interpreter/tests/ -v
python interpreter/tests/test_js_codegen.py -v
```

3. **Explore the Codebase**
   - `interpreter/` - Core interpreter and compilers
   - `examples/` - Example VL programs
   - `vibe-vscode/` - VS Code extension
   - `docs/` - Documentation files

4. **Check Existing Issues**
   - Look at [open issues](../../issues) to find something to work on
   - Issues labeled `good first issue` are great for newcomers
   - Issues labeled `help wanted` are priorities

3. **Join the Discussion**
   - Open an issue to discuss your idea before starting work
   - Ask questions if anything is unclear
   - Share your thoughts on language design

## 🛠️ Development Setup

### Prerequisites

- Python 3.9+ (for interpreter development)
- Node.js 18+ (for tooling)
- Git

### Local Setup

```bash
# Clone the repository
git clone https://github.com/pmarmaroli/vibe-language.git
cd vibe-language

# Create a virtual environment (Python)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install tiktoken

# Run test suites
python test_examples.py      # Test all example programs
python test_robustness.py    # Test complex scenarios (100% pass rate)
python run_benchmarks.py  # Comprehensive benchmarks
```

## 📝 Contribution Process

### 1. Fork and Clone

```bash
# Fork the repo on GitHub, then:
git clone https://github.com/YOUR_USERNAME/vibe-language.git
cd vibe-language
git remote add upstream https://github.com/pmarmaroli/vibe-language.git
```

### 2. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/issue-description
```

**Branch naming conventions:**
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation changes
- `test/` - Test additions or fixes
- `refactor/` - Code refactoring

### 3. Make Your Changes

- Write clear, concise commit messages
- Follow the coding style (see below)
- Add tests for new functionality
- Update documentation as needed

### 4. Test Your Changes

```bash
# Run tests
pytest

# Run linter
flake8

# Check formatting
black --check .
```

### 5. Commit Your Changes

```bash
git add .
git commit -m "feat: add XYZ feature"
# or
git commit -m "fix: resolve issue with ABC"
```

**Commit message format:**
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `test:` - Test changes
- `refactor:` - Code refactoring
- `chore:` - Maintenance tasks

### 6. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub with:
- Clear title and description
- Reference any related issues (e.g., "Fixes #123")
- Explain what changed and why
- Include screenshots/examples if applicable

## 💻 Coding Standards

### Python (Interpreter/Compiler)

- **Style Guide:** PEP 8
- **Formatter:** Black (line length 100)
- **Linter:** Flake8
- **Type Hints:** Use type hints for all functions
- **Docstrings:** Google style docstrings

**Example:**
```python
def parse_function(vl_code: str) -> FunctionNode:
    """Parse VL function syntax into AST node.
    
    Args:
        vl_code: VL source code string
        
    Returns:
        FunctionNode representing the parsed function
        
    Raises:
        ParseError: If syntax is invalid
    """
    # Implementation
    pass
```

### JavaScript/TypeScript (Tooling)

- **Style Guide:** Airbnb JavaScript Style Guide
- **Formatter:** Prettier
- **Linter:** ESLint
- **Types:** TypeScript preferred for new code

### VL Code Examples

- Follow the [language specification](README.md)
- Include comments explaining the code
- Keep examples focused and concise
- Test that examples work

## 🧪 Testing Guidelines

- Write tests for all new functionality
- Maintain or improve code coverage
- Include both unit tests and integration tests
- Test edge cases and error conditions

**Test structure:**
```python
def test_function_parsing():
    """Test basic function parsing."""
    vl_code = "F:sum|I,I|I|ret:op:+(i0,i1)"
    result = parse_function(vl_code)
    assert result.name == "sum"
    assert len(result.inputs) == 2
```

## 📚 Documentation Guidelines

- Use clear, simple language
- Include code examples
- Explain *why*, not just *what*
- Keep documentation up-to-date with code changes

**Documentation types:**
1. **Code comments** - Explain complex logic
2. **Docstrings** - Document functions/classes
3. **README sections** - High-level explanations
4. **Tutorials** - Step-by-step guides
5. **Reference docs** - Complete API documentation

## 🤝 Code Review Process

All contributions go through code review:

1. **Automated Checks**
   - Tests must pass
   - Linting must pass
   - Code coverage should not decrease

2. **Human Review**
   - At least one maintainer approval required
   - Address review comments promptly
   - Be open to feedback and suggestions

3. **Merge**
   - Squash commits if requested
   - Maintainer will merge when approved

## 🐛 Reporting Bugs

**Before reporting:**
- Check if the issue already exists
- Verify you're using the latest version
- Collect relevant information

**Bug report should include:**
- Clear, descriptive title
- Steps to reproduce
- Expected vs actual behavior
- VL version and environment
- Code samples if applicable
- Error messages/logs

**Use the bug report template:**
```markdown
**Description**
A clear description of the bug.

**To Reproduce**
Steps to reproduce:
1. ...
2. ...

**Expected Behavior**
What should happen.

**Actual Behavior**
What actually happens.

**Environment**
- VL version: X.Y.Z
- OS: [e.g., macOS 14, Ubuntu 22.04]
- Python version: 3.11

**Additional Context**
Any other relevant information.
```

## 💡 Suggesting Features

We love feature suggestions! Before proposing:

1. **Check existing issues/discussions**
2. **Consider if it fits VL's philosophy**
3. **Think about implementation complexity**

**Feature request should include:**
- Use case and motivation
- Proposed syntax/API
- Example code
- Alternatives considered
- Implementation ideas (if any)

## 🌟 Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Credited in relevant documentation

Significant contributors may be invited to join the core team.

## 📞 Getting Help

- **Questions:** Open a [Discussion](../../discussions)
- **Chat:** [Discord/Slack - Coming Soon]
- **Email:** [Coming Soon]

## 📜 Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for all contributors, regardless of:
- Age, body size, disability
- Ethnicity, gender identity and expression
- Level of experience
- Nationality, personal appearance
- Race, religion
- Sexual identity and orientation

### Our Standards

**Positive behavior:**
- Using welcoming and inclusive language
- Being respectful of differing viewpoints
- Gracefully accepting constructive criticism
- Focusing on what's best for the community
- Showing empathy towards others

**Unacceptable behavior:**
- Harassment of any kind
- Trolling, insulting/derogatory comments
- Public or private harassment
- Publishing others' private information
- Other unethical or unprofessional conduct

### Enforcement

Instances of unacceptable behavior may be reported to project maintainers. All complaints will be reviewed and investigated promptly and fairly.

## 📄 License

By contributing to VL, you agree that your contributions will be licensed under the [MIT License](LICENSE).

## 🙏 Thank You

Thank you for contributing to VL! Every contribution, no matter how small, helps make VL better for everyone.

---

**Questions?** Open an issue or start a discussion. We're here to help!

**Happy coding!** 🚀
