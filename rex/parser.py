from rex.lexer import Lexer
from rex.nodes import *
from rex.symbols import *
from rex.symtable import SymTable


class Parser:
    def __init__(self, lexer: Lexer):
        self.lexer: Lexer = lexer
        self.lexer.next_token()
        self.token = self.lexer.token.symbol
        self.symtable = SymTable()
        self.indent = 0

    def next_token(self):
        self.lexer.next_token()
        self.token = self.lexer.token.symbol

    def require(self, *args: Enum):
        for arg in args:
            if self.token == arg:
                return
        if len(args) == 1:
            self.error(f'Ожидается токен {args[0]}, получен токен {self.token}!')
        else:
            self.error(f'Ожидается один из токенов {args}, получен токен {self.token}!')

    def error(self, msg: str):
        raise Exception(f'Ошибка синтаксического анализа ({self.lexer.token.pos[0]}, {self.lexer.token.pos[1]}): {msg}')

    def statement(self) -> Node | None:
        match self.token:
            # <if_stmt> | <cycle_stmt> | <func_def> | "RETURN" <args> | <expression>
            case Special.NEWLINE:
                return None
            case KeyWords.IF:
                self.next_token()
                return self.if_statement()
            case KeyWords.WHILE | KeyWords.UNTIL | KeyWords.FOR:
                return self.cycle_statement()
            case KeyWords.FUNCTION:
                return self.func_statement()
            case KeyWords.RETURN:
                self.next_token()
                return self.return_statement()
            case KeyWords.NEXT:
                self.next_token()
                return NodeNext()
            case KeyWords.BREAK:
                self.next_token()
                return NodeBreak()
            case _:
                return self.expression()

    def block(self, *args: Enum, skiplast=True) -> Node:
        self.symtable.create_local_data_block()
        self.indent += 1
        statements = []
        while self.token not in args:
            statement = self.statement()
            if statement is not None:
                statements.append(statement)
                print(self.lexer.token)
                self.require(Special.NEWLINE, Special.SEMICOLON)
            self.next_token()
        if skiplast:
            self.next_token()
        self.symtable.dispose_local_data_block(self.lexer.token.pos)
        self.indent -= 1
        return NodeBlock(statements, self.indent + 1)

    def if_block(self) -> Node:
        condition = self.expression()
        self.require(KeyWords.THEN, Special.NEWLINE, Special.SEMICOLON)
        self.next_token()
        block = self.block(KeyWords.END, KeyWords.ELSIF, KeyWords.ELSE, skiplast=False)
        return NodeIfStatement(condition, block)

    def elseif_block(self) -> Node:
        self.next_token()
        condition = self.expression()
        self.require(KeyWords.THEN, Special.NEWLINE, Special.SEMICOLON)
        self.next_token()
        block = self.block(KeyWords.END, KeyWords.ELSIF, KeyWords.ELSE, skiplast=False)
        return NodeElsIfStatement(condition, block)

    def else_block(self) -> Node:
        self.next_token()
        block = self.block(KeyWords.END)
        return NodeElseStatement(block, self.indent)

    def if_statement(self) -> Node:
        block = []
        if_block = self.if_block()
        block.append(if_block)
        if self.token == KeyWords.END:
            self.next_token()
            return NodeIfBlock(if_block, self.indent)
        else:
            elsif_block = []
            else_block = None
            if self.token == KeyWords.ELSIF:
                while self.token not in {KeyWords.END, KeyWords.ELSE}:
                    elsif_block.append(self.elseif_block())
                if self.token == KeyWords.ELSE:
                    else_block = self.else_block()
            else:
                else_block = self.else_block()
            return NodeIfBlock(if_block, self.indent, elsif_block, else_block)

    def cycle_statement(self) -> Node:
        match self.token:
            case KeyWords.FOR:
                self.next_token()
                vars_list = self.variable_list()
                self.require(KeyWords.IN)
                self.next_token()
                iterable = self.expression()
                self.require(KeyWords.DO, Special.NEWLINE, Special.SEMICOLON)
                self.next_token()
                block = self.block(KeyWords.END)
                return NodeForBlock(NodeActualParams(vars_list), iterable, block, self.indent)
            case KeyWords.WHILE:
                self.next_token()
                condition = self.expression()
                self.require(Special.NEWLINE, Special.SEMICOLON, KeyWords.DO)
                self.next_token()
                block = self.block(KeyWords.END)
                # self.next_token()
                return NodeWhileBlock(condition, block, self.indent)
            case KeyWords.UNTIL:
                self.next_token()
                condition = self.expression()
                self.require(Special.NEWLINE, Special.SEMICOLON, KeyWords.DO)
                self.next_token()
                block = self.block(KeyWords.END)
                # self.next_token()
                return NodeUntilBlock(condition, block, self.indent)

    def declare_params(self) -> Node:
        params = []
        while self.token not in {Special.RPAR}:
            params.append(self.variable())
            if self.token == Special.COMMA:
                self.next_token()
        return NodeDeclareParams(params)

    def actual_params(self) -> Node:
        params = []
        while self.token not in {Special.RPAR}:
            params.append(self.expression())
            if self.token == Special.COMMA:
                self.next_token()
        return NodeActualParams(params)

    def func_statement(self) -> Node:
        match self.token:
            case Special.ID:
                id = self.lexer.token.value
                self.next_token()
                self.require(Special.LPAR)
                self.next_token()
                params = self.actual_params()
                self.require(Special.RPAR)
                self.next_token()
                if not self.symtable.is_func_exist(id):
                    self.error(f"Попытка вызвать функцию {id}, которая не была объявлена!")
                return NodeFuncCall(id, params)
            case KeyWords.FUNCTION:
                self.next_token()
                id = self.lexer.token.value
                self.next_token()
                self.require(Special.LPAR)
                self.next_token()
                params = self.declare_params()
                self.require(Special.RPAR)
                self.next_token()
                self.require(Special.NEWLINE, Special.SEMICOLON)
                self.next_token()
                block = self.block(KeyWords.END)
                self.symtable.add_func(id, NodeFunc(id, params), self.lexer.token.pos)
                return NodeFuncDec(id, params, block, self.indent)
            case _:
                self.error("Ожидался вызов или объявление функции")

    def expression(self) -> Node:
        match self.token:
            case KeyWords.NOT:
                self.next_token()
                first_expr = NodeNot(self.expression())
            case _:
                first_expr = self.arg()

        if self.token == KeyWords.AND:
            return NodeAnd(first_expr, self.expression())
        elif self.token == KeyWords.OR:
            return NodeOr(first_expr, self.expression())

        return first_expr

    def return_statement(self) -> Node:
        if self.token in [Special.NEWLINE, Special.SEMICOLON]:
            return NodeReturn("")
        return NodeReturn(self.args())

    def parse(self) -> Node:
        if self.token == Special.EOF:
            self.error("Empty file!")
        else:
            statements = []
            while self.token != Special.EOF:
                statement = self.statement()
                if statement is not None:
                    statements.append(statement)
                    if self.token != Special.EOF:
                        self.require(Special.NEWLINE, Special.SEMICOLON)
                self.next_token()
            return NodeProgram(statements)

    def arg(self):
        match self.token:
            case Operators.MINUS:
                self.next_token()
                first_arg = NodeUnaryMinus(self.arg())
            case Operators.PLUS:
                self.next_token()
                first_arg = NodeUnaryPlus(self.arg())
            case Special.LPAR:
                self.next_token()
                first_arg = self.arg()
                self.require(Special.RPAR)
                self.next_token()
            case _:
                first_arg = self.parse_expression()
        if self.token == Special.DOUBLE_DOT:
            self.next_token()
            return NodeDoubleDot(first_arg, self.arg())
        elif self.token in asgn_ops:
            if isinstance(first_arg, NodeVariable) or isinstance(first_arg, NodeArrayCall):
                return self.asgn_op(first_arg)
            self.error("Ожидалась переменная или массив!")

        return first_arg

    def args(self):
        args = [self.arg()]
        while self.token == Special.COMMA:
            self.next_token()
            args.append(self.arg())
        return NodeArgs(args)

    def primary(self) -> Node:
        match self.token:
            # <literal> | <lhs> | <func_call> | "LBR" [args] "RBR"
            case Special.ID:
                return self.rhs()
            case Special.INTEGER | Special.FLOAT | Special.STR | Reserved.TRUE | Reserved.FALSE | Reserved.NIL:
                return self.literal()
            case Special.LBR:  # Array definition
                self.next_token()
                args = self.args()
                self.require(Special.RBR)
                self.next_token()
                return NodeArray(args)
            case Special.LPAR:
                self.next_token()
                expr = self.parse_expression()
                self.require(Special.RPAR)
                self.next_token()
                return NodePar(expr)
            case Operators.MINUS:
                self.next_token()
                return NodeUnaryMinus(self.arg())
            case Operators.PLUS:
                self.next_token()
                return NodeUnaryPlus(self.arg())
            case _:
                self.error(f"Был получен токен {self.token}, а ожидался литерал или функция!")

    def asgn_op(self, lhs):
        match self.token:
            case Operators.EQUALS:
                self.next_token()
                t = self.parse_expression()
                self.symtable.add_var(lhs.id, t)
                return NodeEquals(lhs, t)
            case Operators.ASTERISK_EQUALS:
                self.symtable.is_var_exist(lhs.id, self.lexer.token.pos, True)
                self.next_token()
                return NodeAsteriskEquals(lhs, self.arg())
            case Operators.SLASH_EQUALS:
                self.symtable.is_var_exist(lhs.id, self.lexer.token.pos, True)
                self.next_token()
                return NodeSlashEquals(lhs, self.arg())
            case Operators.MOD_EQUALS:
                self.symtable.is_var_exist(lhs.id, self.lexer.token.pos, True)
                self.next_token()
                return NodeModEquals(lhs, self.arg())
            case Operators.DEGREE_EQUALS:
                self.symtable.is_var_exist(lhs.id, self.lexer.token.pos, True)
                self.next_token()
                return NodeDegreeEquals(lhs, self.arg())
            case Operators.PLUS_EQUALS:
                self.symtable.is_var_exist(lhs.id, self.lexer.token.pos, True)
                self.next_token()
                return NodePlusEquals(lhs, self.arg())
            case Operators.MINUS_EQUALS:
                self.symtable.is_var_exist(lhs.id, self.lexer.token.pos, True)
                self.next_token()
                return NodeMinusEquals(lhs, self.arg())

    def parse_expression(self) -> Node:
        left = self.term()
        op = self.token
        while op in [Operators.PLUS, Operators.MINUS, KeyWords.AND, KeyWords.OR]:
            self.next_token()
            match op:
                case Operators.PLUS:
                    left = NodePlus(left, self.term())
                case Operators.MINUS:
                    left = NodeMinus(left, self.term())
                case KeyWords.AND:
                    left = NodeAnd(left, self.term())
                case KeyWords.OR:
                    left = NodeOr(left, self.term())
            op = self.token
        return left

    def term(self) -> Node:
        left = self.primary()
        op = self.token
        while op in [Operators.ASTERISK, Operators.SLASH, Operators.MOD, Operators.DEGREE,
                     Operators.GREATER, Operators.GREATER_EQUAL, Operators.LESS, Operators.LESS_EQUAL,
                     Operators.DOUBLE_EQUALS, Operators.NOT_EQUALS]:
            self.next_token()
            match op:
                case Operators.ASTERISK:
                    left = NodeAsterisk(left, self.primary())
                case Operators.SLASH:
                    left = NodeSlash(left, self.primary())
                case Operators.MOD:
                    left = NodeMod(left, self.primary())
                case Operators.DEGREE:
                    left = NodeDegree(left, self.primary())
                case Operators.GREATER:
                    left = NodeGreater(left, self.term())
                case Operators.GREATER_EQUAL:
                    left = NodeGreaterEqual(left, self.term())
                case Operators.LESS:
                    left = NodeLess(left, self.term())
                case Operators.LESS_EQUAL:
                    left = NodeLessEqual(left, self.term())
                case Operators.DOUBLE_EQUALS:
                    left = NodeCompEqual(left, self.primary())
                case Operators.NOT_EQUALS:
                    left = NodeNotEqual(left, self.primary())
            op = self.token
        return left

    def bin_op(self, first):
        node: Node | None = None
        match self.token:
            case Operators.ASTERISK:
                node = NodeAsterisk(first, self.arg())
            case Operators.SLASH:
                node = NodeSlash(first, self.arg())
            case Operators.MOD:
                node = NodeMod(first, self.arg())
            case Operators.DEGREE:
                node = NodeDegree(first, self.arg())
            case Operators.PLUS:
                node = NodePlus(first, self.arg())
            case Operators.MINUS:
                node = NodeMinus(first, self.arg())
            case Operators.LESS:
                node = NodeLess(first, self.arg())
            case Operators.LESS_EQUAL:
                node = NodeLessEqual(first, self.arg())
            case Operators.GREATER:
                node = NodeGreater(first, self.arg())
            case Operators.GREATER_EQUAL:
                node = NodeGreaterEqual(first, self.arg())
            case Operators.DOUBLE_EQUALS:
                node = NodeCompEqual(first, self.arg())
            case Operators.NOT_EQUALS:
                node = NodeNotEqual(first, self.arg())
            case _:
                self.error(f"Был получен токен {self.token}, а ожидался бинарный оператор!")
        self.next_token()
        return node

    def variable(self):
        self.require(Special.ID)
        name = self.lexer.token.value
        self.next_token()
        return NodeVariable(name)

    def lhs(self):
        var = self.variable()
        if self.token == Special.LBR:
            self.next_token()
            args = self.args()
            self.require(Special.RBR)
            self.next_token()
            self.symtable.is_var_exist(var.id, self.lexer.token.pos, True)
            return NodeArrayCall(var.id, args)
        return var

    def rhs(self):
        var = self.variable()
        if self.token == Special.LBR:
            self.next_token()
            args = self.args()
            self.require(Special.RBR)
            self.next_token()
            self.symtable.is_var_exist(var.id, self.lexer.token.pos, True)
            return NodeArrayCall(var.id, args)
        elif self.token == Special.LPAR:
            self.next_token()
            if self.token == Special.RPAR:
                self.next_token()
                if not self.symtable.is_func_exist(var.id):
                    self.error(f"Попытка вызвать функцию {var.id}, которая не была объявлена!")
                return NodeFuncCall(var.id, NodeActualParams(list()))
            args = self.args()
            self.require(Special.RPAR)
            self.next_token()
            if not self.symtable.is_func_exist(var.id):
                self.error(f"Попытка вызвать функцию {var.id}, которая не была объявлена!")
            return NodeFuncCall(var.id, NodeActualParams(args))
        return var

    def variable_list(self):
        var_list = [self.variable()]
        while self.token == Special.COMMA:
            self.next_token()
            var_list.append(self.variable())
        return var_list

    def literal(self):
        node: Node | None = None
        match self.token:
            case Special.INTEGER:
                node = NodeInteger(self.lexer.token.value)
            case Special.FLOAT:
                node = NodeFloat(self.lexer.token.value)
            case Special.STR:
                node = NodeString(self.lexer.token.value)
            case Reserved.TRUE | Reserved.FALSE:
                node = NodeBool(self.token == Reserved.TRUE)
            case _:
                self.error("Неопознанный тип данных!")
        self.next_token()
        return node
