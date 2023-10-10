from rex import Rex
from parser import Parser
from translator import Translator


f = open('samples/sample_2.rb')
code = f.read()
f.close()

# tr = Translator()
# print(tr.parse(code))

rex = Rex()
rex.setup(code)

p = Parser(rex)
parse_res = p.parse()
print(parse_res)
print(parse_res.generate())


# while rex.next_token():
#     print(rex.lexem)
# print(rex.lexem)
