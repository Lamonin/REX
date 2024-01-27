import unittest
from rex.lexer import Lexer
from rex.parser import Parser
from rex.symbols import *
from rex.symtable import SemanticError


def read_code(path: str) -> str:
    f = open(path)
    code: str = f.read()
    f.close()
    return code


class RexLexerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.rex = Lexer()

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
            parsed_tokens.append(self.rex.token.symbol)
        parsed_tokens.append(self.rex.token.symbol)

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
            if self.rex.token.value is None:
                parsed_tokens.append(self.rex.token.symbol)
            else:
                parsed_tokens.append((self.rex.token.symbol, self.rex.token.value))
        parsed_tokens.append(self.rex.token.symbol)

        expected_result = [
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

        self.assertListEqual(parsed_tokens, expected_result)

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
            parsed_tokens.append(self.rex.token.symbol)
        parsed_tokens.append(self.rex.token.symbol)

        expected_result = [
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

        self.assertListEqual(parsed_tokens, expected_result)

    def test_bracketsTokens(self):
        code = '''\
                ( ) [ ] { } |\
               '''

        self.rex.setup(code)

        parsed_tokens = list()
        while self.rex.next_token():
            parsed_tokens.append(self.rex.token.symbol)
        parsed_tokens.append(self.rex.token.symbol)

        expected_result = [
            Special.LPAR,
            Special.RPAR,
            Special.LBR,
            Special.RBR,
            Special.LFBR,
            Special.RFBR,
            Special.VBR,
            Special.EOF
        ]

        self.assertListEqual(parsed_tokens, expected_result)

    def test_logicalOperators(self):
        code = '''\
                < > <= >= == != and or not\
               '''

        self.rex.setup(code)

        parsed_tokens = list()
        while self.rex.next_token():
            parsed_tokens.append(self.rex.token.symbol)
        parsed_tokens.append(self.rex.token.symbol)

        expected_result = [
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

        self.assertListEqual(parsed_tokens, expected_result)

    def test_specialTokens(self):
        code = '''\
                , .. ; .\
               '''

        self.rex.setup(code)

        parsed_tokens = list()
        while self.rex.next_token():
            parsed_tokens.append(self.rex.token.symbol)
        parsed_tokens.append(self.rex.token.symbol)

        expected_result = [
            Special.COMMA,
            Special.DOUBLE_DOT,
            Special.SEMICOLON,
            Special.DOT,
            Special.EOF
        ]

        self.assertListEqual(parsed_tokens, expected_result)

    def test_ignoreWhitespace(self):
        code = '''\
                \t           \t        
                                \t   
               '''

        self.rex.setup(code)

        parsed_tokens = list()
        while self.rex.next_token():
            parsed_tokens.append(self.rex.token.symbol)
        parsed_tokens.append(self.rex.token.symbol)

        expected_result = [
            Special.NEWLINE,
            Special.NEWLINE,
            Special.EOF
        ]

        self.assertListEqual(parsed_tokens, expected_result)

    def test_emptyInput(self):
        code = ''

        self.rex.setup(code)

        parsed_tokens = list()
        while self.rex.next_token():
            parsed_tokens.append(self.rex.token.symbol)
        parsed_tokens.append(self.rex.token.symbol)

        expected_result = [Special.EOF]

        self.assertListEqual(parsed_tokens, expected_result)

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
                parsed_tokens.append(self.rex.token)
            parsed_tokens.append(self.rex.token)

            return parsed_tokens

        results = list()
        for i in range(5):
            results.append(rex_run())

        res = True
        first_result = results[0]
        for result in results:
            res = res and first_result == result
        self.assertEqual(res, True)

    def test_tokensPositioning(self):
        code = '''\
               my_array = [1, 2, 3, 4, 5]
               puts my_array.sum\
               '''

        self.rex.setup(code)

        parsed_tokens = list()
        while self.rex.next_token():
            parsed_tokens.append(self.rex.token.pos)
        parsed_tokens.append(self.rex.token.pos)

        expected_result = [
            (1, 16), (1, 25), (1, 27),
            (1, 28), (1, 29), (1, 31),
            (1, 32), (1, 34), (1, 35),
            (1, 37), (1, 38), (1, 40),
            (1, 41), (1, 42), (2, 16),
            (2, 21), (2, 29), (2, 30),
            (2, 48)
        ]

        self.assertListEqual(parsed_tokens, expected_result)


class RexParserTests(unittest.TestCase):
    def setUp(self) -> None:
        self.parser = Parser()

    def test_canParseAllRubyCode(self):
        code = read_code('codes/code_1.rb')
        self.parser.setup(code)
        parse_result = self.parser.parse()
        print(parse_result)

    def test_functions(self):
        code = read_code('codes/functions.rb')
        self.parser.setup(code)
        parse_result = self.parser.parse()
        print(parse_result)

    def test_ifstatement(self):
        code = read_code('codes/if.rb')
        self.parser.setup(code)
        parse_result = self.parser.parse()
        print(parse_result)

    def test_cycles(self):
        code = read_code('codes/cycles.rb')
        self.parser.setup(code)
        parse_result = self.parser.parse()
        print(parse_result)
        print(parse_result.generate())

    def test_variables(self):
        code = read_code('codes/variables.rb')
        self.parser.setup(code)
        parse_result = self.parser.parse()
        print(parse_result)


class RexSemanticTests(unittest.TestCase):
    def setUp(self) -> None:
        self.parser = Parser()

    def test_valid_code(self):
        code = '''
               a = 10
               b = 2 * a + 10
               
               def sum(a, b)
                    def bar(a)
                        return 10 + a
                    end
                   return a + b + bar(a)
               end
               
               c = sum(1, 10) + sum(a, b)
               puts(c)
           '''

        self.parser.setup(code)

        try:
            self.parser.parse()
        except SemanticError:
            self.assertTrue(False)

        self.assertTrue(True)

    def test_using_an_undeclared_variable(self):
        code = '''
            c = a
        '''

        self.parser.setup(code)

        try:
            self.parser.parse()
        except Exception as e:
            self.assertEqual(type(e), SemanticError)
            return

        self.assertTrue(False)

    def test_calling_an_undeclared_function(self):
        code = '''
            c = foo()
        '''

        self.parser.setup(code)

        try:
            self.parser.parse()
        except Exception as e:
            self.assertEqual(type(e), SemanticError)
            return

        self.assertTrue(False)

    def test_calling_a_function_with_the_wrong_number_of_parameters(self):
        code = '''
            def sum(a, b)
                return a + b
            end
            c = sum(1)
        '''

        self.parser.setup(code)

        try:
            self.parser.parse()
        except Exception as e:
            self.assertEqual(type(e), SemanticError)
            return

        self.assertTrue(False)

    def test_use_of_a_variable_outside_its_scope(self):
        code = '''
            if true then
                a = 10
            end
            puts(a)
        '''

        self.parser.setup(code)

        try:
            self.parser.parse()
        except Exception as e:
            self.assertEqual(type(e), SemanticError)
            return

        self.assertTrue(False)

    def test_using_a_function_outside_its_scope(self):
        code = '''
            if true then
                def foo()
                    puts("Foo")
                end
                puts(foo())
            end
            puts(foo())
        '''

        self.parser.setup(code)

        try:
            self.parser.parse()
        except Exception as e:
            self.assertEqual(type(e), SemanticError)
            return

        self.assertTrue(False)


class RexGeneratorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.parser = Parser()

    def test_correct_translation_of_all_ruby_code(self):
        code = '''
            # Переменные
            name = "John"
            age = 30
            
            # Условие
            if age >= 18
              puts(name + " is an adult")
            else
             puts(name + " is underage")
            end
            
            # Цикл while
            i = 0
            while i < 5
              puts(i)
              i += 1
            end
            
            # Цикл until
            j = 5 
            until j == 0
              puts(j)
              j -= 1
            end
            
            # Цикл for
            for k in 0..5
              puts(k)
            end
            
            # Функция
            def print_name(n)
              puts("Hello, #{n}!")
            end
            
            print_name(name)
            
            # Ввод данных
            input_name = readline("Enter your name: ")
            puts("Hi #{input_name}!")
        '''

        translated_r_code = read_code('codes/translated_r_code_1.rb')

        self.parser.setup(code)
        parse_res = self.parser.parse()
        print(parse_res)
        gen_res = parse_res.generate()
        print(gen_res)
        self.assertEqual(gen_res, translated_r_code)

    def test_optimization_solving_simple_math(self):
        code = '''
            a = (10 + 2 * (9-5) ** 2) / 2
            b = 11 ** 2 - 12 ** 2
            c = a + b
            puts(c)
        '''

        translated_r_code = (
            "a <- 21\n"
            "b <- -23\n"
            "c <- a + b\n"
            "print(c)\n"
        )

        self.parser.setup(code)
        parse_res = self.parser.parse()
        gen_res = parse_res.generate()
        self.assertEqual(gen_res, translated_r_code)

    def test_optimization_parenthesis_removal(self):
        code = '''
            a = (((((((((((10 + 20)))))))))))
            b = (((((a)) + (10))) * 20)
            puts(a + b)
        '''

        translated_r_code = (
            "a <- 30\n"
            "b <- (a + 10) * 20\n"
            "print(a + b)\n"
        )

        self.parser.setup(code)
        parse_res = self.parser.parse()
        gen_res = parse_res.generate()
        self.assertEqual(gen_res, translated_r_code)

    def test_optimization_extra_unary_operator(self):
        code = '''
            a = --10
            b = ---1
            c = +++1
            puts(a + b + c)
            if not not not true then
                puts(a + b)
            end
        '''

        translated_r_code = (
            "a <- 10\n"
            "b <- -1\n"
            "c <- +1\n"
            "print(a + b + c)\n"
            "if (!TRUE) {\n"
            "\tprint(a + b)\n"
            "}\n"
        )

        self.parser.setup(code)
        parse_res = self.parser.parse()
        gen_res = parse_res.generate()
        self.assertEqual(gen_res, translated_r_code)

    def test_optimization_unused_variables_and_functions(self):
        code = '''
            a = 10
            b = 20
            def foo()
              return a
            end
            c = a + b
            puts(a)
        '''

        translated_r_code = (
            "a <- 10\n"
            "print(a)\n"
        )

        self.parser.setup(code)
        parse_res = self.parser.parse()
        gen_res = parse_res.generate()
        self.assertEqual(gen_res, translated_r_code)

    def test_optimization_return_statement(self):
        code = '''
            def foo()
                puts("Foo called")
                return
                puts("Foo try called")
            end
            foo()
            return false
            a = 10
            b = 20
            puts(a + b)
        '''

        translated_r_code = (
            "foo <- function() {\n"
            '\tprint("Foo called")\n'
            "\treturn\n"
            "}\n"
            "foo()\n"
            "return\n"
        )

        self.parser.setup(code)
        parse_res = self.parser.parse()
        gen_res = parse_res.generate()
        self.assertEqual(gen_res, translated_r_code)
