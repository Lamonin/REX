from rex import Rex


f = open('sample_2.rb')


rex = Rex()
rex.setup(f.read())

f.close()

while rex.next_token():
    print(rex.lexem)
print(rex.lexem)
