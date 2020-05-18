from chemical import it

s = '123456'
print(s)
print(it(s).rev())
print(it(s).rev().collect(str))
print(it(s).rev().rev().collect(str))
print(it(s).skip(1).collect(str))
print(it(s).rev().skip(1).collect(str))  # '54321'

