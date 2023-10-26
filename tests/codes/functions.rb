def foo()
end

def bar()
    puts("Hello world")
    foo()
    a = 10 + 14
end

def sum(a, b)
    c = a + b
    return c
end

def one(a)
    puts(a)
    def puts(a, b, c)
        puts(a, b, c)
    end
    puts(a, 10, 20)
    sum(a, 10)
end

foo()
bar()
sum(one(10), one(20))
