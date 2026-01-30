import sys
sys.path.insert(0, 'src')

from vl.lexer import tokenize
from vl.parser import Parser

code = "x=[]|x[0]=5"
tokens = tokenize(code)

print("Tokens:")
for i, t in enumerate(tokens):
    print(f"  {i}: {t.type.name:15} '{t.value}'")

parser = Parser(tokens)
try:
    ast = parser.parse()
    print("\nSuccess!")
    print(ast)
except Exception as e:
    print(f"\nError: {e}")
    import traceback
    traceback.print_exc()
