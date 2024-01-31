from typing import Callable

from rex.misc import get_args_name_from_count
from rex.nodes import NodeFuncCall, NodeVariable, NodeArray
from rex.types import *


class SemanticError(Exception):
    pass


class NameSpace:
    def __init__(self):
        self.variables: dict[str, Variable] = dict()
        self.functions: dict[str, Function] = dict()

    def add_variable(self, name: str, value: Variable):
        if name in self.variables:
            value.number_of_uses = self.variables[name].number_of_uses
            value.number_of_uses.new_order()
        self.variables[name] = value

    def add_function(self, name: str, value: Function):
        if name in self.functions:
            value.number_of_uses = self.functions[name].number_of_uses
            value.number_of_uses.new_order()
        self.functions[name] = value


class SymTable:
    get_pos: Callable[[], tuple[int, int]]

    def __init__(self):
        self.name_spaces: list[NameSpace] = list()
        self.get_pos = lambda: (0, 0)

        # Define global name space
        gns = NameSpace()
        gns.add_function(
            "puts",
            PredefinedFunction(
                predefined_construction="print({args})",
            ),
        )
        gns.add_function(
            "readline",
            PredefinedFunction(
                predefined_construction="readline()",
                args_count=1,
            ),
        )

        self.name_spaces.append(gns)

    def create_local_namespace(self):
        self.name_spaces.append(NameSpace())

    def dispose_local_namespace(self):
        if len(self.name_spaces) <= 1:
            self.error("Попытка уничтожить глобальное пространство имен.")
        self.name_spaces.pop()

    def add_variable(self, name: str, value: Variable):
        self.name_spaces[-1].add_variable(name, value)

    def add_function(self, name: str, value: Function):
        self.name_spaces[-1].add_function(name, value)

    def compare_variable_type(self, var_name: str, var_type: type(SemanticType)) -> bool:
        return isinstance(self.get_variable(var_name), var_type)

    def variable_exist(self, name: str) -> bool:
        for ns in reversed(self.name_spaces):
            if name in ns.variables:
                return True
        return False

    def get_variable(self, name: str) -> Variable | None:
        self.check_variable_presence(name)
        for ns in reversed(self.name_spaces):
            if name in ns.variables:
                return ns.variables[name]
        return None

    def get_function(self, name: str) -> Function | None:
        self.check_function_presence(name)
        for ns in reversed(self.name_spaces):
            if name in ns.functions:
                return ns.functions[name]
        return None

    def get_by_node_type(self, node):
        if isinstance(node, NodeFuncCall):
            return self.get_function(node.id)
        elif isinstance(node, NodeVariable):
            return self.get_variable(node.id)
        return None

    def function_exist(self, name: str) -> bool:
        for ns in reversed(self.name_spaces):
            if name in ns.functions:
                return True
        return False

    def check_variable_presence(self, name: str):
        if not self.variable_exist(name):
            self.error(f"Переменная {name} не объявлена.")

    def check_function_presence(self, name: str):
        if not self.function_exist(name):
            self.error(f"Функция {name} не объявлена.")

    def check_variable_is_array(self, name):
        if not self.compare_variable_type(name, Auto) and not self.compare_variable_type(name, Array):
            self.error(f"Переменная {name} не является массивом.")

    def check_function_arguments_count(self, name: str, args_count: int):
        f = self.get_function(name)
        if f.args_count != -1 and f.args_count != args_count:
            self.error(
                f"Функция {name} принимает {f.args_count} {get_args_name_from_count(f.args_count)}, а не {args_count}"
            )

    def error(self, msg: str):
        raise SemanticError(
            f"Ошибка семантического анализа ({self.get_pos()[0]}, {self.get_pos()[1]}): {msg}"
        )
