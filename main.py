from rex.lexer import Lexer
from rex.nodes import NodeArrayCall, NodeInteger, NodeArgs
from rex.parser import Parser


def read_code(path: str) -> str:
    f = open(path)
    code: str = f.read()
    f.close()
    return code


def test_sample_lexer(path: str):
    print(f"{'LEXER RESULT':=^30}")
    code = read_code(path)

    rex = Lexer()
    rex.setup(code)

    while rex.next_token():
        print(rex.token)
    print(rex.token)


def test_sample_parser(path: str):
    print(f"{'PARSER RESULT':=^30}")
    code = read_code(path)
    p: Parser = Parser()
    p.setup(code)
    print(p.parse())


def test_sample_translator(path: str):
    print(f"{'TRANSLATOR RESULT':=^30}")
    code = read_code(path)
    p: Parser = Parser()
    p.setup(code)
    print(p.parse().generate())


test_sample_lexer('samples/sample_2.rb')
test_sample_parser('samples/sample_2.rb')
test_sample_translator('samples/sample_2.rb')
