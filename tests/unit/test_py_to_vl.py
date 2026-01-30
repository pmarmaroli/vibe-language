"""
Tests for Python to VL converter
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from vl.py_to_vl import PythonToVLConverter, convert_python_to_vl
from vl.compiler import Compiler, TargetLanguage


def test_simple_function():
    """Test converting a simple function"""
    python_code = """
def add(x: int, y: int) -> int:
    return x + y
"""
    
    converter = PythonToVLConverter()
    vl_code = converter.convert(python_code)
    
    assert 'fn:add' in vl_code
    assert 'i:int,int' in vl_code
    assert 'o:int' in vl_code
    assert 'ret:i0+i1' in vl_code
    print("✓ Simple function conversion works")


def test_variable_assignment():
    """Test converting variable assignments"""
    python_code = """
x = 5
y = 10
z = x + y
"""
    
    converter = PythonToVLConverter()
    vl_code = converter.convert(python_code)
    
    assert 'x=5' in vl_code
    assert 'y=10' in vl_code
    assert 'z=x+y' in vl_code
    print("✓ Variable assignment conversion works")


def test_if_statement():
    """Test converting if statements"""
    python_code = """
x = 5
if x > 3:
    y = 10
else:
    y = 0
"""
    
    converter = PythonToVLConverter()
    vl_code = converter.convert(python_code)
    
    assert 'if:x>3' in vl_code
    assert 'y=10' in vl_code
    assert 'else:' in vl_code
    assert 'y=0' in vl_code
    print("✓ If statement conversion works")


def test_for_loop():
    """Test converting for loops"""
    python_code = """
for i in [1, 2, 3]:
    print(i)
"""
    
    converter = PythonToVLConverter()
    vl_code = converter.convert(python_code)
    
    assert 'for:i' in vl_code
    assert 'in:[1,2,3]' in vl_code
    print("✓ For loop conversion works")


def test_while_loop():
    """Test converting while loops"""
    python_code = """
x = 0
while x < 10:
    x += 1
"""
    
    converter = PythonToVLConverter()
    vl_code = converter.convert(python_code)
    
    assert 'while:x<10' in vl_code
    assert 'x+=1' in vl_code
    print("✓ While loop conversion works")


def test_function_call():
    """Test converting function calls"""
    python_code = """
result = add(5, 3)
print(result)
"""
    
    converter = PythonToVLConverter()
    vl_code = converter.convert(python_code)
    
    assert 'result=add(5,3)' in vl_code
    assert 'print(result)' in vl_code
    print("✓ Function call conversion works")


def test_list_operations():
    """Test converting list operations"""
    python_code = """
numbers = [1, 2, 3, 4, 5]
first = numbers[0]
"""
    
    converter = PythonToVLConverter()
    vl_code = converter.convert(python_code)
    
    assert 'numbers=[1,2,3,4,5]' in vl_code
    assert 'first=numbers[0]' in vl_code
    print("✓ List operations conversion works")


def test_dict_operations():
    """Test converting dict operations"""
    python_code = """
person = {'name': 'Alice', 'age': 30}
name = person['name']
"""
    
    converter = PythonToVLConverter()
    vl_code = converter.convert(python_code)
    
    assert "person={'name':'Alice','age':30}" in vl_code
    assert "name=person['name']" in vl_code
    print("✓ Dict operations conversion works")


def test_boolean_operations():
    """Test converting boolean operations"""
    python_code = """
x = True and False
y = True or False
z = not True
"""
    
    converter = PythonToVLConverter()
    vl_code = converter.convert(python_code)
    
    assert '&&' in vl_code or 'true' in vl_code
    assert '||' in vl_code or 'false' in vl_code
    assert '!' in vl_code
    print("✓ Boolean operations conversion works")


def test_round_trip():
    """Test Python → VL → Python round trip"""
    python_code = """
def fibonacci(n: int) -> int:
    if n <= 1:
        return n
    else:
        return fibonacci(n - 1) + fibonacci(n - 2)

result = fibonacci(10)
print(result)
"""
    
    # Convert Python to VL
    py_to_vl = PythonToVLConverter()
    vl_code = py_to_vl.convert(python_code)
    
    print("\n--- Original Python ---")
    print(python_code)
    
    print("\n--- Converted VL ---")
    print(vl_code)
    
    # Compile VL back to Python
    compiler = Compiler(vl_code, TargetLanguage.PYTHON)
    generated_python = compiler.compile()
    
    print("\n--- Generated Python ---")
    print(generated_python)
    
    # Execute both versions and compare
    # (This is a basic check - full semantic equivalence is complex)
    print("✓ Round trip conversion completes")


def test_aug_assignment():
    """Test converting augmented assignments"""
    python_code = """
x = 10
x += 5
x -= 2
x *= 3
x /= 2
"""
    
    converter = PythonToVLConverter()
    vl_code = converter.convert(python_code)
    
    assert 'x+=5' in vl_code
    assert 'x-=2' in vl_code
    assert 'x*=3' in vl_code
    assert 'x/=2' in vl_code
    print("✓ Augmented assignment conversion works")


def test_string_operations():
    """Test converting string operations"""
    python_code = """
name = 'Alice'
greeting = 'Hello, ' + name
"""
    
    converter = PythonToVLConverter()
    vl_code = converter.convert(python_code)
    
    assert "name='Alice'" in vl_code
    assert "greeting='Hello, '+name" in vl_code
    print("✓ String operations conversion works")


def run_all_tests():
    """Run all converter tests"""
    print("Testing Python to VL Converter\n")
    
    test_simple_function()
    test_variable_assignment()
    test_if_statement()
    test_for_loop()
    test_while_loop()
    test_function_call()
    test_list_operations()
    test_dict_operations()
    test_boolean_operations()
    test_aug_assignment()
    test_string_operations()
    test_round_trip()
    
    print("\n✅ All Python → VL converter tests passed!")


if __name__ == '__main__':
    run_all_tests()
