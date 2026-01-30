"""
VL Benchmark Suite
Compares token usage between VL source code and generated Python code.
"""

import sys
import os
from pathlib import Path
import time

# Add interpreter directory to path so we can import the compiler
project_root = Path(__file__).parent.parent
interpreter_path = project_root / 'interpreter'
sys.path.append(str(interpreter_path))

try:
    from compiler import Compiler, TargetLanguage
    import tiktoken
except ImportError:
    print("Error: Missing dependencies.")
    print("Please ensure you are in the root directory and have installed requirements.")
    print("  pip install tiktoken")
    sys.exit(1)
except Exception as e:
    print(f"Error importing compiler modules: {e}")
    print(f"Make sure {interpreter_path} exists and contains compiler.py")
    sys.exit(1)

def count_tokens(text: str, model: str = "gpt-4") -> int:
    """Count tokens using tiktoken"""
    try:
        encoding = tiktoken.encoding_for_model(model)
        return len(encoding.encode(text))
    except Exception:
        # Fallback if model not found
        encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))

def run_benchmark():
    print(f"{'='*80}")
    print(f"{'VL TOKEN EFFICIENCY BENCHMARK':^80}")
    print(f"{'='*80}")
    print(f"{'TEST CASE':<30} | {'VL TOKENS':<10} | {'PY TOKENS':<10} | {'SAVINGS':<10}")
    print(f"{'-'*80}")
    
    test_cases = [
        {
            "name": "Hello World",
            "vl": "print('Hello World')"  # Implicit call (no @)
        },
        {
            "name": "Simple Function",
            "vl": "fn:add|i:int,int|o:int|ret:i0+i1"
        },
        {
            "name": "API Call",
            "vl": "requests.get('users/active')"  # Implicit call
        },
        {
            "name": "Data Pipeline",
            "vl": "data:users|filter:active==true|groupBy:role|agg:count"
        },
        {
            "name": "Complex Logic",
            "vl": "fn:process|i:arr|o:arr|limit=100|for:item,i0|if:item.val>limit?item.val*2:item.val|ret:i0"  # Implicit var
        },
        {
            "name": "Conditional Return",
            "vl": "fn:max|i:int,int|o:int|ret:if:i0>i1?i0:i1"
        },
        {
            "name": "Array Map",
            "vl": "fn:double_all|i:arr|o:arr|ret:data:i0|map:item*2"
        },
        {
            "name": "Variable Assignment",
            "vl": "count=0|name='Alice'|total=count+10"  # Implicit vars (no v:)
        },
        {
            "name": "Loop with Accumulator",
            "vl": "total=0|for:i,0..10|total+=i"  # Range shorthand + compound +=
        },
        {
            "name": "Multi-step Calculation",
            "vl": "x=5|y=10|result=(x+y)/2"  # Implicit vars
        },
        {
            "name": "Boolean Logic",
            "vl": "fn:validate|i:int,int|o:bool|ret:i0>0&&i1<100"
        },
        {
            "name": "Recursion",
            "vl": "fn:fact|i:int|o:int|if:i0<=1?ret:1:ret:i0*@fact(i0-1)"
        },
        {
            "name": "Pipeline from Expression",
            "vl": "fn:fetchActive|i:str|o:arr|result=api:GET,i0|ret:$result|filter:status=='active'"  # Implicit var
        }
    ]
    
    total_vl_tokens = 0
    total_py_tokens = 0
    
    for case in test_cases:
        vl_code = case["vl"]
        
        # Compile to Python
        try:
            compiler = Compiler(vl_code, TargetLanguage.PYTHON)
            py_code = compiler.compile()
        except Exception as e:
            print(f"{case['name']:<30} | {'ERROR':<10} | {'-':<10} | {'-':<10}")
            continue
            
        # Count tokens
        vl_count = count_tokens(vl_code)
        py_count = count_tokens(py_code)
        
        # Calculate savings
        if py_count > 0:
            savings = (1 - (vl_count / py_count)) * 100
        else:
            savings = 0
            
        print(f"{case['name']:<30} | {vl_count:<10} | {py_count:<10} | {savings:>9.1f}%")
        
        total_vl_tokens += vl_count
        total_py_tokens += py_count

    print(f"{'='*80}")
    
    if total_py_tokens > 0:
        avg_savings = (1 - (total_vl_tokens / total_py_tokens)) * 100
        print(f"{'TOTAL':<30} | {total_vl_tokens:<10} | {total_py_tokens:<10} | {avg_savings:>9.1f}%")
    
    print(f"{'='*80}")

if __name__ == "__main__":
    run_benchmark()
