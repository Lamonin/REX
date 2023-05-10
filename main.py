from rex import Rex


f = open('sample_1.rb')

rex = Rex(f.read())

f.close()

while rex.next_token():
    print(rex.lexem)

