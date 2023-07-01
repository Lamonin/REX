from rex import *
import sys


class Node:
    def __get_class_name(self):
        c = str(self.__class__)
        pos_1 = c.find('.') + 1
        pos_2 = c.find("'", pos_1)
        return f"{c[pos_1:pos_2]}"

    def __repr__(self, level=0):
        attrs = self.__dict__
        if len(attrs) == 1 and isinstance(list(attrs.values())[0], list):
            is_sequence = True
        else:
            is_sequence = False
        res = f"{self.__get_class_name()}\n"
        if is_sequence:
            elements = list(attrs.values())[0]
            for el in elements:
                res += '|   ' * level
                res += "|+-"
                res += el.__repr__(level + 1)
        else:
            for attr_name in attrs:
                res += '|   ' * level
                res += "|+-"
                if isinstance(attrs[attr_name], Special):
                    res += f"{attr_name}: {attrs[attr_name]}\n"
                else:
                    res += f"{attr_name}: {attrs[attr_name].__repr__(level + 1)}"
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
class NodeUnaryPlus(Node):
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
class NodeFuncDec(NodeFunc):
    pass
class NodeFuncCall(NodeFunc):
    pass


class NodeReturn(Node):
    def __init__(self, value):
        self.value = value


class Parser:
    def __init__(self, lexer: Rex):
        self.lexer = lexer
        self.token = self.lexer.lexem

    def next_token(self):
        self.lexer.next_token()
        self.token = self.lexer.lexem

    def require(self, *args: Enum):
        for arg in args:
            if self.token.token == arg:
                return
        if len(args) == 1:
            self.error(f'Ожидается токен {args[0]}, получен токен {self.token.token}!')
        else:
            self.error(f'Ожидается один из токенов {args}, получен токен {self.token.token}!')

    def error(self, msg: str):
        print(f'Ошибка синтаксического анализа ({self.lexer.line}, {self.lexer.pos}): {msg}')
        sys.exit(1)

    def statement(self) -> Node:
        match self.token.token:
            # <if_stmt> | <cycle_stmt> | <func_def> | "RETURN" <args> | <expression>
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
            case _:
                return self.expression()

    def if_statement(self) -> Node:
        pass

    def cycle_statement(self) -> Node:
        match self.token.token:
            case KeyWords.FOR:
                pass
            case KeyWords.WHILE:
                pass
            case KeyWords.UNTIL:
                pass

    def func_statement(self) -> Node:
        pass

    def expression(self) -> Node:
        pass

    def return_statement(self) -> Node:
        pass

    def parse(self) -> Node:
        if self.token.token == Special.EOF:
            self.error("Empty file!")
        else:
            statements = []
            while self.token.token != Special.EOF:
                statements.append(self.statement())
                self.require(Special.NEWLINE, Special.SEMICOLON)
                self.next_token()
            return NodeProgram(statements)