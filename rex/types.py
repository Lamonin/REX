class NumberOfUsesTable:
    def __init__(self):
        self.use_table = [0]

    def new_order(self):
        self.use_table.append(0)

    def get(self, order: int = 0):
        return self.use_table[-(order + 1)]

    def increase(self, order: int = 0):
        self.use_table[-(order + 1)] += 1

    def decrease(self, order: int = 0):
        self.use_table[-(order + 1)] -= 1

    def remove(self, order: int = 0):
        del self.use_table[-(order + 1)]


class SemanticType:
    def __init__(self):
        self.number_of_uses: NumberOfUsesTable = NumberOfUsesTable()


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
