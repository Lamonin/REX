from rex.nodes import *


class DataBlock:
    def __init__(self):
        self.functions: dict[str, NodeFunc] = dict()
        self.variables: dict[str, Node] = dict()

    def add_func(self, func_id, func_node: NodeFunc):
        self.functions[func_id] = func_node

    def is_func_exist(self, func_id):
        return func_id in self.functions

    def add_var(self, var_id, value: Node):
        self.variables[var_id] = value

    def is_var_exist(self, var_id):
        return var_id in self.variables


class SymTable:
    def __init__(self):
        self.data_blocks: list[DataBlock] = list()
        self.table = {
            "puts": (type(NodeFunc), None)
        }

        # Define global names
        gdb = DataBlock()
        gdb.add_func("puts", NodeFunc("puts", list()))
        self.data_blocks.append(gdb)

    def create_local_data_block(self):
        self.data_blocks.append(DataBlock())

    def dispose_local_data_block(self, pos):
        if len(self.data_blocks) > 1:
            self.data_blocks.pop()
        else:
            self.error("Попытка уничтожить глобальное пространство переменных!", pos)

    def add_func(self, func_id, func_node: NodeFunc, pos):
        if self.data_blocks[-1].is_func_exist(func_id):
            self.error(f"Функция {func_id} уже была объявлена!", pos)
        self.data_blocks[-1].add_func(func_id, func_node)

    def is_func_exist(self, func_id, pos, with_error=False):
        for db in reversed(self.data_blocks):
            res = db.is_func_exist(func_id)
            if res:
                return True
        if with_error:
            self.error(f"Функция с именем {func_id} не была объявлена!", pos)
        return False

    def add_var(self, var_id, value: Node):
        self.data_blocks[-1].add_var(var_id, value)

    def is_var_exist(self, var_id, pos, with_error=False):
        for db in reversed(self.data_blocks):
            res = db.is_var_exist(var_id)
            if res:
                return True
        if with_error:
            self.error(f"Символа с именем {var_id} не существует!", pos)
        return False

    def error(self, msg: str, pos):
        raise Exception(f'Ошибка семантического анализа ({pos[0]}, {pos[1]}): {msg}')
