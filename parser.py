from rex import *
import sys


asgn_ops = [
    Operators.EQUALS,
    Operators.PLUS_EQUALS,
    Operators.MINUS_EQUALS,
    Operators.ASTERISK_EQUALS,
    Operators.SLASH_EQUALS,
    Operators.MOD_EQUALS,
    Operators.DEGREE_EQUALS
]


class Node:
    def __get_class_name(self):
        c = str(self.__class__)
        pos_1 = c.find('.') + 1
        pos_2 = c.find("'", pos_1)
        return f"{c[pos_1:pos_2]}"

    def __repr__(self, level=0):
        attrs = self.__dict__
        is_sequence = len(attrs) == 1 and isinstance(list(attrs.values())[0], list)
        res = f"{self.__get_class_name()}\n"
        if is_sequence:
            elements = list(attrs.values())[0]
            for el in elements:
                res += '|   ' * level
                res += "|+-"
                res += el.__repr__(level + 1) if (isinstance(el, Node)) else el.__repr__()
        else:
            for attr_name in attrs:
                res += '|   ' * level
                res += "|+-"
                if isinstance(attrs[attr_name], Special):
                    res += f"{attr_name}: {attrs[attr_name]}"
                elif isinstance(attrs[attr_name], list):
                    res += f"{attr_name}:\n"
                    res += '|   ' * level
                    res += "[\n"
                    for el in attrs[attr_name]:
                        res += '|   ' * (level+1)
                        res += el.__repr__(level + 1) if (isinstance(el, Node)) else el.__repr__()
                    res = res.rstrip('\n')
                    res += "\n"
                    res += '|   ' * level
                    res += "]"
                else:
                    res += f"{attr_name}: {attrs[attr_name].__repr__(level + 1) if (isinstance(attrs[attr_name], Node)) else attrs[attr_name].__repr__()}"
                res = res.rstrip('\n') + "\n"

        return res


class NodeProgram(Node):
    def __init__(self, child):
        self.child = child


class NodeBlock(Node):
    def __init__(self, children):
        self.children = children


class NodeNewLine(Node):
    def __init__(self, line):
        self.line = line


class NodeStatement(Node):
    def __init__(self, statement):
        self.statement = statement


class NodeLiteral(Node):
    def __init__(self, value):
        self.value = value


class NodeBool(NodeLiteral):
    pass


class NodeInteger(NodeLiteral):
    pass


class NodeFloat(NodeLiteral):
    pass


class NodeString(NodeLiteral):
    pass


class NodeVariable(Node):
    def __init__(self, id):
        self.id = id


class NodeBinOperator(Node):
    def __init__(self, left, right):
        self.left = left
        self.right = right


class NodePlus(NodeBinOperator):
    pass
class NodeMinus(NodeBinOperator):
    pass
class NodeAsterisk(NodeBinOperator):
    pass
class NodeSlash(NodeBinOperator):
    pass
class NodeMod(NodeBinOperator):
    pass
class NodeDegree(NodeBinOperator):
    pass


class NodeComp(NodeBinOperator):
    pass
class NodeGreater(NodeComp):
    pass
class NodeGreaterEqual(NodeComp):
    pass
class NodeLess(NodeComp):
    pass
class NodeLessEqual(NodeComp):
    pass
class NodeCompEqual(NodeComp):
    pass
class NodeNotEqual(NodeComp):
    pass
class NodeDoubleDot(NodeBinOperator):
    pass


class NodeAssign(NodeBinOperator):
    pass


class NodeEquals(NodeAssign):
    pass
class NodePlusEquals(NodeAssign):
    pass
class NodeMinusEquals(NodeAssign):
    pass
class NodeAsteriskEquals(NodeAssign):
    pass
class NodeSlashEquals(NodeAssign):
    pass
class NodeModEquals(NodeAssign):
    pass
class NodeDegreeEquals(NodeAssign):
    pass


class NodePrimary(Node):
    def __init__(self, value):
        self.value = value


class NodeIfStatement(Node):
    def __init__(self, condition, block):
        self.condition = condition
        self.block = block
class NodeElsIfStatement(NodeIfStatement):
    pass
class NodeElseStatement(NodeBlock):
    pass


class NodeCycleStatement(Node):
    def __init__(self, condition, block):
        self.condition = condition
        self.block = block


class NodeWhileBlock(NodeCycleStatement):
    pass
class NodeUntilBlock(NodeCycleStatement):
    pass


