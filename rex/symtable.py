from rex.types import *
from rex.nodes import *


class NameSpace:
    def __init__(self):
        self.variables: dict[str, VariableType] = dict()
        self.functions: dict[str, FunctionType] = dict()

    def add_variable(self, name: str, value: VariableType):
        self.variables[name] = value

    def add_function(self, name: str, value: FunctionType):
        self.functions[name] = value


class SymTable:
    def __init__(self):
        self.name_spaces: list[NameSpace] = list()

        # Define global name space
        gns = NameSpace()
        gns.add_function("puts", FunctionType(args_count=-1))

        self.name_spaces.append(gns)

    def create_local_name_space(self):
        self.name_spaces.append(NameSpace())

    def dispose_local_name_space(self, pos):
        if len(self.name_spaces) > 1:
            self.name_spaces.pop()
        else:
            self.error("Попытка уничтожить глобальное пространство имен!", pos)

    def add_variable(self, name: str, value: VariableType):
        self.name_spaces[-1].add_variable(name, value)

    def add_function(self, name: str, value: FunctionType):
        self.name_spaces[-1].add_function(name, value)

    def compare_variable_type(self, var_name: str, var_type: type(SemanticType)) -> bool:
        for ns in reversed(self.name_spaces):
            if var_name in ns.variables:
                return isinstance(ns.variables[var_name], var_type)
        return False

    def variable_exist(self, name: str) -> bool:
        for ns in reversed(self.name_spaces):
            if name in ns.variables:
                return True
        return False

    def get_function(self, name: str) -> FunctionType | None:
        for ns in reversed(self.name_spaces):
            if name in ns.functions:
                return ns.functions[name]
        return None

    def function_exist(self, name: str) -> bool:
        for ns in reversed(self.name_spaces):
            if name in ns.functions:
                return True
        return False

    def error(self, msg: str, pos):
        raise Exception(f'Ошибка семантического анализа ({pos[0]}, {pos[1]}): {msg}')
