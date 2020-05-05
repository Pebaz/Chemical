

class it:
    def __init__(self, items):
        self.items = iter(items)

    def __iter__(self):
        return self

    def __next__(self):
        return next(self.items)

    def skip(self, times):
        for _ in range(times):
            next(self.items)
        return self

    def take(self, num_items):
        return it(next(self.items) for i in range(num_items))

    def all(self, func):
        return all(func(i) for i in self.items)
