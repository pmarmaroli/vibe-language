from src.vl.lexer import tokenize
from src.vl.parser import Parser

code = """counts[word]+=1"""

tokens = tokenize(code)
print("Tokens:")
for i, tok in enumerate(tokens):
    print(f"  {i}: {tok.type.name:15} {repr(tok.value):10} line={tok.line} col={tok.column}")

parser = Parser(tokens)
print("\nCurrent token:", parser.current_token)
print("Next token:", parser.peek(1))
