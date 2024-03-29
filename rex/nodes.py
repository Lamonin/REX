import operator
from rex.symbols import Special
from rex.misc import try_to_num, convert_float_to_int


def get_indent(indent: int):
    indent_str = ""
    for i in range(indent):
        indent_str += "\t"
    return indent_str


class Node:
    def __repr__(self, level=0):
        attrs = self.__dict__
        is_sequence = len(attrs) == 1 and isinstance(list(attrs.values())[0], list)
        res = f"{self.__class__.__name__}\n"
        if is_sequence:
            elements = list(attrs.values())[0]
            for el in elements:
                res += "|\t" * level
                res += "|+-"
                res += el.__repr__(level + 1)
            res += "\n"
        else:
            for attr_name in attrs:
                res += "|\t" * level
                res += "|+-"
                if isinstance(attrs[attr_name], Special):
                    res += f"{attr_name}: {attrs[attr_name]}"
                elif isinstance(attrs[attr_name], list):
                    attr_count = len(attrs[attr_name])
                    res += f"{attr_name}:"
                    if attr_count > 0:
                        res += "\n"
                        res += "|\t" * level
                    res += "["
                    if attr_count > 0:
                        res += "\n"
                    for el in attrs[attr_name]:
                        res += "|\t" * (level + 1)
                        res += (
                            el.__repr__(level + 1)
                            if (isinstance(el, Node))
                            else el.__repr__()
                        )
                    res = res.rstrip("\n")
                    if attr_count > 0:
                        res += "\n"
                        res += "|\t" * level
                    res += "]"
                else:
                    res += f"{attr_name}: {attrs[attr_name].__repr__(level + 1) if (isinstance(attrs[attr_name], Node)) else attrs[attr_name].__repr__()}"
                res = res.rstrip("\n") + "\n"

        return res

    def generate(self) -> str:
        pass

    def iterate(self) -> list:
        return [self]


class NodeProgram(Node):
    def __init__(self, child):
        self.child = child

    def generate(self):
        code = ""
        for i in self.child:
            code += f"{i.generate()}\n"
        return code

    def iterate(self) -> list:
        iterate_result = list()
        for child in self.child:
            iterate_result.extend(child.iterate())
        return iterate_result


class NodeBlock(Node):
    def __init__(self, statements, indent: int):
        self.indent = indent
        self.statements = statements

    def generate(self, indent=0):
        code = ""
        indent_str = get_indent(self.indent if indent == 0 else indent)
        if isinstance(self.statements, list):
            for i in self.statements:
                code += f"{indent_str}{i.generate()}\n"
        else:
            code += f"{self.statements.generate(indent)}"
        return code

    def iterate(self) -> list:
        iterate_result = list()
        for stmt in self.statements:
            iterate_result.extend(stmt.iterate())
        return iterate_result


class NodeNewLine(Node):
    def generate(self):
        return ""


# TODO: Не используется, возможно стоит удалить
class NodeStatement(Node):
    def __init__(self, statement):
        self.statement = statement

    def generate(self):
        return self.statement.generate() + "\n"


class NodeComment(Node):
    def __init__(self, comment):
        self.comment = comment

    def generate(self):
        return f"#{self.comment}"


class NodeLiteral(Node):
    def __init__(self, value):
        self.value = value

    def generate(self):
        return str(self.value)


class NodeInteger(NodeLiteral):
    pass


class NodeFloat(NodeLiteral):
    pass


class NodeString(NodeLiteral):
    def generate(self):
        return f'"{self.value}"'


class NodeNil(Node):
    def generate(self):
        return "NULL"


class NodeLogical:
    pass


class NodeBool(NodeLiteral, NodeLogical):
    def generate(self):
        return str(self.value).upper()


class NodeVariable(Node):
    def __init__(self, id):
        self.id = id

    def generate(self):
        return str(self.id)


class NodePar(Node):
    def __init__(self, expr):
        self.expr = expr

    def generate(self):
        expr = self.expr.generate()
        if try_to_num(expr)[0]:
            return f"{expr}"
        return f"({expr})"

    def iterate(self) -> list:
        return self.expr.iterate()


# region Binary Operators
class NodeBinOperator(Node):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def iterate(self) -> list:
        iterate_result = [item for sublist in [self.left.iterate(), self.right.iterate()] for item in sublist]
        return iterate_result


class NodeNumericBinOperator(NodeBinOperator):
    def calc(self, op_symbol: str, op: operator):
        left = self.left.generate()
        right = self.right.generate()
        left_num = try_to_num(left)
        right_num = try_to_num(right)
        if left_num[0] and right_num[0]:
            return f"{convert_float_to_int(op(left_num[1], right_num[1]))}"
        return f"{left} {op_symbol} {right}"


