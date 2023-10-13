from rex.nodes import NodeFunc


class SymTable:
    def __init__(self):
        self.table = {
            "puts": (type(NodeFunc), None)
        }

    def Add(self, id: str, type, value, pos):
        if id in self.table:
            self.error(f"Символ с именем {id} уже существует!", pos)
        else:
            self.table[id] = (type, value)

    def Set(self, id, value, pos):
        if id not in self.table:
            self.error(f"Попытка присвоить значение {value} для несуществующего символа {id}!", pos)
        else:
            self.table[id] = (self.table[id][0], value)

    def Get(self, id, pos):
        if id not in self.table:
            self.error(f"Символа с именем {id} не существует!", pos)
        else:
            return self.table[id]

    def Exist(self, id):
        return id in self.table

    def error(self, msg: str, pos):
        raise Exception(f'Ошибка семантического анализа ({pos[0]}, {pos[1]}): {msg}')
