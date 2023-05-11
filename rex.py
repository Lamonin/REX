import re
from enum import Enum, auto


class KeyWords(Enum):
    # Functions
    FUNCTION = auto()
    RETURN = auto()
    END = auto()
    # Cycles
    WHILE = auto()
    DO = auto()
    FOR = auto()
    UNTIL = auto()
    NEXT = auto()
    BREAK = auto()
    # Conditions
    IF = auto()
    ELIF = auto()
    ELSE = auto()
    IN = auto()
    CASE = auto()
    WHEN = auto()
    # Logical
    OR = auto()
    AND = auto()
    NOT = auto()


class Special(Enum):
    ID = auto()
    NUM = auto()
    INTEGER = auto()
    FLOAT = auto()
    STR = auto()
    EOF = auto()
    CONST = auto()
    NEWLINE = auto()
    DOT = auto()
    DOUBLE_DOT = auto()
    COMMA = auto()
    SEMICOLON = auto()
    LPAR = auto()
    RPAR = auto()
    LBR = auto()  # Left Square Bracket
    RBR = auto()  # Right Square Bracket
    LFBR = auto()  # Right Figure Bracket
    RFBR = auto()  # Right Figure Bracket
    VBR = auto()  # Vertical Bracket


class Reserved(Enum):
    TRUE = auto()
    FALSE = auto()
    NIL = auto()


class Operators(Enum):
    EQUALS = auto()
    NOT_EQUALS = auto()
    LESS = auto()
    GREATER = auto()
    LESS_EQUAL = auto()
    GREATER_EQUAL = auto()
    PLUS = auto()
    MINUS = auto()
    ASTERISK = auto()
    SLASH = auto()
    MOD = auto()
    DOUBLE_EQUALS = auto()
    PLUS_EQUALS = auto()
    MINUS_EQUALS = auto()
    ASTERISK_EQUALS = auto()
    SLASH_EQUALS = auto()
    MOD_EQUALS = auto()


ops: dict[str, Operators | Special] = {
    '=': Operators.EQUALS,
    '<': Operators.LESS,
    '>': Operators.GREATER,
    '<=': Operators.LESS_EQUAL,
    '>=': Operators.GREATER_EQUAL,
    '+': Operators.PLUS,
    '-': Operators.MINUS,
    '*': Operators.ASTERISK,
    '/': Operators.SLASH,
    '%': Operators.MOD,
    '==': Operators.DOUBLE_EQUALS,
    '!=': Operators.NOT_EQUALS,
    '+=': Operators.PLUS_EQUALS,
    '-=': Operators.MINUS_EQUALS,
    '*=': Operators.ASTERISK_EQUALS,
    '/=': Operators.SLASH_EQUALS,
    '%=': Operators.MOD_EQUALS,
    '..': Special.DOUBLE_DOT,
    ',': Special.COMMA,
    ';': Special.SEMICOLON
}

brackets: dict[str, Special] = {
    '(': Special.LPAR,
    ')': Special.RPAR,
    '[': Special.LBR,
    ']': Special.RBR,
    '{': Special.LFBR,
    '}': Special.RFBR,
    '|': Special.VBR
}

keywords: dict[str, KeyWords] = {
    'def': KeyWords.FUNCTION,
    'return': KeyWords.RETURN,
    'end': KeyWords.END,
    'while': KeyWords.WHILE,
    'do': KeyWords.DO,
    'for': KeyWords.FOR,
    'until': KeyWords.UNTIL,
    'next': KeyWords.NEXT,
    'break': KeyWords.BREAK,
    'if': KeyWords.IF,
    'elif': KeyWords.ELIF,
    'else': KeyWords.ELSE,
    'in': KeyWords.IN,
    'case': KeyWords.CASE,
    'when': KeyWords.WHEN,
    'or': KeyWords.OR,
    'and': KeyWords.AND,
    'not': KeyWords.NOT,
    'true': Reserved.TRUE,
    'false': Reserved.FALSE,
    'nil': Reserved.NIL
}

num_pattern = re.compile(r'[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?$')
id_pattern = re.compile(r'^[a-zA-Z_]\w*\??$')


class Lexem:
    def __init__(self, token: Enum, value: str = None, pos: tuple[int, int] = None):
        self.token = token
        self.value = value
        self.pos = pos if pos is not None else (-1, -1)

    def __str__(self):
        return f"{self.token.name}" + (
            f":{self.value}" if self.value is not None else "") + f":{self.pos[0]}:{self.pos[1]}"


class Rex:
    def __init__(self, code: str):
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
            start_pos = self.pos
            start_char_pos = self.char_pos
            op = char()

            self.pos += 1
            if self.pos < code_len and char() in ops:
                op += char()
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
        elif char() == '#':
            while self.pos < code_len and char() != '\n':
                self.pos += 1
            if self.pos < code_len and char() == '\n':
                self.pos -= 1
            return self.next_token()
        # STRINGS
        elif char() == '"' or char() == "'":
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

            block: str = self.code[start_pos:self.pos]
            matches = num_pattern.findall(block)

            self.pos -= 1

            if matches is not None and len(matches) == 1:
                self.lexem = Lexem(token_type, block, pos=(self.line, start_char_pos))
            else:
                raise Exception(f'Incorrect number token:{self.code[start_pos:self.pos]}')

        # KEYWORD OR IDENTIFIER
        elif char().isalpha() or char() == ['_']:
            start_pos = self.pos
            start_char_pos = self.char_pos

            while self.pos < code_len and (char().isalnum() or char() in ['_', '?']):
                self.pos += 1

            block: str = self.code[start_pos:self.pos]

            matches = id_pattern.findall(block)
            if matches is None or len(matches) != 1:
                raise Exception(f'Incorrect id token:{self.code[start_pos:self.pos]}')

            if block in keywords:
                self.lexem = Lexem(keywords[block], pos=(self.line, start_char_pos))
            else:
                self.lexem = Lexem(Special.ID, block, pos=(self.line, start_char_pos))
            self.pos -= 1
        else:
            raise Exception('Incorrect token: ' + char())

        return True
