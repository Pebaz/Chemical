
class it:
    traits = {}

    def __init__(self, items):
        self.items = iter(items)

    def __getattr__(self, name):
        print(name)
        clazz = it.traits[name]
        def wrap(*args, **kwargs):
            nonlocal clazz
            return clazz(self.items, *args, **kwargs)
        return wrap

    def __iter__(self):
        return self

    def __next__(self):
        return next(self.items)

    # def skip(self, times):
    #     # skip = it(i for i in self)
    #     # for _ in range(times):
    #     #     next(skip)
    #     # return skip
    #     return Skip(self.items, times)

    def take(self, num_items):
        return it(next(self.items) for i in range(num_items))

    def nth(self, num):
        for _ in range(num):
            item = next(self.items)
        if num > 0:
            return item

    def last(self):
        for item in self.items: ...
        return item

    def all(self, func):
        return all(func(i) for i in self.items)

    def product(self):
        def mul(state, x):
            state *= x
            return state
        return Scan(self.items, 1, mul).last()

    def scan(self, seed, closure):
        return Scan(self.items, seed, closure)

    def step_by(self, step):
        return Step(self.items, step)

    def collect(self, into=list):
        return into(self)

    def step(self, times):
        return Step(self.items, times)


def trait(bind=None):
    def inner(*args, **kwargs):
        nonlocal bind
        return bind(*args, **kwargs)
    def wrapper(clazz):
        nonlocal bind
        it.traits[bind] = clazz
        return clazz
    if isinstance(bind, str):
        return wrapper
    else:
        it.traits[bind.__name__] = bind
        return inner


class Step(it):
    def __init__(self, items, step):
        it.__init__(self, items)
        self.step = step

    def __next__(self):
        nxt = next(self.items)
        try:
            for _ in range(self.step - 1):
                next(self.items)
        except StopIteration:
            pass
        return nxt


@trait('skip_it')
class Skip(it):
    def __init__(self, items, times):
        it.__init__(self, items)
        self.times = times
        for _ in range(times):
            next(self)

print(it.traits)

class Scan(it):
    def __init__(self, items, seed, closure):
        it.__init__(self, items)
        self.seed = seed
        self.closure = closure

    def __next__(self):
        return self.closure(self.seed, next(self.items))


# for class_ in list(globals().values()):
#     if isinstance(class_, type) and issubclass(class_, it):
#         if class_ == it: continue

#         def wrapper(clazz):
#             def inner(*args, **kwargs):
#                 nonlocal clazz
#                 return clazz(*args, **kwargs)
#             return inner

#         setattr(it, class_.__name__.lower(), wrapper(class_))


# Allow people to write custom additions that can introspect themselves
# onto the it class
