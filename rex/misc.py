from rex.nodes import Node, NodePar


def get_args_name_from_count(c):
    cc = c % 10
    if cc == 1:
        return "аргумент"
    elif 2 <= cc <= 4:
        return "аргумента"
    else:
        return "аргументов"


def get_node_without_par(node) -> Node:
    while isinstance(node, NodePar):
        node = node.expr
    return node


def try_to_num(value: str) -> (bool, int | float | None):
    try:
        return True, int(value)
    except ValueError:
        try:
            return True, float(value)
        except ValueError:
            return False, None


def convert_float_to_int(value: float) -> float | int:
    if isinstance(value, int):
        return value

    if value.is_integer():
        return int(value)
    else:
        return value
