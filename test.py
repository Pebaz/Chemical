from chemical import it

print(it)

for i in it(range(10)).take(3).skip(2):
    print(i)
