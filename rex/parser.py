from rex.lexer import Lexer
from rex.misc import get_args_name_from_count
from rex.types import *
from rex.nodes import *
from rex.symbols import *
from rex.symtable import SymTable

bin_ops = {
    Operators.PLUS: NodePlus,
    Operators.MINUS: NodeMinus,
    Operators.ASTERISK: NodeAsterisk,
    Operators.SLASH: NodeSlash,
    Operators.MOD: NodeMod,
    Operators.DEGREE: NodeDegree,
    Operators.DOUBLE_EQUALS: NodeCompEqual,
    Operators.NOT_EQUALS: NodeNotEqual,
    Operators.LESS: NodeLess,
    Operators.GREATER: NodeGreater,
    Operators.LESS_EQUAL: NodeLessEqual,
    Operators.GREATER_EQUAL: NodeGreaterEqual,
    Special.DOUBLE_DOT: NodeDoubleDot,
    KeyWords.AND: NodeAnd,
    KeyWords.OR: NodeOr
}

unary_ops = {
    Operators.PLUS: NodeUnaryPlus,
    Operators.MINUS: NodeUnaryMinus,
    KeyWords.NOT: NodeNot,
}

assign_ops = {
    Operators.PLUS_EQUALS: NodePlusEquals,
    Operators.MINUS_EQUALS: NodeMinusEquals,
    Operators.ASTERISK_EQUALS: NodeAsteriskEquals,
    Operators.SLASH_EQUALS: NodeSlashEquals,
    Operators.MOD_EQUALS: NodeModEquals,
    Operators.DEGREE_EQUALS: NodeDegreeEquals,
}


def get_node_without_par(node) -> Node:
    while isinstance(node, NodePar):
        node = node.expr
    return node


class ParsingError(Exception):
    pass


