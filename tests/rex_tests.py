import unittest
from rex.lexer import Rex
from rex.symbols import *


class RexParsingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.rex = Rex()

    def test_numberOperators(self):
        code = '''\
               x = 10 + 5 - 5 * 2 / 2 % 10
               x += 1
               x -= 1
               x *= 1
               x /= 1
               x %= 1\
               '''

        self.rex.setup(code)

        parsed_tokens = list()
        while self.rex.next_token():
            parsed_tokens.append(self.rex.lexem.token)
        parsed_tokens.append(self.rex.lexem.token)

        excepted_tokens = [
            Special.ID,
            Operators.EQUALS,
            Special.INTEGER,
            Operators.PLUS,
            Special.INTEGER,
            Operators.MINUS,
            Special.INTEGER,
            Operators.ASTERISK,
            Special.INTEGER,
            Operators.SLASH,
            Special.INTEGER,
            Operators.MOD,
            Special.INTEGER,
            Special.NEWLINE,

            Special.ID,
            Operators.PLUS_EQUALS,
            Special.INTEGER,
            Special.NEWLINE,

            Special.ID,
            Operators.MINUS_EQUALS,
            Special.INTEGER,
            Special.NEWLINE,

            Special.ID,
            Operators.ASTERISK_EQUALS,
            Special.INTEGER,
            Special.NEWLINE,

            Special.ID,
            Operators.SLASH_EQUALS,
            Special.INTEGER,
            Special.NEWLINE,

            Special.ID,
            Operators.MOD_EQUALS,
            Special.INTEGER,

            Special.EOF
        ]

        self.assertListEqual(parsed_tokens, excepted_tokens)

    def test_numberTokens(self):
        code = '''\
               0
               1
               10
               100
               0.1
               0.01e4
               -100\
               '''

        self.rex.setup(code)

        parsed_tokens = list()
        while self.rex.next_token():
            if self.rex.lexem.value is None:
                parsed_tokens.append(self.rex.lexem.token)
            else:
                parsed_tokens.append((self.rex.lexem.token, self.rex.lexem.value))
        parsed_tokens.append(self.rex.lexem.token)

        excepted_result = [
            (Special.INTEGER, '0'),
            Special.NEWLINE,
            (Special.INTEGER, '1'),
            Special.NEWLINE,
            (Special.INTEGER, '10'),
            Special.NEWLINE,
            (Special.INTEGER, '100'),
            Special.NEWLINE,
            (Special.FLOAT, '0.1'),
            Special.NEWLINE,
            (Special.FLOAT, '0.01e4'),
            Special.NEWLINE,
            Operators.MINUS,
            (Special.INTEGER, '100'),

            Special.EOF
        ]

        self.assertListEqual(parsed_tokens, excepted_result)

    def test_keywordTokens(self):
        # \ - needed to ignore the NEWLINE token.
        code = '''\
                def\
                return\
                end\
                while\
                do\
                for\
                until\
                next\
                break\
                if\
                elsif\
                else\
                in\
                case\
                when\
                or\
                and\
                not\
                true\
                false\
                nil\
               '''

        self.rex.setup(code)

        parsed_tokens = list()
        while self.rex.next_token():
            parsed_tokens.append(self.rex.lexem.token)
        parsed_tokens.append(self.rex.lexem.token)

        excepted_result = [
            KeyWords.FUNCTION,
            KeyWords.RETURN,
            KeyWords.END,
            KeyWords.WHILE,
            KeyWords.DO,
            KeyWords.FOR,
            KeyWords.UNTIL,
            KeyWords.NEXT,
            KeyWords.BREAK,
            KeyWords.IF,
            KeyWords.ELSIF,
            KeyWords.ELSE,
            KeyWords.IN,
            KeyWords.CASE,
            KeyWords.WHEN,
            KeyWords.OR,
            KeyWords.AND,
            KeyWords.NOT,
            Reserved.TRUE,
            Reserved.FALSE,
            Reserved.NIL,
            Special.EOF
        ]

        self.assertListEqual(parsed_tokens, excepted_result)

    def test_bracketsTokens(self):
        code = '''\
                ( ) [ ] { } |\
               '''

        self.rex.setup(code)

        parsed_tokens = list()
        while self.rex.next_token():
            parsed_tokens.append(self.rex.lexem.token)
        parsed_tokens.append(self.rex.lexem.token)

        excepted_result = [
            Special.LPAR,
            Special.RPAR,
            Special.LBR,
            Special.RBR,
            Special.LFBR,
            Special.RFBR,
            Special.VBR,
            Special.EOF
        ]

        self.assertListEqual(parsed_tokens, excepted_result)

    def test_logicalOperators(self):
        code = '''\
                < > <= >= == != and or not\
               '''

        self.rex.setup(code)

        parsed_tokens = list()
        while self.rex.next_token():
            parsed_tokens.append(self.rex.lexem.token)
        parsed_tokens.append(self.rex.lexem.token)

        excepted_result = [
            Operators.LESS,
            Operators.GREATER,
            Operators.LESS_EQUAL,
            Operators.GREATER_EQUAL,
            Operators.DOUBLE_EQUALS,
            Operators.NOT_EQUALS,
            KeyWords.AND,
            KeyWords.OR,
            KeyWords.NOT,
            Special.EOF
        ]

        self.assertListEqual(parsed_tokens, excepted_result)

    def test_specialTokens(self):
        code = '''\
                , .. ; .\
               '''

        self.rex.setup(code)

        parsed_tokens = list()
        while self.rex.next_token():
            parsed_tokens.append(self.rex.lexem.token)
        parsed_tokens.append(self.rex.lexem.token)

        excepted_result = [
            Special.COMMA,
            Special.DOUBLE_DOT,
            Special.SEMICOLON,
            Special.DOT,
            Special.EOF
        ]

        self.assertListEqual(parsed_tokens, excepted_result)

    def test_ignoreWhitespace(self):
        code = '''\
                \t           \t        
                                \t   
               '''

        self.rex.setup(code)

        parsed_tokens = list()
        while self.rex.next_token():
            parsed_tokens.append(self.rex.lexem.token)
        parsed_tokens.append(self.rex.lexem.token)

        excepted_result = [
            Special.NEWLINE,
            Special.NEWLINE,
            Special.EOF
        ]

        self.assertListEqual(parsed_tokens, excepted_result)

    def test_emptyInput(self):
        code = ''

        self.rex.setup(code)

        parsed_tokens = list()
        while self.rex.next_token():
            parsed_tokens.append(self.rex.lexem.token)
        parsed_tokens.append(self.rex.lexem.token)

        excepted_result = [Special.EOF]

        self.assertListEqual(parsed_tokens, excepted_result)

    def test_severalRunsOnTheSame(self):
        code = '''\
                puts "Hello world!"
                a = 10
                b = 10.1
                c = a + b
                if c == 20.1
                    puts 'Hi!'
                else
                    puts 'Bye!'
                end\
                '''

        def rex_run() -> list:
            self.rex.setup(code)

            parsed_tokens = list()
            while self.rex.next_token():
                parsed_tokens.append(self.rex.lexem)
            parsed_tokens.append(self.rex.lexem)

            return parsed_tokens

        results = list()
        for i in range(5):
            results.append(rex_run())

        res = True
        first_result = results[0]
        for result in results:
            res = res and first_result == result
        self.assertEqual(res, True)

    def test_complexCode(self):
        code = '''\
                hello = "Hello, world!"
                # Define a method
                def self.say_hello
                    puts hello
                end

                x = 5
                if x > 10
                  puts "x is greater than 10"
                elsif x > 5
                  puts "x is greater than 5 but less than or equal to 10"
                else
                  puts "x is less than or equal to 5"
                end
                
                my_array = [1, 2, 3, 4, 5]
                puts my_array.sum
               '''

        self.rex.setup(code)

        parsed_tokens = list()
        while self.rex.next_token():
            parsed_tokens.append(str(self.rex.lexem))
        parsed_tokens.append(str(self.rex.lexem))

        excepted_result = [
            'ID:hello:1:17', 'EQUALS:1:23', 'STR:Hello, world!:1:25', 'NEWLINE:1:40', 'NEWLINE:2:34', 'FUNCTION:3:17',
            'ID:self:3:21', 'DOT:3:25', 'ID:say_hello:3:26', 'NEWLINE:3:35', 'ID:puts:4:21', 'ID:hello:4:26',
            'NEWLINE:4:31', 'END:5:17', 'NEWLINE:5:20', 'NEWLINE:6:1', 'ID:x:7:17', 'EQUALS:7:19', 'INTEGER:5:7:21',
            'NEWLINE:7:22', 'IF:8:17', 'ID:x:8:20', 'GREATER:8:22', 'INTEGER:10:8:24', 'NEWLINE:8:26', 'ID:puts:9:19',
            'STR:x is greater than 10:9:24', 'NEWLINE:9:46', 'ELSIF:10:17', 'ID:x:10:23', 'GREATER:10:25',
            'INTEGER:5:10:27', 'NEWLINE:10:28', 'ID:puts:11:19',
            'STR:x is greater than 5 but less than or equal to 10:11:24', 'NEWLINE:11:74', 'ELSE:12:17',
            'NEWLINE:12:21', 'ID:puts:13:19', 'STR:x is less than or equal to 5:13:24', 'NEWLINE:13:54', 'END:14:17',
            'NEWLINE:14:20', 'NEWLINE:15:17', 'ID:my_array:16:17', 'EQUALS:16:26', 'LBR:16:28', 'INTEGER:1:16:29',
            'COMMA:16:30', 'INTEGER:2:16:32', 'COMMA:16:33', 'INTEGER:3:16:35', 'COMMA:16:36', 'INTEGER:4:16:38',
            'COMMA:16:39', 'INTEGER:5:16:41', 'RBR:16:42', 'NEWLINE:16:43', 'ID:puts:17:17', 'ID:my_array:17:22',
            'DOT:17:30', 'ID:sum:17:31', 'NEWLINE:17:34', 'EOF:18:16'
        ]

        self.assertListEqual(parsed_tokens, excepted_result)

    def test_tokensPositioning(self):
        code = '''\
               my_array = [1, 2, 3, 4, 5]
               puts my_array.sum\
               '''

        self.rex.setup(code)

        parsed_tokens = list()
        while self.rex.next_token():
            parsed_tokens.append(self.rex.lexem.pos)
        parsed_tokens.append(self.rex.lexem.pos)

        excepted_result = [
            (1, 16), (1, 25), (1, 27),
            (1, 28), (1, 29), (1, 31),
            (1, 32), (1, 34), (1, 35),
            (1, 37), (1, 38), (1, 40),
            (1, 41), (1, 42), (2, 16),
            (2, 21), (2, 29), (2, 30),
            (2, 48)
        ]

        self.assertListEqual(parsed_tokens, excepted_result)
