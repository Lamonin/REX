# Переменные
name <- "John"
age <- 30

# Условие
if (age >= 18) {
	print(name + " is an adult")
} else {
	print(name + " is underage")
}

# Цикл while
i <- 0
while (i < 5) {
	print(i)
	i <- i + 1
}

# Цикл until
j <- 5
while !(j == 0) {
	print(j)
	j <- j - 1
}

# Цикл for
for (k in 0:5) {
	print(k)
}

# Функция
print_name <- function(n) {
	print("Hello, #{n}!")
}

print_name(name)

# Ввод данных
print("Hi #{input_name}!")