class NodeForBlock(Node):
    def __init__(self, it, iterable, block):
        self.iter = it
        self.iterable = iterable
        self.block = block


class NodeUnaryOp(Node):
    def __init__(self, right):
        self.right = right


class NodeUnaryMinus(NodeUnaryOp):
    pass
class NodeUnaryPlus(NodeUnaryOp):
    pass


class NodeArgs(Node):
    def __init__(self, arguments):
        self.arguments = arguments


class NodeParams(Node):
    def __init__(self, params):
        self.params = params


class NodeDeclareParams(NodeParams):
    pass
class NodeActualParams(NodeParams):
    pass


class NodeFunc(Node):
    def __init__(self, id, params):
        self.id = id
        self.params = params


class NodeFuncDec(Node):
    def __init__(self, id, params, block):
        self.id = id
        self.params = params
        self.block = block


class NodeFuncCall(NodeFunc):
    pass


class NodeReturn(Node):
    def __init__(self, value):
        self.value = value

class NodeArray(Node):
    def __init__(self, args):
        self.args = args

class NodeArrayCall(Node):
    def __init__(self, id, args):
        self.id = id
        self.args = args

class NodeNext(Node):
    pass

class NodeBreak(Node):
    pass

class NodeNot(Node):
    def __init__(self, expression):
        self.expression = expression

class NodeAnd(NodeBinOperator):
    pass

class NodeOr(NodeBinOperator):
    pass


