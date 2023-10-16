from rex.symbols import Special


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
                res += '|\t' * level
                res += "|+-"
                res += el.__repr__(level + 1)
            res += "\n"
        else:
            for attr_name in attrs:
                res += '|\t' * level
                res += "|+-"
                if isinstance(attrs[attr_name], Special):
                    res += f"{attr_name}: {attrs[attr_name]}"
                elif isinstance(attrs[attr_name], list):
                    attr_count = len(attrs[attr_name])
                    res += f"{attr_name}:"
                    if attr_count > 0:
                        res += "\n"
                        res += '|\t' * level
                    res += "["
                    if attr_count > 0:
                        res += "\n"
                    for el in attrs[attr_name]:
                        res += '|\t' * (level + 1)
                        res += el.__repr__(level + 1) if (isinstance(el, Node)) else el.__repr__()
                    res = res.rstrip('\n')
                    if attr_count > 0:
                        res += "\n"
                        res += '|\t' * level
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
            code += f"{i.generate()}\n"
        return code


class NodeBlock(Node):
    def __init__(self, children, indent: int):
        self.children = children
        self.indent = indent

    def generate(self, indent=0):
        code = ""
        indent_str = get_indent(self.indent if indent == 0 else indent)
        if isinstance(self.children, list):
            for i in self.children:
                code += f"{indent_str}{i.generate()}\n"
        else:
            code += f"{self.children.generate(indent)}"
        return code


class NodeNewLine(Node):
    def generate(self):
        return ""


class NodeStatement(Node):
    def __init__(self, statement):
        self.statement = statement

    def generate(self):
        return self.statement.generate() + "\n"


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
    def generate(self):
        return f'"{self.value}"'


class NodeVariable(Node):
    def __init__(self, id):
        self.id = id

    def generate(self):
        return str(self.id)


class NodePar(Node):
    def __init__(self, expr):
        self.expr = expr

    def generate(self):
        return f"({self.expr.generate()})"


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
        return f"{self.left.generate()} ** {self.right.generate()}"


class NodeGreater(NodeBinOperator):
    def generate(self):
        return f"{self.left.generate()} > {self.right.generate()}"


class NodeGreaterEqual(NodeBinOperator):
    def generate(self):
        return f"{self.left.generate()} >= {self.right.generate()}"


class NodeLess(NodeBinOperator):
    def generate(self):
        return f"{self.left.generate()} < {self.right.generate()}"


class NodeLessEqual(NodeBinOperator):
    def generate(self):
        return f"{self.left.generate()} <= {self.right.generate()}"


class NodeCompEqual(NodeBinOperator):
    def generate(self):
        return f"{self.left.generate()} == {self.right.generate()}"


class NodeNotEqual(NodeBinOperator):
    def generate(self):
        return f"{self.left.generate()} != {self.right.generate()}"


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
        return f"{self.left.generate()}<- {self.left.generate()} - {self.right.generate()}"


class NodeAsteriskEquals(NodeBinOperator):
    def generate(self):
        return f"{self.left.generate()}<- {self.left.generate()} * {self.right.generate()}"


class NodeSlashEquals(NodeBinOperator):
    def generate(self):
        return f"{self.left.generate()}<- {self.left.generate()} / {self.right.generate()}"


class NodeModEquals(NodeBinOperator):
    def generate(self):
        return f"{self.left.generate()}<- {self.left.generate()} % {self.right.generate()}"


class NodeDegreeEquals(NodeBinOperator):
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

    def generate(self, indent=0):
        indent_str = get_indent(indent)
        return f"if ({self.condition.generate()}) {{\n{self.block.generate(indent+1)}{indent_str}}}"


class NodeElsIfStatement(NodeIfStatement):
    def generate(self, indent=0):
        indent_str = get_indent(indent)
        return f"else if ({self.condition.generate()}) {{\n{self.block.generate(indent+1)}{indent_str}}}"


class NodeElseStatement(NodeBlock):
    def generate(self, indent=0):
        indent_str = get_indent(indent)
        return f"else {{\n{super().generate(indent+1)}{indent_str}}}"


class NodeIfBlock(Node):
    def __init__(self, if_block, indent: int, elsif=None, else_block=None):
        self.indent = indent
        self.if_block = if_block
        self.elsif = elsif if elsif is not None else ""
        self.else_block = else_block if else_block is not None else ""

    def generate(self):
        indent_str = get_indent(self.indent)
        code = f"{self.if_block.generate(self.indent)}"
        for elsif in self.elsif:
            code += f" {elsif.generate(self.indent)}"
        if self.else_block != "":
            code += f" {self.else_block.generate(self.indent)}"
        return code


class NodeCycleStatement(Node):
    def __init__(self, condition, block, indent):
        self.condition = condition
        self.block = block
        self.indent = indent


class NodeWhileBlock(NodeCycleStatement):
    def generate(self):
        indent_str = get_indent(self.indent)
        return f"while ({self.condition.generate()})\n{indent_str}{{\n{self.block.generate(self.indent + 1)}{indent_str}}}"


class NodeUntilBlock(NodeCycleStatement):
    def generate(self):
        indent_str = get_indent(self.indent)
        return f"while !({self.condition.generate()})\n{indent_str}{{\n{self.block.generate(self.indent + 1)}{indent_str}}}"


class NodeForBlock(Node):
    def __init__(self, it, iterable, block, indent):
        self.iter = it
        self.iterable = iterable
        self.block = block
        self.indent = indent

    def generate(self):
        indent_str = get_indent(self.indent)
        return f"for ({self.iter.generate()} in {self.iterable.generate}){{\n{self.block.generate(self.indent)}{indent_str}}}"


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

    def generate(self):
        return f"{', '.join([a.generate() for a in self.arguments])}"


class NodeParams(Node):
    def __init__(self, params):
        self.params = params

    def generate(self):
        if isinstance(self.params, list):
            out = [p.generate() for p in self.params]
            return "" if len(out) == 0 else out
        return self.params.generate()


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


class NodeFuncCall(NodeFunc):
    def generate(self):
        return f"{self.id}({self.params.generate()})"


class NodeReturn(Node):
    def __init__(self, value):
        self.value = value

    def generate(self):
        return f"return {self.value.generate()}"


class NodeArray(Node):
    def __init__(self, args):
        self.args = args

    def generate(self):
        return str(self.args)


class NodeArrayCall(Node):
    def __init__(self, id, args):
        self.id = id
        self.args = args

    def generate(self):
        return f"{self.id}{self.args}"


class NodeNext(Node):
    def generate(self):
        return "next"


class NodeBreak(Node):
    def generate(self):
        return "break"


class NodeNot(Node):
    def __init__(self, expression):
        self.expression = expression

    def generate(self):
        return f"!{self.expression.generate()}"


class NodeAnd(NodeBinOperator):
    def generate(self):
        return f"{self.left.generate()} & {self.right.generate()}"


class NodeOr(NodeBinOperator):
    def generate(self):
        return f"{self.left.generate()} | {self.right.generate()}"