class Parser:
    def __init__(self):
        self.lexer: Lexer | None = None
        self.symtable: SymTable | None = None
        self.indent = 0
        self.token = None

    def setup(self, code):
        self.lexer = Lexer()
        self.lexer.setup(code)
        self.lexer.next_token()
        self.symtable = SymTable()
        self.symtable.get_pos = lambda: self.lexer.token.pos
        self.indent = 0
        self.token = self.lexer.token.symbol

    def next_token(self):
        self.lexer.next_token()
        self.token = self.lexer.token.symbol

    def require(self, *args: Enum, message=None):
        if self.token not in args:
            if message:
                self.error(message)
            if len(args) == 1:
                self.error(f"Ожидается токен {args[0]}, получен токен {self.token}!")
            self.error(f"Ожидается один из токенов {args}, получен токен {self.token}!")

    def is_node_logical(self, node: Node) -> bool:
        node = get_node_without_par(node)
        if not issubclass(type(node), NodeLogical):
            if isinstance(node, NodeFuncCall):
                rt = self.symtable.get_function(node.id).return_type
                if rt is not None and issubclass(type(rt), NodeLogical):
                    return True
            return False
        return True

    def error(self, msg: str):
        raise ParsingError(
            f"({self.lexer.token.pos[0]}, {self.lexer.token.pos[1]}) : {msg}"
        )

    def parse(self) -> Node:
        if self.token == Special.EOF:
            self.error("Пустой файл!")

        statements = []
        while self.token != Special.EOF:
            statement = self.statement()

            if statement:
                statements.append(statement)
                if self.token != Special.EOF:
                    self.require(
                        Special.NEWLINE,
                        Special.SEMICOLON,
                        message="Ожидался конец строки!",
                    )

            if isinstance(statement, NodeReturn):
                statement.value = None  # Return value has no meaning
                break  # There is no point in parsing further after return

            self.next_token()

        self.optimize_statements(statements)

        return NodeProgram(statements)

    def block(self, *args: Enum, skip_last=True, initialize_function=None) -> NodeBlock:
        self.symtable.create_local_namespace()
        self.indent += 1

        if initialize_function:
            initialize_function()

        is_return_statement_appeared = False

        statements = []
        while self.token not in args:
            statement = self.statement()

            if statement:
                if not is_return_statement_appeared:  # Ignore statements after return statement
                    statements.append(statement)

                self.require(
                    Special.NEWLINE, Special.SEMICOLON, message="Ожидался конец строки!"
                )

            self.next_token()

            if isinstance(statement, NodeReturn):
                is_return_statement_appeared = True

        if skip_last:
            self.next_token()

        # Optimize block statements
        self.optimize_statements(statements)

        self.symtable.dispose_local_namespace()
        self.indent -= 1

        return NodeBlock(statements, self.indent + 1)

    def optimize_statements(self, statements):
        stmts_to_remove = []

        for stmt in reversed(statements):
            if isinstance(stmt, NodeEquals):
                if self.symtable.get_variable(stmt.left.id).number_of_uses == 0:
                    right_nodes = stmt.right.iterate()
                    for right_node in right_nodes:
                        if isinstance(right_node, NodeVariable):
                            self.symtable.get_variable(right_node.id).number_of_uses -= 1
                        elif isinstance(right_node, NodeFuncCall):
                            self.symtable.get_function(right_node.id).number_of_uses -= 1
                    stmts_to_remove.append(stmt)
            elif isinstance(stmt, NodeFuncDec):
                if self.symtable.get_function(stmt.id).number_of_uses == 0:
                    right_nodes = stmt.iterate()
                    for right_node in right_nodes:
                        if isinstance(right_node, NodeVariable):
                            self.symtable.get_variable(right_node.id).number_of_uses -= 1
                        elif isinstance(right_node, NodeFuncCall):
                            self.symtable.get_function(right_node.id).number_of_uses -= 1
                    stmts_to_remove.append(stmt)

        # Apply optimizations for node-tree
        for stmt in stmts_to_remove:
            statements.remove(stmt)

        # Trim newlines in beginning and end of block
        stmts_to_remove.clear()
        for stmt in statements:
            if not isinstance(stmt, NodeNewLine):
                break
            stmts_to_remove.append(stmt)

        # Apply trim for node-tree
        for stmt in stmts_to_remove:
            statements.remove(stmt)

        stmts_to_remove.clear()
        for stmt in reversed(statements):
            if not isinstance(stmt, NodeNewLine):
                break
            stmts_to_remove.append(stmt)

        # Apply trim for node-tree
        for stmt in stmts_to_remove:
            statements.remove(stmt)

    def statement(self) -> Node | None:
        match self.token:
            case Special.NEWLINE:
                return NodeNewLine()
            case KeyWords.IF:
                self.next_token()
                return self.if_statement()
            case KeyWords.WHILE | KeyWords.UNTIL | KeyWords.FOR:
                return self.cycle_statement()
            case KeyWords.FUNCTION:
                return self.func_definition()
            case KeyWords.RETURN:
                self.next_token()
                return self.return_statement()
            case KeyWords.NEXT:
                self.next_token()
                return NodeNext()
            case KeyWords.BREAK:
                self.next_token()
                return NodeBreak()
            case Special.ID:
                lhs = self.lhs()
                if self.token == Special.LPAR:  # function call
                    return self.function_call(lhs.id)
                if not isinstance(lhs, NodeFuncCall):  # assign operation
                    return self.assign_op(lhs)
        self.error(f"Некорректная конструкция {self.lexer.token.pos}")

    def if_statement(self) -> Node:
        if_block = self.if_block()
        if self.token == KeyWords.END:
            self.next_token()
            return NodeIfBlock(if_block, self.indent)
        else:
            elsif_blocks = None
            else_block = None
            if self.token == KeyWords.ELSIF:
                elsif_blocks = []
                while self.token not in {KeyWords.END, KeyWords.ELSE}:
                    elsif_blocks.append(self.elseif_block())
                if self.token != KeyWords.ELSE:
                    self.next_token()
            if self.token == KeyWords.ELSE:
                else_block = self.else_block()
            return NodeIfBlock(if_block, self.indent, elsif_blocks, else_block)

    def if_block(self) -> Node:
        condition = self.arg(end=[KeyWords.THEN, Special.NEWLINE, Special.SEMICOLON])

        if not self.is_node_logical(condition):
            self.error(f"Ожидалось логическое выражение, а получено {type(condition).__name__}")

        self.require(KeyWords.THEN, Special.NEWLINE, Special.SEMICOLON)
        self.next_token()
        if self.token == Special.NEWLINE:
            self.next_token()
        block = self.block(KeyWords.END, KeyWords.ELSIF, KeyWords.ELSE, skip_last=False)
        return NodeIfStatement(condition, block)

    def elseif_block(self) -> Node:
        self.next_token()
        condition = self.arg(end=[KeyWords.THEN, Special.NEWLINE, Special.SEMICOLON])
        self.require(KeyWords.THEN, Special.NEWLINE, Special.SEMICOLON)
        self.next_token()
        block = self.block(KeyWords.END, KeyWords.ELSIF, KeyWords.ELSE, skip_last=False)
        return NodeElsIfStatement(condition, block)

    def else_block(self) -> Node:
        self.next_token()
        self.require(Special.NEWLINE)
        self.next_token()
        block = self.block(KeyWords.END)
        return NodeElseStatement(block, self.indent)

    def declare_params(self) -> NodeDeclareParams:
        params = []
        while self.token != Special.RPAR:
            params.append(self.variable())
            if self.token == Special.COMMA:
                self.next_token()
        return NodeDeclareParams(params)

    def actual_params(self) -> NodeActualParams:
        params = []
        while self.token != Special.RPAR:
            params.append(self.arg(end=[Special.COMMA], pars=True))
            if self.token == Special.COMMA:
                self.next_token()
        return NodeActualParams(params)

    def cycle_statement(self) -> Node:
        match self.token:
            case KeyWords.FOR:
                self.next_token()
                vars_list = self.variable_list()
                self.require(KeyWords.IN)
                self.next_token()
                iterable = self.arg(
                    end=[KeyWords.DO, Special.NEWLINE, Special.SEMICOLON]
                )
                self.require(KeyWords.DO, Special.NEWLINE, Special.SEMICOLON)
                self.next_token()
                if self.token == Special.NEWLINE:
                    self.next_token()

                def init_function():
                    for v in vars_list:
                        self.symtable.add_variable(v.id, Auto())

                block = self.block(KeyWords.END, initialize_function=init_function)

                return NodeForBlock(
                    NodeActualParams(vars_list), iterable, block, self.indent
                )
            case KeyWords.WHILE:
                self.next_token()
                condition = self.arg(
                    end=[KeyWords.DO, Special.NEWLINE, Special.SEMICOLON]
                )
                self.require(Special.NEWLINE, Special.SEMICOLON, KeyWords.DO)
                self.next_token()
                if self.token == Special.NEWLINE:
                    self.next_token()
                block = self.block(KeyWords.END)
                return NodeWhileBlock(condition, block, self.indent)
            case KeyWords.UNTIL:
                self.next_token()
                condition = self.arg(
                    end=[KeyWords.DO, Special.NEWLINE, Special.SEMICOLON]
                )
                self.require(Special.NEWLINE, Special.SEMICOLON, KeyWords.DO)
                self.next_token()
                if self.token == Special.NEWLINE:
                    self.next_token()
                block = self.block(KeyWords.END)
                return NodeUntilBlock(condition, block, self.indent)

    def func_definition(self) -> Node:
        if self.token == KeyWords.FUNCTION:
            self.next_token()
            func_id = self.lexer.token.value
            self.next_token()
            self.require(Special.LPAR, message="Пропущена открывающая скобка!")
            self.next_token()
            params = self.declare_params()
            self.require(Special.RPAR, message="Пропущена закрывающая скобка!")
            self.next_token()
            self.require(Special.NEWLINE, Special.SEMICOLON)
            self.next_token()

            def init_function():
                for p in params.params:
                    self.symtable.add_variable(p.id, Auto())

            block = self.block(KeyWords.END, initialize_function=init_function)

            return_type = None
            for stmt in block.statements:
                if isinstance(stmt, NodeReturn):
                    rt = stmt.value
                    while isinstance(rt, NodeFuncCall):
                        rt = self.symtable.get_function(rt.id).return_type
                    return_type = rt
                    break

            self.symtable.add_function(
                func_id,
                Function(args_count=len(params.params), return_type=return_type),
            )
            return NodeFuncDec(func_id, params, block, self.indent)
        self.error("Ожидалось объявление функции!")

    def function_call(self, func_name):
        self.next_token()
        call_args = self.args(end=[Special.COMMA, Special.NEWLINE], pars=True)
        self.require(Special.RPAR, message="Пропущена закрывающая скобка!")
        self.next_token()

        self.symtable.check_function_arguments_count(func_name, len(call_args.arguments))

        f = self.symtable.get_function(func_name)
        f.number_of_uses += 1

        if isinstance(f, PredefinedFunction):
            return NodeFuncCall(f.predefined_name, call_args, f.predefined_construction)

        return NodeFuncCall(func_name, call_args)

    def return_statement(self) -> Node:
        if self.token in [Special.NEWLINE, Special.SEMICOLON]:
            return NodeReturn()
        args = self.args()
        return NodeReturn(args.arguments[0] if len(args.arguments) == 1 else args)

    def arg(self, end=None, pars=False):
        if end is None:
            end = [Special.NEWLINE, Special.EOF]

        def get_op_priority(op) -> int:
            match op:
                case Special.LPAR:
                    return 0
                case KeyWords.AND | KeyWords.OR:
                    return 1
                case Operators.DOUBLE_EQUALS | Operators.NOT_EQUALS | Operators.LESS | Operators.GREATER | Operators.LESS_EQUAL | Operators.GREATER_EQUAL:
                    return 2
                case Operators.PLUS | Operators.MINUS:
                    return 3
                case Operators.ASTERISK | Operators.SLASH | Operators.MOD | Special.DOUBLE_DOT:
                    return 4
                case Operators.DEGREE:
                    return 5
                case _:
                    if isinstance(op, type) and issubclass(op, NodeUnaryOp):
                        return 5
            self.error(f"Некорректный элемент математического выражения {op}")

        def apply_stack_op():
            top_of_temp_stack = temp_stack.pop()

            if isinstance(top_of_temp_stack, type) and issubclass(top_of_temp_stack, NodeUnaryOp):
                top_of_out_stack = out_stack.pop()
                if type(top_of_out_stack) is top_of_temp_stack:
                    out_stack.append(top_of_out_stack.right)
                else:
                    out_stack.append(top_of_temp_stack(top_of_out_stack))
            elif top_of_temp_stack in bin_ops:
                right_operand = out_stack.pop()
                left_operand = out_stack.pop()

                if top_of_temp_stack in [KeyWords.AND, KeyWords.OR]:
                    if not self.is_node_logical(left_operand):
                        self.error(
                            f"Ожидалось логическое значение, а получено "
                            f"{get_node_without_par(left_operand).__class__.__name__}"
                        )
                    if not self.is_node_logical(right_operand):
                        self.error(
                            f"Ожидалось логическое значение, а получено "
                            f"{get_node_without_par(right_operand).__class__.__name__}"
                        )

                # TODO Добавить проверку соответствия типов у числовых операторов
                # TODO Попробовать оптимизировать логические операторы

                out_stack.append(bin_ops[top_of_temp_stack](left_operand, right_operand))
            elif top_of_temp_stack == Special.LPAR:
                self.error("Пропущена закрывающая скобка!")
            else:
                out_stack.append(top_of_temp_stack)

        temp_stack = []
        out_stack: list[Node] = []
        left_par_count = 0
        last_parsed_is_op = True

        while self.token not in end:
            if self.token not in bin_ops and self.token not in unary_ops:
                last_parsed_is_op = False
                if self.token == Special.LPAR:
                    left_par_count += 1
                    temp_stack.append(self.token)
                    self.next_token()
                    last_parsed_is_op = True
                elif self.token == Special.RPAR:
                    if left_par_count == 0 and pars:
                        break
                    while temp_stack[-1] != Special.LPAR:
                        apply_stack_op()
                        if len(temp_stack) == 0:
                            self.error("Пропущена открывающая скобка!")
                    temp_stack.pop()
                    left_par_count -= 1
                    if not isinstance(out_stack[-1], NodeLiteral) and not isinstance(
                            out_stack[-1], NodePar
                    ):
                        out_stack.append(NodePar(out_stack.pop()))
                    self.next_token()
                else:
                    out_stack.append(self.primary())
            else:
                if last_parsed_is_op:
                    if self.token not in unary_ops:
                        self.error(f"Неправильный унарный оператор {self.token}")
                    temp_stack.append(unary_ops[self.token])
                else:
                    last_parsed_is_op = True
                    opp = get_op_priority(self.token)
                    while (
                            len(temp_stack) > 0 and get_op_priority(temp_stack[-1]) >= opp
                    ):
                        apply_stack_op()
                    temp_stack.append(self.token)
                self.next_token()

        while len(temp_stack) > 0:
            apply_stack_op()

        arg = out_stack.pop() if len(out_stack) else None

        while isinstance(arg, NodePar):
            arg = arg.expr

        return arg

    def args(self, end=None, pars=False):
        if end is None:
            end = [Special.COMMA, Special.NEWLINE]
        args = list()
        first_arg = self.arg(end=end, pars=pars)
        if first_arg:
            args.append(first_arg)
            while self.token == Special.COMMA:
                self.next_token()
                args.append(self.arg(end=end, pars=pars))
        return NodeArgs(args)

    def assign_op(self, lhs):
        if self.token == Operators.EQUALS:
            self.next_token()
            value = self.arg()

            if isinstance(value, NodeArray):
                self.symtable.add_variable(lhs.id, Array())
            else:
                self.symtable.add_variable(lhs.id, Variable())

            return NodeEquals(lhs, value)
        else:
            if self.token not in assign_ops:
                self.error(f"Неизвестный оператор присваивания {self.token}")
            self.symtable.check_variable_presence(lhs.id)
            assign_op = assign_ops[self.token]
            self.next_token()
            return assign_op(lhs, self.arg())

    def bin_op(self, first):
        bin_operator: dict = {
            Operators.ASTERISK: NodeAsterisk,
            Operators.SLASH: NodeSlash,
            Operators.MOD: NodeMod,
            Operators.DEGREE: NodeDegree,
            Operators.PLUS: NodePlus,
            Operators.MINUS: NodeMinus,
            Operators.GREATER: NodeGreater,
            Operators.GREATER_EQUAL: NodeGreaterEqual,
            Operators.LESS: NodeLess,
            Operators.LESS_EQUAL: NodeLessEqual,
            Operators.DOUBLE_EQUALS: NodeCompEqual,
            Operators.NOT_EQUALS: NodeNotEqual,
        }

        if self.token not in bin_operator:
            self.error(f"Был получен токен {self.token}, а ожидался бинарный оператор!")

        node = bin_operator[self.token](first, self.arg())
        self.next_token()
        return node

    def primary(self) -> Node:
        match self.token:
            # <literal> | <lhs> | <func_call> | "LBR" [args] "RBR"
            case Special.ID:
                return self.rhs()
            case Special.INTEGER | Special.FLOAT | Special.STR | Reserved.TRUE | Reserved.FALSE | Reserved.NIL:
                return self.literal()
            case Special.LBR:
                self.next_token()
                if self.token == Special.RBR:
                    self.next_token()
                    return NodeArray()
                args = self.args()
                self.require(Special.RBR)
                self.next_token()
                return NodeArray(args)
            case _:
                self.error(
                    f"Был получен токен {self.token}, а ожидался литерал или функция!"
                )

    def variable(self):
        self.require(Special.ID, message="Ожидалась переменная!")
        name = self.lexer.token.value
        self.next_token()
        return NodeVariable(name)

    def variable_list(self):
        var_list = [self.variable()]
        while self.token == Special.COMMA:
            self.next_token()
            var_list.append(self.variable())
        return var_list

    def lhs(self):
        var = self.variable()
        if self.token == Special.LBR:
            args = []
            while self.token == Special.LBR:
                self.next_token()
                idx = self.arg(end=[Special.RBR, Special.COMMA])
                if isinstance(idx, NodeFloat):
                    self.error("Индексами массива могут быть только целые числа!")
                args.append(idx)
                self.require(Special.RBR)
                self.next_token()
            self.symtable.check_variable_is_array(var.id)
            return NodeArrayCall(var.id, args)
        return var

    def rhs(self):
        lhs = self.lhs()

        if isinstance(lhs, NodeVariable) and self.token == Special.LPAR:
            return self.function_call(lhs.id)

        self.symtable.check_variable_presence(lhs.id)
        self.symtable.get_variable(lhs.id).number_of_uses += 1

        return lhs

    def literal(self):
        node = None
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
