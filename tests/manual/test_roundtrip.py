"""
Test Python → VL → Python round trip for real code
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from vl.py_to_vl import convert_python_to_vl
from vl.compiler import Compiler, TargetLanguage

# Test 1: Simple arithmetic function
python_code_1 = """
def add(x: int, y: int) -> int:
    return x + y
"""

print("=== Test 1: Simple Function ===")
print("Python input:")
print(python_code_1)

vl_code = convert_python_to_vl(python_code_1)
print("\nVL output:")
print(vl_code)

# Compile back to Python
compiler = Compiler(vl_code, TargetLanguage.PYTHON)
generated = compiler.compile()
print("\nGenerated Python:")
print(generated)
print()

# Test 2: Conditional logic
python_code_2 = """
def max_value(a: int, b: int) -> int:
    if a > b:
        return a
    else:
        return b
"""

print("=== Test 2: Conditional ===")
print("Python input:")
print(python_code_2)

vl_code_2 = convert_python_to_vl(python_code_2)
print("\nVL output:")
print(vl_code_2)

compiler_2 = Compiler(vl_code_2, TargetLanguage.PYTHON)
generated_2 = compiler_2.compile()
print("\nGenerated Python:")
print(generated_2)
print()

# Test 3: Variable manipulation
python_code_3 = """
def process(n: int) -> int:
    result = n * 2
    result += 10
    return result
"""

print("=== Test 3: Variables ===")
print("Python input:")
print(python_code_3)

vl_code_3 = convert_python_to_vl(python_code_3)
print("\nVL output:")
print(vl_code_3)

compiler_3 = Compiler(vl_code_3, TargetLanguage.PYTHON)
generated_3 = compiler_3.compile()
print("\nGenerated Python:")
print(generated_3)
print()

print("✅ All round-trip tests completed!")
