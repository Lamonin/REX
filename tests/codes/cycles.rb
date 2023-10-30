a = 0

while (true) do
    a += 1
    if a > 10 then
        break
    end
end

for i, j in 1..10 do
    puts(i, j)
end

until false
    a -= 1
    if a > 0 then
        next
    end
    break
end
