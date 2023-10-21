class SemanticType:
    pass


class VariableType(SemanticType):
    pass


class ArrayType(VariableType):
    pass


class FunctionType(SemanticType):
    def __init__(self, args_count=0):
        self.args_count = args_count
