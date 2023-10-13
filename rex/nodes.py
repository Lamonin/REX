from rex.symbols import Special


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
            code += f"{i.generate()}"
        return code


class NodeBlock(Node):
    def __init__(self, children):
        self.children = children

    def generate(self, indent=0):
        code = ""
        indent_str = ""
        for i in range(indent):
            indent_str += "\t"
        for i in self.children:
            code += f"{indent_str}{i.generate()}"
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

    def generate(self):
        return f"{', '.join([a.generate() for a in self.arguments])}"


class NodeParams(Node):
    def __init__(self, params):
        self.params = params

    def generate(self):
        return ", ".join([str(p) for p in self.params])


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

    def generate(self):
        return f"def {self.id}({self.params.generate()})\n{self.block.generate(indent=1)}end\n"


class NodeFuncCall(NodeFunc):
    def generate(self):
        return f"{self.id}({self.params.generate()})\n"


class NodeReturn(Node):
    def __init__(self, value):
        self.value = value

    def generate(self):
        return f"return {self.value.generate()}\n"


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
        return "next\n"


class NodeBreak(Node):
    def generate(self):
        return "break\n"


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
