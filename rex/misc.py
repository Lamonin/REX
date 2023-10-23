
def get_args_name_from_count(c):
    cc = c % 10
    if cc == 1:
        return "аргумент"
    elif 2 <= cc <= 4:
        return "аргумента"
    else:
        return "аргументов"
