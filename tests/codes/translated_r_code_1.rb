# ����������
name <- "John"
age <- 30

# �������
if (age >= 18) {
	print(name + " is an adult")
} else {
	print(name + " is underage")
}

# ���� while
i <- 0
while (i < 5) {
	print(i)
	i <- i + 1
}

# ���� until
j <- 5
while !(j == 0) {
	print(j)
	j <- j - 1
}

# ���� for
for (k in 0:5) {
	print(k)
}

# �������
print_name <- function(n) {
	print("Hello, #{n}!")
}

print_name(name)

# ���� ������
print("Hi #{input_name}!")
