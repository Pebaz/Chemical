from chemical import it

'''
print(it)

for i in it(range(10)).take(3).skip(2):
    print(i)

a = 10, 9, 8, 7, 6, 5, 4, 3, 2, 1

print(it(a).all(lambda x: x > 2))


print(it(a).skip(6).all(lambda x: x < 5))

print(list(it(a).skip(6)))

# def mul(state, x):
#     print(state, x)
#     state[0] = state[0] * x
#     return state[0]

# print(list(it([1, 2, 3, 4]).scan(1, mul)))

print(it([1, 2, 3]).product())

print(it([1, 2, 3, 4, 5]).nth(1))

print(list(it(range(10)).step_by(3).skip(1).take(2)))
'''

for i in it(range(10)).step_by(2).collect(list):
    print(i)

print(it(range(10)).step_by(2).collect(lambda items: {i : i for i in items}))
print(it(range(10)).step_by(2).skip(1).collect())