class NodePlus(NodeNumericBinOperator):
    def generate(self):
        return self.calc("+", operator.add)


class NodeMinus(NodeNumericBinOperator):
    def generate(self):
        return self.calc("-", operator.sub)


class NodeAsterisk(NodeNumericBinOperator):
    def generate(self):
        return self.calc("*", operator.mul)


class NodeSlash(NodeNumericBinOperator):
    def generate(self):
        return self.calc("/", operator.truediv)


class NodeMod(NodeNumericBinOperator):
    def generate(self):
        return self.calc("%%", operator.mod)


class NodeDegree(NodeNumericBinOperator):
    def generate(self):
        return self.calc("^", operator.pow)


class NodeGreater(NodeBinOperator, NodeLogical):
    def generate(self):
        return f"{self.left.generate()} > {self.right.generate()}"


class NodeGreaterEqual(NodeBinOperator, NodeLogical):
    def generate(self):
        return f"{self.left.generate()} >= {self.right.generate()}"


class NodeLess(NodeBinOperator, NodeLogical):
    def generate(self):
        return f"{self.left.generate()} < {self.right.generate()}"


class NodeLessEqual(NodeBinOperator, NodeLogical):
    def generate(self):
        return f"{self.left.generate()} <= {self.right.generate()}"


class NodeCompEqual(NodeBinOperator, NodeLogical):
    def generate(self):
        return f"{self.left.generate()} == {self.right.generate()}"


class NodeNotEqual(NodeBinOperator, NodeLogical):
    def generate(self):
        return f"{self.left.generate()} != {self.right.generate()}"


class NodeAnd(NodeBinOperator):
    def generate(self):
        return f"{self.left.generate()} & {self.right.generate()}"


class NodeOr(NodeBinOperator):
    def generate(self):
        return f"{self.left.generate()} | {self.right.generate()}"


class NodeDoubleDot(NodeBinOperator):
    def generate(self):
        return f"{self.left.generate()}:{self.right.generate()}"


class NodeEquals(NodeBinOperator):
    def generate(self):
        return f"{self.left.generate()} <- {self.right.generate()}"


class NodePlusEquals(NodeBinOperator):
    def generate(self):
        return f"{self.left.generate()} <- {self.left.generate()} + {self.right.generate()}"


class NodeMinusEquals(NodeBinOperator):
    def generate(self):
        return f"{self.left.generate()} <- {self.left.generate()} - {self.right.generate()}"


class NodeAsteriskEquals(NodeBinOperator):
    def generate(self):
        return f"{self.left.generate()} <- {self.left.generate()} * {self.right.generate()}"


class NodeSlashEquals(NodeBinOperator):
    def generate(self):
        return f"{self.left.generate()} <- {self.left.generate()} / {self.right.generate()}"


class NodeModEquals(NodeBinOperator):
    def generate(self):
        return f"{self.left.generate()} <- {self.left.generate()} % {self.right.generate()}"


class NodeDegreeEquals(NodeBinOperator):
    def generate(self):
        return f"{self.left.generate()} <- {self.left.generate()} ** {self.right.generate()}"

# endregion


class NodePrimary(Node):
    def __init__(self, value):
        self.value = value

    def generate(self):
        return self.value.generate()


class NodeIfStatement(Node):
    def __init__(self, condition, block):
        self.condition = condition
        self.block = block

    def generate(self, indent=0):
        indent_str = get_indent(indent)
        return f"if ({self.condition.generate()}) {{\n{self.block.generate(indent + 1)}{indent_str}}}"

    def iterate(self) -> list:
        result = self.condition.iterate()
        result.extend(self.block.iterate())
        return result


class NodeElsIfStatement(NodeIfStatement):
    def generate(self, indent=0):
        indent_str = get_indent(indent)
        return f"else if ({self.condition.generate()}) {{\n{self.block.generate(indent + 1)}{indent_str}}}"


class NodeElseStatement(NodeBlock):
    def generate(self, indent=0):
        indent_str = get_indent(indent)
        return f"else {{\n{super().generate(indent + 1)}{indent_str}}}"


class NodeIfBlock(Node):
    def __init__(self, if_block, indent: int, elsif=None, else_block=None):
        self.indent = indent
        self.if_block = if_block
        self.elsif = elsif if elsif is not None else ""
        self.else_block = else_block if else_block is not None else ""

    def generate(self):
        code = f"{self.if_block.generate(self.indent)}"
        for elsif in self.elsif:
            code += f" {elsif.generate(self.indent)}"
        if self.else_block != "":
            code += f" {self.else_block.generate(self.indent)}"
        return code

    def iterate(self) -> list:
        result = self.if_block.iterate()
        if self.elsif != "":
            result.extend(self.elsif.iterate())
        if self.else_block != "":
            result.extend(self.else_block.iterate())
        return result


