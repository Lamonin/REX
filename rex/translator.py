from rex.lexer import Lexer
from rex.parser import Parser


class Translator:
    def __init__(self):
        self.lexer = Lexer()
        self.parser = Parser(self.lexer)

    def get_lexer_result(self, code: str):
        pass

    def parse(self, code: str):
        self.lexer.setup(code)
        return self.parser.parse()

    def translate(self, code: str):
        return self.parse(code).generate()
