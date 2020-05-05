


class it:
    def __init__(self, items):
        self.items = iter(items)

    def __iter__(self):
        return self

    def __next__(self):
        return next(self.items)

    def skip(self, times):
        skip = it(i for i in self)
        for _ in range(times):
            next(skip)
        return skip

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


class Step(it):
    def __init__(self, items, step):
        it.__init__(self, items)
        self.step = step

    def __next__(self):
        nxt = next(self.items)
        print('->', nxt)
        try:
            for _ in range(self.step - 1):
                next(self.items)
        except StopIteration:
            pass
        return nxt


class Scan(it):
    def __init__(self, items, seed, closure):
        it.__init__(self, items)
        self.seed = seed
        self.closure = closure

    def __next__(self):
        return self.closure(self.seed, next(self.items))
