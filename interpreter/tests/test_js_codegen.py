
import unittest
import sys
import os

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lexer import tokenize
from parser import Parser
from codegen_js import JSCodeGenerator

class TestJSCodeGenerator(unittest.TestCase):
    def compile(self, code):
        tokens = tokenize(code)
        parser = Parser(tokens)
        ast = parser.parse()
        generator = JSCodeGenerator(ast)
        return generator.generate()

    def test_variable_def(self):
        code = "v:x:int=42"
        js = self.compile(code)
        self.assertIn("let x = 42;", js)

    def test_function_def(self):
        code = "fn:add|i:int,int|o:int|ret:op:+(i0,i1)"
        js = self.compile(code)
        self.assertIn("function add(i0, i1) {", js)
        self.assertIn("return (i0 + i1);", js)

    def test_direct_call(self):
        code = "@print('Hello')"
        js = self.compile(code)
        self.assertIn("print('Hello');", js)

    def test_if_stmt(self):
        code = "if:true?@print('yes'):@print('no')"
        js = self.compile(code)
        self.assertIn("if (true) {", js)
        self.assertIn("print('yes');", js)
        self.assertIn("} else {", js)
        self.assertIn("print('no');", js)

if __name__ == '__main__':
    unittest.main()
