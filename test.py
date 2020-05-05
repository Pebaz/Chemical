from chemical import it

print(it)

for i in it(range(10)).take(3).skip(2):
    print(i)

a = 10, 9, 8, 7, 6, 5, 4, 3, 2, 1

print(it(a).all(lambda x: x > 2))


print(it(a).skip(6).all(lambda x: x < 5))

print(list(it(a).skip(6)))
