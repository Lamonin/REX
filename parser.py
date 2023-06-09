from rex import *


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
                res += el.__repr__(level + 1)
            res += "\n"
        else:
            for attr_name in attrs:
                res += '|   ' * level
                res += "|+-"
                if isinstance(attrs[attr_name], Special):
                    res += f"{attr_name}: {attrs[attr_name]}"
                elif isinstance(attrs[attr_name], list):
                    attr_count = len(attrs[attr_name])
                    res += f"{attr_name}:"
                    if attr_count > 0:
                        res += "\n"
                        res += '|   ' * level
                    res += "["
                    if attr_count > 0:
                        res += "\n"
                    for el in attrs[attr_name]:
                        res += '|   ' * (level+1)
                        res += el.__repr__(level + 1) if (isinstance(el, Node)) else el.__repr__()
                    res = res.rstrip('\n')
                    if attr_count > 0:
                        res += "\n"
                        res += '|   ' * level
                    res += "]"
                else:
                    res += f"{attr_name}: {attrs[attr_name].__repr__(level + 1) if (isinstance(attrs[attr_name], Node)) else attrs[attr_name].__repr__()}"
                res = res.rstrip('\n') + "\n"

        return res

    def generate(self):
        pass


class NodeProgram(Node):
    def __init__(self, child):
        self.child = child

    def generate(self):
        code = ""
        for i in self.child:
            code += f"{i.generate()}"
        return code


class NodeBlock(Node):
    def __init__(self, children):
        self.children = children

    def generate(self):
        code = ""
        for i in self.children:
            code += f"{i.generate()}"
        return code


class NodeNewLine(Node):
    def __init__(self, line):
        self.line = line

    def generate(self):
        return "\n"


class NodeStatement(Node):
    def __init__(self, statement):
        self.statement = statement

    def generate(self):
        return self.statement.generate()


class NodeLiteral(Node):
    def __init__(self, value):
        self.value = value

    def generate(self):
        return str(self.value)


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

    def generate(self):
        return f"{self.id}"


class NodeBinOperator(Node):
    def __init__(self, left, right):
        self.left = left
        self.right = right


class NodePlus(NodeBinOperator):

    def generate(self):
        return f"{self.left.generate()} + {self.right.generate()}"


class NodeMinus(NodeBinOperator):
    def generate(self):
        return f"{self.left.generate()} - {self.right.generate()}"


class NodeAsterisk(NodeBinOperator):
    def generate(self):
        return f"{self.left.generate()} * {self.right.generate()}"


class NodeSlash(NodeBinOperator):
    def generate(self):
        return f"{self.left.generate()} / {self.right.generate()}"


class NodeMod(NodeBinOperator):
    def generate(self):
        return f"{self.left.generate()} * {self.right.generate()}"


class NodeDegree(NodeBinOperator):
    def generate(self):
        return f"{self.left.generate()} * {self.right.generate()}"


class NodeComp(NodeBinOperator):
    pass


class NodeGreater(NodeComp):
    def generate(self):
        return f"{self.left.generate()} > {self.right.generate()}"


class NodeGreaterEqual(NodeComp):
    def generate(self):
        return f"{self.left.generate()} >= {self.right.generate()}"


class NodeLess(NodeComp):
    def generate(self):
        return f"{self.left.generate()} < {self.right.generate()}"


class NodeLessEqual(NodeComp):
    def generate(self):
        return f"{self.left.generate()} <= {self.right.generate()}"


class NodeCompEqual(NodeComp):
    def generate(self):
        return f"{self.left.generate()} == {self.right.generate()}"


class NodeNotEqual(NodeComp):
    def generate(self):
        return f"{self.left.generate()} != {self.right.generate()}"


class NodeDoubleDot(NodeBinOperator):
    def generate(self):
        return f"{self.left.generate()}:{self.right.generate()}"


class NodeAssign(NodeBinOperator):
    pass


class NodeEquals(NodeAssign):
    def generate(self):
        return f"{self.left.generate()} = {self.right.generate()}"


class NodePlusEquals(NodeAssign):
    def generate(self):
        return f"{self.left.generate()} <- {self.left.generate()} + {self.right.generate()}"


