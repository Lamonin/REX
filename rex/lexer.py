import re

from rex.symbols import *


class LexicalError(Exception):
    pass


class Transliterator:
    def __init__(self):
        self.num_pattern = re.compile(
            r"^(?!0\d)-?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?$"
        )
        self.id_pattern = re.compile(r"^[a-zA-Z_]\w*\??$")

    def is_num(self, n: str) -> bool:
        matches = self.num_pattern.findall(n)
        return matches is not None and len(matches) == 1

    def is_id(self, s: str) -> bool:
        matches = self.id_pattern.findall(s)
        return matches is not None and len(matches) == 1

    def is_quote(self, c):
        return c == '"' or c == "'"


class Token:
    def __init__(self, token: Enum, value: str = None, pos: tuple[int, int] = None):
        self.symbol = token
        self.value = value
        self.pos = pos if pos is not None else (-1, -1)

    def __str__(self):
        return (
                f"{self.symbol.name}"
                + (f":{self.value}" if self.value is not None else "")
                + f":{self.pos[0]}:{self.pos[1]}"
        )

    def __eq__(self, other: "Token"):
        return (
                self.symbol == other.symbol
                and self.value == other.value
                and self.pos == other.pos
        )


class Lexer:
    def __init__(self):
        self.code: str = str()
        self.char_pos: int = 0
        self.position: int = -1
        self.line: int = 1
        self.token: Token | None = None
        self.trnslt = Transliterator()

    def setup(self, code: str):
        self.code: str = code
        self.char_pos: int = 0
        self.position: int = -1
        self.line: int = 1
        self.token: Token | None = None

    @property
    def pos(self):
        return self.position

    @pos.setter
    def pos(self, value):
        self.char_pos += value - self.position
        self.position = value

    def error(self, message: str):
        raise LexicalError(f"({self.line - 1}, {self.char_pos}) : {message}")

    def next_token(self) -> bool:
        code_len = len(self.code)

        def char() -> str:
            return self.code[self.pos]

        def is_eof() -> bool:
            return self.pos >= code_len

        def next_char():
            self.pos += 1

        def prev_char():
            self.pos -= 1

        def try_next_char() -> bool:
            if is_eof():
                return False
            next_char()
            if is_eof():
                return False
            return True

        # SKIP WHITESPACE AND HANDLE NEWLINES
        next_char()
        while not is_eof() and char().isspace():
            if char() == "\n":
                self.token = Token(Special.NEWLINE, pos=(self.line, self.char_pos))
                self.line += 1
                self.char_pos = 0
                return True
            next_char()

        # END OF FILE
        if is_eof():
            self.token = Token(Special.EOF, pos=(self.line, self.char_pos))
            return False

        # OPERATORS
        if char() in ops:
            start_char_pos = self.char_pos
            op = char()

            while op in ops and try_next_char():
                op += char()

            if op not in ops:
                op = op[:-1]
                prev_char()

            self.token = Token(ops[op], pos=(self.line, start_char_pos))
        # BRACKETS
        elif char() in brackets:
            self.token = Token(brackets[char()], pos=(self.line, self.char_pos))
        # COMMENTARY
        elif char() == "#":
            start_char_pos = self.char_pos
            start_pos = self.pos + 1
            while not is_eof() and char() != "\n":
                next_char()
            comment_text = self.code[start_pos:self.pos]
            self.token = Token(Special.COMMENT, comment_text, pos=(self.line, start_char_pos))
            self.line += 1
            self.char_pos = 0
            prev_char()
        # STRINGS
        elif self.trnslt.is_quote(char()):
            quote = char()
            start_pos = self.pos + 1
            start_char_pos = self.char_pos
            next_char()
            while not is_eof() and char() != quote:
                next_char()
            if not is_eof() and char() == quote:
                self.token = Token(
                    Special.STR,
                    self.code[start_pos: self.pos],
                    pos=(self.line, start_char_pos),
                )
            else:
                if code_len - self.pos < 10:
                    example = self.code[start_pos:-1]
                else:
                    example = self.code[start_pos: start_pos + 9]
                self.error(f"Incorrect string literal: {example}...")
        # NUMBERS
        elif char().isdigit():
            start_pos = self.pos
            start_char_pos = self.char_pos

            token_type = Special.INTEGER
            while not is_eof() and char().isdigit():
                next_char()

            if not is_eof() and char() == ".":
                next_char()
                if char() == ".":
                    self.pos -= 2
                    self.token = Token(
                        Special.INTEGER,
                        self.code[start_pos: self.pos + 1],
                        pos=(self.line, start_char_pos),
                    )
                    return True
                if not is_eof() and char().isdigit():
                    token_type = Special.FLOAT
                    while not is_eof() and char().isdigit():
                        next_char()
                else:
                    prev_char()

            if not is_eof() and char() in ["e", "E"]:
                next_char()
                if not is_eof() and char() in ["-", "+"]:
                    next_char()
                while not is_eof() and char().isdigit():
                    next_char()

            if (
                    not is_eof()
                    and not char().isspace()
                    and char() not in ops
                    and char() not in [")", "]", "<", ">"]
            ):
                self.error(
                    f"Incorrect number token: {self.code[start_pos:self.pos + 1]}"
                )

            potential_num: str = self.code[start_pos: self.pos]
            prev_char()

            if self.trnslt.is_num(potential_num):
                self.token = Token(
                    token_type, potential_num, pos=(self.line, start_char_pos)
                )
            else:
                self.error(f"Incorrect number token: {self.code[start_pos:self.pos + 1]}")

        # KEYWORD OR IDENTIFIER
        elif char().isalpha() or char() == ["_"]:
            start_pos = self.pos
            start_char_pos = self.char_pos

            while not is_eof() and (char().isalnum() or char() in ["_", "?"]):
                next_char()

            potential_id = self.code[start_pos: self.pos]

            if not self.trnslt.is_id(potential_id):
                self.error(f"Incorrect id token: {self.code[start_pos:self.pos]}")

            if potential_id in keywords:
                self.token = Token(
                    keywords[potential_id], pos=(self.line, start_char_pos)
                )
            else:
                self.token = Token(
                    Special.ID, potential_id, pos=(self.line, start_char_pos)
                )
            prev_char()
        else:
            self.error("Incorrect symbol: " + char())

        return True
