def find_missing(sequence)
  consecutive     = sequence.each_cons(2)
  differences     = consecutive.map { |a,b| b - a }
  sequence        = differences.max_by { |n| differences.count(n) }
  missing_between = consecutive.find { |a,b| (b - a) != sequence }
  missing_between.first + sequence
end
find_missing([2,4,6,10])

HELLO = "Hello, world!"

# Define a method
def self.say_hello
    puts HELLO
end

x = 5
if x > 10
  puts "x is greater than 10"
elsif x > 5
  puts "x is greater than 5 but less than or equal to 10"
else
  puts "x is less than or equal to 5"
end

my_array = [1, 2, 3, 4, 5]
puts my_array.sum