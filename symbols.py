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
    ELSIF = auto()
    ELSE = auto()
    THEN = auto()
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
    DEGREE = auto()
    DOUBLE_EQUALS = auto()
    PLUS_EQUALS = auto()
    MINUS_EQUALS = auto()
    ASTERISK_EQUALS = auto()
    SLASH_EQUALS = auto()
    MOD_EQUALS = auto()
    DEGREE_EQUALS = auto()


ops: dict[str, Operators | Special] = {
    '=': Operators.EQUALS,
    '<': Operators.LESS,
    '>': Operators.GREATER,
    '<=': Operators.LESS_EQUAL,
    '>=': Operators.GREATER_EQUAL,
    '==': Operators.DOUBLE_EQUALS,
    '!=': Operators.NOT_EQUALS,
    '+': Operators.PLUS,
    '-': Operators.MINUS,
    '*': Operators.ASTERISK,
    '/': Operators.SLASH,
    '%': Operators.MOD,
    '**': Operators.DEGREE,
    '+=': Operators.PLUS_EQUALS,
    '-=': Operators.MINUS_EQUALS,
    '*=': Operators.ASTERISK_EQUALS,
    '/=': Operators.SLASH_EQUALS,
    '%=': Operators.MOD_EQUALS,
    '**=': Operators.DEGREE_EQUALS,
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
    'elsif': KeyWords.ELSIF,
    'else': KeyWords.ELSE,
    'then': KeyWords.THEN,
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