class NodeMinusEquals(NodeAssign):
    def generate(self):
        return f"{self.left.generate()}<- {self.left.generate()} - {self.right.generate()}"


class NodeAsteriskEquals(NodeAssign):
    def generate(self):
        return f"{self.left.generate()}<- {self.left.generate()} * {self.right.generate()}"


class NodeSlashEquals(NodeAssign):
    def generate(self):
        return f"{self.left.generate()}<- {self.left.generate()} / {self.right.generate()}"


class NodeModEquals(NodeAssign):
    def generate(self):
        return f"{self.left.generate()}<- {self.left.generate()} % {self.right.generate()}"


class NodeDegreeEquals(NodeAssign):
    def generate(self):
        return f"{self.left.generate()}<- {self.left.generate()} ** {self.right.generate()}"


class NodePrimary(Node):
    def __init__(self, value):
        self.value = value

    def generate(self):
        return self.value.generate()


class NodeIfStatement(Node):
    def __init__(self, condition, block):
        self.condition = condition
        self.block = block

    def generate(self):
        return f"if {self.condition.generate()} {{\n{self.block.generate()}\n}}"


class NodeElsIfStatement(NodeIfStatement):
    def generate(self):
        return f"else if ({self.condition.generate()}) {{\n{self.block.generate()}\n}}"


class NodeElseStatement(NodeBlock):
    pass


class NodeIfBlock(Node):
    def __init__(self, if_block, elsif=[], else_block=None):
        self.if_block = if_block
        self.elsif = elsif if len(elsif) > 0 else ""
        self.else_block = else_block if else_block is not None else ""

    def generate(self):
        code = f"{self.if_block.generate()}"
        for eif in self.elsif:
            code += f" {eif.generate()}"
        if self.else_block != "":
            print(type(self.else_block))
            code += f"else {{{self.else_block.generate()}\n}}"
        return code


class NodeCycleStatement(Node):
    def __init__(self, condition, block):
        self.condition = condition
        self.block = block


class NodeWhileBlock(NodeCycleStatement):
    def generate(self):
        return f"while ({self.condition.generate()})\n{{{self.block.generate()}\n}}"


class NodeUntilBlock(NodeCycleStatement):
    pass


class NodeForBlock(Node):
    def __init__(self, it, iterable, block):
        self.iter = it
        self.iterable = iterable
        self.block = block

    def generate(self):
        return f"for ({self.iter.generate()} in {self.iterable.generate})" + "{\n" + f"{self.block.generate()}" + "}"


class NodeUnaryOp(Node):
    def __init__(self, right):
        self.right = right


class NodeUnaryMinus(NodeUnaryOp):
    def generate(self):
        return f"-{self.right.generate()}"


class NodeUnaryPlus(NodeUnaryOp):
    def generate(self):
        return f"+{self.right.generate()}"


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

    def generate(self):
        return f"{self.id}{self.args}"


class NodeNext(Node):
    def generate(self):
        return "next\n"


class NodeBreak(Node):
    def generate(self):
        return "break\n"


class NodeNot(Node):
    def __init__(self, expression):
        self.expression = expression


class NodeAnd(NodeBinOperator):
    pass


class NodeOr(NodeBinOperator):
    pass


class SymTable:
    def __init__(self):
        self.table = {
            "puts": (type(NodeFunc), None)
        }

    def Add(self, id: str, type, value, pos):
        if id in self.table:
            self.error(f"Символ с именем {id} уже существует!", pos)
        else:
            self.table[id] = (type, value)

    def Set(self, id, value, pos):
        if id not in self.table:
            self.error(f"Попытка присвоить значение {value} для несуществующего символа {id}!", pos)
        else:
            self.table[id] = (self.table[id][0], value)

    def Get(self, id, pos):
        if id not in self.table:
            self.error(f"Символа с именем {id} не существует!", pos)
        else:
            return self.table[id]

    def Exist(self, id):
        return id in self.table

    def error(self, msg: str, pos):
        raise Exception(f'Ошибка семантического анализа ({pos[0]}, {pos[1]}): {msg}')


