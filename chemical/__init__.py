
class it:
    """
    You can extend `it` with methods that produce iterators and methods that
    produce a value. Decorate a class or a function with `trait` respectively to
    get this to work.
    """
    traits = {}

    def __init__(self, items):
        self.items = iter(items)

    def __iter__(self):
        return self

    def __next__(self):
        return next(self.items)

    def __dir__(self):
        from itertools import chain
        return sorted(set(chain(self.__dict__.keys(), self.traits.keys())))

    def __getattr__(self, name):
        clazz = it.traits[name]
        def wrap(*args, **kwargs):
            nonlocal clazz
            return clazz(self, *args, **kwargs)
        return wrap


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

    it.traits[bind.__name__.lower()] = bind
    return inner


@trait('step_by')
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


@trait
def all(self, func):
    return all(func(i) for i in self.items)


@trait
class Skip(it):
    def __init__(self, items, times):
        it.__init__(self, items)
        self.times = times
        for _ in range(times):
            next(self)


@trait
class Collect(it):
    def __init__(self, items, into=list):
        return into(items)


@trait
def nth(self, num):
    item = None
    for _ in range(num):
        item = next(self)
    return item


@trait
def count(self):
    return len(list(self))


@trait
def collect(self, into=list):
    return into(self)


@trait
def last(self):
    item = None
    for i in self:
        item = i
    return item


@trait
def take(self, num_items):
    return it(next(self) for i in range(num_items))