class NodeCycleStatement(Node):
    def __init__(self, condition, block, indent):
        self.indent = indent
        self.condition = condition
        self.block = block

    def iterate(self) -> list:
        result = self.condition.iterate()
        result.extend(self.block.iterate())
        return result


class NodeWhileBlock(NodeCycleStatement):
    def generate(self):
        indent_str = get_indent(self.indent)
        return f"while ({self.condition.generate()}) {indent_str}{{\n{self.block.generate(self.indent + 1)}{indent_str}}}"


class NodeUntilBlock(NodeCycleStatement):
    def generate(self):
        indent_str = get_indent(self.indent)
        return f"while !({self.condition.generate()}) {indent_str}{{\n{self.block.generate(self.indent + 1)}{indent_str}}}"


class NodeForBlock(Node):
    def __init__(self, it, iterable, block, indent):
        self.indent = indent
        self.iter = it
        self.iterable = iterable
        self.block = block

    def generate(self):
        indent_str = get_indent(self.indent)
        return f"for ({self.iter.generate()} in {self.iterable.generate()}) {{\n{self.block.generate(self.indent)}{indent_str}}}"

    def iterate(self) -> list:
        result = self.iterable.iterate()
        result.extend(self.block.iterate())
        return result


class NodeUnaryOp(Node):
    def __init__(self, right):
        self.right = right

    def iterate(self) -> list:
        return self.right.iterate()


class NodeUnaryMinus(NodeUnaryOp):
    def generate(self):
        return f"-{self.right.generate()}"


class NodeUnaryPlus(NodeUnaryOp):
    def generate(self):
        return f"+{self.right.generate()}"


class NodeNot(NodeUnaryOp, NodeLogical):
    def generate(self):
        return f"!{self.right.generate()}"


class NodeArgs(Node):
    def __init__(self, arguments):
        self.arguments = arguments

    def generate(self):
        return f"{', '.join([a.generate() for a in self.arguments])}"

    def iterate(self) -> list:
        result = []
        for argument in self.arguments:
            result.extend(argument.iterate())
        return result


class NodeParams(Node):
    def __init__(self, params):
        self.params = params

    def generate(self):
        if isinstance(self.params, list):
            out = [p.generate() for p in self.params]
            return "" if len(out) == 0 else ", ".join(out)
        return self.params.generate()

    def iterate(self) -> list:
        result = []
        for param in self.params:
            result.extend(param.iterate())
        return result


class NodeDeclareParams(NodeParams):
    pass


class NodeActualParams(NodeParams):
    pass


class NodeFunc(Node):
    def __init__(self, id, params):
        self.id = id
        self.params = params


class NodeFuncDec(NodeFunc):
    def __init__(self, id, params, block, indent: int):
        super().__init__(id, params)
        self.block = block
        self.indent = indent

    def generate(self):
        indent_str = get_indent(self.indent)
        return f"{self.id} <- function({self.params.generate()}) {{\n{self.block.generate(self.indent + 1)}{indent_str}}}"

    def iterate(self) -> list:
        return self.block.iterate()


class NodeFuncCall(NodeFunc):
    def __init__(self, id, params, predefined_construction=None):
        super().__init__(id, params)
        self.predefined_construction = predefined_construction

    def generate(self):
        if self.predefined_construction:
            return self.predefined_construction.format(name=id, args=self.params.generate())
        return f"{self.id}({self.params.generate()})"

    def iterate(self) -> list:
        return [self] + self.params.iterate()


class NodeReturn(Node):
    def __init__(self, value: Node = None):
        self.value: Node = value

    def generate(self):
        return f"return{' ' + self.value.generate() if self.value is not None else ''}"

    def iterate(self) -> list:
        return self.value.iterate() if self.value is not None else super().iterate()


class NodeArray(Node):
    def __init__(self, args=None):
        self.args = args

    def generate(self):
        return f"c({str(self.args)})" if self.args is not None else "c()"

    def iterate(self) -> list:
        return self.args.iterate() if self.args is not None else super().iterate()


class NodeArrayCall(Node):
    def __init__(self, id, args: list):
        self.id = id
        self.args = args

    def generate(self):
        args_str = "".join([f"[{a.generate()}]" for a in self.args])
        return f"{self.id}{args_str}"

    def iterate(self) -> list:
        result = list()
        for a in self.args:
            result.extend(a.iterate())
        return result


class NodeNext(Node):
    def generate(self):
        return "next"


class NodeBreak(Node):
    def generate(self):
        return "break"