class Parser:
    def __init__(self, lexer: Rex):
        self.lexer: Rex = lexer
        self.lexer.next_token()
        self.token = self.lexer.lexem.token
        self.symtable = SymTable()

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
        statements = []
        while self.token not in args:
            statement = self.statement()
            if statement is not None:
                statements.append(statement)
                self.require(Special.NEWLINE, Special.SEMICOLON)
            self.next_token()
        if skiplast:
            self.next_token()
        return NodeBlock(statements)

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
        return NodeElseStatement(block)

    def if_statement(self) -> Node:
        block = []
        if_block = self.if_block()
        block.append(if_block)
        if self.token == KeyWords.END:
            self.next_token()
            return if_block
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
            return NodeIfBlock(if_block, elsif_block, else_block)

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
                self.symtable.Add(id, type(NodeFunc), None, self.lexer.lexem.pos)
                self.next_token()
                self.require(Special.LPAR)
                self.next_token()
                params = self.declare_params()
                self.require(Special.RPAR)
                self.next_token()
                self.require(Special.NEWLINE, Special.SEMICOLON)
                self.next_token()
                block = self.block(KeyWords.END)
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
        return args

    def primary(self) -> Node:
        match self.token:
            # <literal> | <lhs> | <func_call> | "LBR" [args] "RBR"
            case Special.ID:
                return self.rhs()
            case Special.INTEGER | Special.FLOAT | Special.STR | Reserved.TRUE | Reserved.FALSE | Reserved.NIL:
                return self.literal()
            case Special.LBR: # Array definition
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
                return expr
            case _:
                self.error(f"Был получен токен {self.token}, а ожидался литерал или функция!")

    def asgn_op(self, lhs):
        match self.token:
            case Operators.EQUALS:
                self.next_token()
                t = self.arg()
                if self.symtable.Exist(lhs.id):
                    self.symtable.Set(lhs.id, t, self.lexer.lexem.pos)
                else:
                    self.symtable.Add(lhs.id, type(t), t, self.lexer.lexem.pos)
                return NodeEquals(lhs, t)
            case Operators.ASTERISK_EQUALS:
                self.symtable.Get(lhs.id, self.lexer.lexem.pos)
                self.next_token()
                return NodeAsteriskEquals(lhs, self.arg())
            case Operators.SLASH_EQUALS:
                self.symtable.Get(lhs.id, self.lexer.lexem.pos)
                self.next_token()
                return NodeSlashEquals(lhs, self.arg())
            case Operators.MOD_EQUALS:
                self.symtable.Get(lhs.id, self.lexer.lexem.pos)
                self.next_token()
                return NodeModEquals(lhs, self.arg())
            case Operators.DEGREE_EQUALS:
                self.symtable.Get(lhs.id, self.lexer.lexem.pos)
                self.next_token()
                return NodeDegreeEquals(lhs, self.arg())
            case Operators.PLUS_EQUALS:
                self.symtable.Get(lhs.id, self.lexer.lexem.pos)
                self.next_token()
                return NodePlusEquals(lhs, self.arg())
            case Operators.MINUS_EQUALS:
                self.symtable.Get(lhs.id, self.lexer.lexem.pos)
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
            self.symtable.Get(var.id, self.lexer.lexem.pos)
            return NodeArrayCall(var.id, args)
        return var

    def rhs(self):
        var = self.variable()
        if self.token == Special.LBR:
            self.next_token()
            args = self.args()
            self.require(Special.RBR)
            self.next_token()
            self.symtable.Get(var.id, self.lexer.lexem.pos)
            return NodeArrayCall(var.id, args)
        elif self.token == Special.LPAR:
            self.next_token()
            if self.token == Special.RPAR:
                self.next_token()
                return NodeFuncCall(var.id, [])
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
        node: Node | None = None
        match self.token:
            case Special.INTEGER:
                node = NodeInteger(self.lexer.lexem.value)
            case Special.FLOAT:
                node = NodeFloat(self.lexer.lexem.value)
            case Special.STR:
                node = NodeString(self.lexer.lexem.value)
            case Reserved.TRUE | Reserved.FALSE:
                node = NodeBool(self.token == Reserved.TRUE)
            case _:
                self.error("Неопознанный тип данных!")
        self.next_token()
        return node