class Parser:
    def __init__(self, lexer: Rex):
        self.lexer: Rex = lexer
        self.lexer.next_token()
        self.token = self.lexer.lexem.token

    def next_token(self):
        self.lexer.next_token()
        self.token = self.lexer.lexem.token

    def require(self, *args: Enum):
        for arg in args:
            if self.token == arg:
                return
        if len(args) == 1:
            self.error(f'Ожидается токен {args[0]}, получен токен {self.token}!')
        else:
            self.error(f'Ожидается один из токенов {args}, получен токен {self.token}!')

    def error(self, msg: str):
        raise Exception(f'Ошибка синтаксического анализа ({self.lexer.lexem.pos[0]}, {self.lexer.lexem.pos[1]}): {msg}')

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
                self.next_token()
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

    def block(self, *args: Enum) -> Node:
        statements = []
        while self.token not in args:
            statement = self.statement()
            if statement is not None:
                statements.append(statement)
                self.require(Special.NEWLINE, Special.SEMICOLON)
            self.next_token()
        self.next_token()
        return NodeBlock(statements)

    def if_statement(self) -> Node:
        pass

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
                return NodeForBlock(vars_list, iterable, block)
            case KeyWords.WHILE:
                self.next_token()
                condition = self.expression()
                self.require(Special.NEWLINE, Special.SEMICOLON, KeyWords.DO)
                self.next_token()
                block = self.block(KeyWords.END)
                self.next_token()
                return NodeWhileBlock(condition, block)
            case KeyWords.UNTIL:
                self.next_token()
                condition = self.expression()
                self.require(Special.NEWLINE, Special.SEMICOLON, KeyWords.DO)
                self.next_token()
                block = self.block(KeyWords.END)
                self.next_token()
                return NodeUntilBlock(condition, block)

    def declare_params(self) -> Node:
        params = []
        while self.token not in {Special.RPAR}:
            params.append(self.variable())
            self.require(Special.COMMA)
            self.next_token()
        return NodeDeclareParams(params)

    def actual_params(self) -> Node:
        params = []
        while self.token not in {Special.RPAR}:
            params.append(self.expression())
            self.require(Special.COMMA)
            self.next_token()
        return NodeActualParams(params)

    def func_statement(self) -> Node:
        match self.token:
            case Special.ID:
                id = self.lexer.lexem.value
                self.next_token()
                self.require(Special.LPAR)
                self.next_token()
                params = self.actual_params()
                self.require(Special.RPAR)
                self.next_token()
                return NodeFuncCall(id, params)
            case KeyWords.FUNCTION:
                self.next_token()
                id = self.lexer.lexem.value
                self.next_token()
                self.require(Special.LPAR)
                self.next_token()
                params = self.declare_params()
                self.require(Special.RPAR)
                self.next_token()
                self.require(Special.NEWLINE, Special.SEMICOLON)
                self.next_token()
                block = self.block()
                self.require(KeyWords.END)
                self.next_token()
                return NodeFuncDec(id, params, block)
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
            return NodeReturn([])
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
            case _:
                first_arg = self.primary()
        if self.token == Special.DOUBLE_DOT:
            self.next_token()
            return NodeDoubleDot(first_arg, self.arg())
        elif self.token in Operators and self.token not in asgn_ops:
            return self.bin_op(first_arg)
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
        return args

    def primary(self) -> Node:
        match self.token:
            # <literal> | <lhs> | <func_call> | "LBR" [args] "RBR"
            case Special.ID:
                return self.rhs()
            case Special.INTEGER | Special.FLOAT | Special.STR | Reserved.TRUE | Reserved.FALSE | Reserved.NIL:
                return self.literal()
            case Special.LBR:
                # Array definition
                self.next_token()
                args = self.args()
                self.require(Special.RBR)
                self.next_token()
                return NodeArray(args)
            case _:
                self.error(f"Был получен токен {self.token}, а ожидался литерал или функция!")

    def asgn_op(self, lhs):
        match self.token:
            case Operators.EQUALS:
                self.next_token()
                return NodeEquals(lhs, self.arg())
            case Operators.PLUS_EQUALS:
                self.next_token()
                return NodePlusEquals(lhs, self.arg())
            case Operators.MINUS_EQUALS:
                self.next_token()
                return NodeMinusEquals(lhs, self.arg())
            case Operators.ASTERISK_EQUALS:
                self.next_token()
                return NodeAsteriskEquals(lhs, self.arg())
            case Operators.SLASH_EQUALS:
                self.next_token()
                return NodeSlashEquals(lhs, self.arg())
            case Operators.MOD_EQUALS:
                self.next_token()
                return NodeModEquals(lhs, self.arg())
            case Operators.DEGREE_EQUALS:
                self.next_token()
                return NodeDegreeEquals(lhs, self.arg())

    def bin_op(self, first):
        match self.token:
            case Operators.PLUS:
                self.next_token()
                return NodePlus(first, self.arg())
            case Operators.MINUS:
                self.next_token()
                return NodeMinus(first, self.arg())
            case Operators.ASTERISK:
                self.next_token()
                return NodeAsterisk(first, self.arg())
            case Operators.SLASH:
                self.next_token()
                return NodeSlash(first, self.arg())
            case Operators.MOD:
                self.next_token()
                return NodeMod(first, self.arg())
            case Operators.DEGREE:
                self.next_token()
                return NodeDegree(first, self.arg())
            case Operators.LESS:
                self.next_token()
                return NodeLess(first, self.arg())
            case Operators.LESS_EQUAL:
                self.next_token()
                return NodeLessEqual(first, self.arg())
            case Operators.GREATER:
                self.next_token()
                return NodeGreater(first, self.arg())
            case Operators.GREATER_EQUAL:
                self.next_token()
                return NodeGreaterEqual(first, self.arg())
            case Operators.DOUBLE_EQUALS:
                self.next_token()
                return NodeCompEqual(first, self.arg())
            case Operators.NOT_EQUALS:
                self.next_token()
                return NodeNotEqual(first, self.arg())

    def variable(self):
        self.require(Special.ID)
        name = self.lexer.lexem.value
        self.next_token()
        return NodeVariable(name)

    def lhs(self):
        var = self.variable()
        if self.token == Special.LBR:
            self.next_token()
            args = self.args()
            self.require(Special.RBR)
            self.next_token()
            return NodeArrayCall(var, args)
        return var

    def rhs(self):
        var = self.variable()
        if self.token == Special.LBR:
            self.next_token()
            args = self.args()
            self.require(Special.RBR)
            self.next_token()
            return NodeArrayCall(var.id, args)
        elif self.token == Special.LPAR:
            self.next_token()
            args = self.args()
            self.require(Special.RPAR)
            self.next_token()
            return NodeFuncCall(var.id, args)
        return var

    def variable_list(self):
        var_list = [self.variable()]
        while self.token == Special.COMMA:
            self.next_token()
            var_list.append(self.variable())
        return var_list

    def literal(self):
        match self.token:
            case Special.INTEGER:
                val = self.lexer.lexem.value
                self.next_token()
                return NodeInteger(val)
            case Special.FLOAT:
                val = self.lexer.lexem.value
                self.next_token()
                return NodeFloat(val)
            case Special.STR:
                val = self.lexer.lexem.value
                self.next_token()
                return NodeString(val)
            case Reserved.TRUE, Reserved.FALSE:
                val = self.lexer.lexem.value
                self.next_token()
                return NodeBool(val)
            case _:
                self.error("Неопознанный тип данных!")
