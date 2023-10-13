from rex.lexer import Rex
from rex.parser import Parser


def read_code(path: str) -> str:
    f = open(path)
    code: str = f.read()
    f.close()
    return code


def test_sample_lexer(path: str):
    print(f"{'LEXER TEST':=^20}")
    code = read_code(path)

    rex = Rex()
    rex.setup(code)

    while rex.next_token():
        print(rex.lexem)
    print(rex.lexem)


def test_sample_parser(path: str):
    print(f"{'PARSER TEST':=^20}")
    code = read_code(path)

    rex = Rex()
    rex.setup(code)

    p: Parser = Parser(rex)
    print(p.parse())


def test_sample_translator(path: str):
    print(f"{'TRANSLATOR TEST':=^20}")
    code = read_code(path)

    rex = Rex()
    rex.setup(code)

    p: Parser = Parser(rex)
    print(p.parse().generate())


test_sample_lexer('samples/sample_2.rb')
test_sample_parser('samples/sample_2.rb')
test_sample_translator('samples/sample_2.rb')
