class SemanticType:
    def __init__(self):
        self.number_of_uses = 0


class Variable(SemanticType):
    pass


class Array(Variable):
    pass


class Auto(Variable):
    pass


class Function(SemanticType):
    def __init__(self, args_count=0, return_type=None):
        super().__init__()
        self.args_count = args_count
        self.return_type = return_type


class PredefinedFunction(Function):
    def __init__(self, predefined_name, predefined_construction=None, args_count=-1):
        self.predefined_name = predefined_name
        self.predefined_construction = predefined_construction
        super().__init__(args_count=args_count)
