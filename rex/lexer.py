import re

from rex.symbols import *


class Transliterator:
    def __init__(self):
        self.num_pattern = re.compile(r'^(?!0\d)-?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?$')
        self.id_pattern = re.compile(r'^[a-zA-Z_]\w*\??$')

    def is_num(self, n: str) -> bool:
        matches = self.num_pattern.findall(n)
        return matches is not None and len(matches) == 1

    def is_id(self, s: str) -> bool:
        matches = self.id_pattern.findall(s)
        return matches is not None and len(matches) == 1

    def is_quote(self, c):
        return c == '"' or c == "'"


class Lexem:
    def __init__(self, token: Enum, value: str = None, pos: tuple[int, int] = None):
        self.token = token
        self.value = value
        self.pos = pos if pos is not None else (-1, -1)

    def __str__(self):
        return f"{self.token.name}" + (
            f":{self.value}" if self.value is not None else "") + f":{self.pos[0]}:{self.pos[1]}"

    def __eq__(self, other: 'Lexem'):
        return self.token == other.token \
            and self.value == other.value \
            and self.pos == other.pos


class Rex:
    def __init__(self):
        self.code: str = str()
        self.char_pos: int = 0
        self.position: int = -1
        self.line: int = 1
        self.lexem: Lexem | None = None
        self.trnslt = Transliterator()

    def setup(self, code: str):
        self.code: str = code
        self.char_pos: int = 0
        self.position: int = -1
        self.line: int = 1
        self.lexem: Lexem | None = None

    @property
    def pos(self):
        return self.position

    @pos.setter
    def pos(self, value):
        self.char_pos += value - self.position
        self.position = value

    def next_token(self) -> bool:
        def char() -> str:
            return self.code[self.pos]

        code_len = len(self.code)

        # SKIP WHITESPACE AND HANDLE NEWLINES
        self.pos += 1
        while self.pos < code_len and char().isspace():
            if char() == '\n':
                self.lexem = Lexem(Special.NEWLINE, pos=(self.line, self.char_pos))
                self.line += 1
                self.char_pos = 0
                return True
            self.pos += 1

        # END OF FILE
        if self.pos >= code_len:
            self.lexem = Lexem(Special.EOF, pos=(self.line, self.char_pos))
            return False

        # OPERATORS
        if char() in ops or char() in ['.', '!']:
            start_char_pos = self.char_pos
            op = char()

            self.pos += 1
            while self.pos < code_len and (char() in ops or char() == '.'):
                op += char()
                self.pos += 1
            else:
                self.pos -= 1

            if op in ops:
                self.lexem = Lexem(ops[op], pos=(self.line, start_char_pos))
            elif op == '.':
                self.lexem = Lexem(Special.DOT, pos=(self.line, start_char_pos))
            else:
                self.pos -= 1
                self.lexem = Lexem(ops[char()], pos=(self.line, start_char_pos))
        # BRACKETS
        elif char() in brackets:
            self.lexem = Lexem(brackets[char()], pos=(self.line, self.char_pos))
        # COMMENTARY
        elif char() == '#':
            while self.pos < code_len and char() != '\n':
                self.pos += 1
            if self.pos < code_len and char() == '\n':
                self.pos -= 1
            return self.next_token()
        # STRINGS
        elif self.trnslt.is_quote(char()):
            quote = char()
            start_pos = self.pos + 1
            start_char_pos = self.char_pos
            self.pos += 1
            while self.pos < code_len and char() != quote:
                self.pos += 1
            if self.pos < code_len and char() == quote:
                self.lexem = Lexem(Special.STR, self.code[start_pos:self.pos], pos=(self.line, start_char_pos))
            else:
                if code_len - self.pos < 10:
                    example = self.code[start_pos:-1]
                else:
                    example = self.code[start_pos:start_pos + 9]
                raise Exception(f'Incorrect string literal: {example}...')
        # NUMBERS
        elif char().isdigit():
            start_pos = self.pos
            start_char_pos = self.char_pos

            token_type = Special.INTEGER
            while self.pos < code_len and char().isdigit():
                self.pos += 1

            if self.pos < code_len and char() == '.':
                self.pos += 1
                if char() == '.':
                    self.pos -= 2
                    self.lexem = Lexem(Special.INTEGER, self.code[start_pos:self.pos + 1],
                                       pos=(self.line, start_char_pos))
                    return True
                if self.pos < code_len and char().isdigit():
                    token_type = Special.FLOAT
                    while self.pos < code_len and char().isdigit():
                        self.pos += 1
                else:
                    self.pos -= 1

            if self.pos < code_len and char() in ['e', 'E']:
                self.pos += 1
                if self.pos < code_len and char() in ['-', '+']:
                    self.pos += 1
                while self.pos < code_len and char().isdigit():
                    self.pos += 1

            if self.pos < code_len and not char().isspace() and char() not in ops and char() not in [')', ']', '<',
                                                                                                     '>']:
                raise Exception(f'Incorrect number token: {self.code[start_pos:self.pos + 1]}')

            potential_num: str = self.code[start_pos:self.pos]
            self.pos -= 1

            if self.trnslt.is_num(potential_num):
                self.lexem = Lexem(token_type, potential_num, pos=(self.line, start_char_pos))
            else:
                raise Exception(f'Incorrect number token: {self.code[start_pos:self.pos + 1]}')

        # KEYWORD OR IDENTIFIER
        elif char().isalpha() or char() == ['_']:
            start_pos = self.pos
            start_char_pos = self.char_pos

            while self.pos < code_len and (char().isalnum() or char() in ['_', '?']):
                self.pos += 1

            potential_id: str = self.code[start_pos:self.pos]

            if not self.trnslt.is_id(potential_id):
                raise Exception(f'Incorrect id token: {self.code[start_pos:self.pos]}')

            if potential_id in keywords:
                self.lexem = Lexem(keywords[potential_id], pos=(self.line, start_char_pos))
            else:
                self.lexem = Lexem(Special.ID, potential_id, pos=(self.line, start_char_pos))
            self.pos -= 1
        else:
            raise Exception('Incorrect token: ' + char())

        return True
