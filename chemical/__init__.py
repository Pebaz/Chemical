
class ChemicalException(Exception):
    "Base class for all Chemical Exceptions"


class TraitException(ChemicalException):
    "Any error having to do with traits"


class it:
    """
    You can extend `it` with methods that produce iterators and methods that
    produce a value. Decorate a class or a function with `trait` respectively to
    get this to work.
    """
    traits = {}

    def __init__(self, items=[], reverse_seed=None):
        if reverse_seed:
            self.reverse = reverse_seed
        else:
            self.reverse = (
                items.reverse if isinstance(items, it)
                else self._get_reverse(items)
            )
        self.items = iter(items)

    def __str__(self):
        return f'<{self.__class__.__name__} object at {hex(id(self))}>'

    def __iter__(self):
        return self

    def __reversed__(self):
        if not self.reverse:
            raise ChemicalException('Underlying collection cannot be reversed.')
        return it(self.reverse, self.items)

    def __next__(self):
        return next(self.items)

    def __dir__(self):
        from itertools import chain
        keys = set(self.__dict__.keys()) ^ {'items'}
        return sorted(set(chain(keys, self.traits.keys())))

    def __getattr__(self, name):
        if name not in it.traits:
            raise TraitException(
                f'Trait or extension method "{name}" not found for {self}.'
            )

        clazz = it.traits[name]

        class wrap:
            __doc__ = clazz.__doc__

            def __init__(self, items, clazz, name):
                self.items = items
                self.clazz = clazz
                self.name = name

            def __repr__(self):
                hid = hex(id(self.clazz))
                return f'<{self.__module__}.it.{self.name} at {hid}>'

            def __call__(self, *args, **kwargs):
                return self.clazz(self.items, *args, **kwargs)

        return wrap(self, clazz, name)

    def _get_reverse(self, obj):
        "Convenience method to get reversed version of object or None."
        try:
            return reversed(obj)
        except TypeError:
            return None

    def next(self):
        return next(self)

    def rev(self):
        return reversed(self)


def trait(bind=None):
    def inner(*args, **kwargs):
        nonlocal bind
        return bind(*args, **kwargs)

    def wrapper(clazz):
        __doc__ = clazz.__doc__
        nonlocal bind
        it.traits[bind] = clazz
        return clazz

    if isinstance(bind, str):
        return wrapper

    it.traits[bind.__name__.lower()] = bind
    inner.__doc__ = bind.__doc__
    return inner


@trait
class Skip(it):
    """
    Lazily skip a number of items in the iterator chain.
    """

    def __init__(self, items, times):
        it.__init__(self, items)
        self.times = times
        assert times > 0, 'skip: number of items to skip must be > 0'
    
    def __next__(self):
        while self.times > 0:
            next(self.items)
            next(self.reverse)
            self.times -= 1

        return next(self.items)

    def __reversed__(self):
        """
        Although subtle, it is important that `next(self.items)` is called the
        same amount of times as `self.reverse`.
        """
        last_item = [next(self.items) for _ in range(self.times)]

        if last_item:
            last_item = last_item[-1]
        else:
            raise StopIteration('skip: reversing collection yields no elements')

        return (it(self.reverse, self.items)
            .take_while(lambda x: id(x) != id(last_item))
        )


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
class Filter(it):
    """
    Filters out elements of the iterator based on the provided lambda.

        :::python

        print('hi')
        for i in range(10):
            "Does something"
            print(i)

    As you can see, this is a code example.
    """

    def __init__(self, items, filter_func=lambda x: bool(x)):
        it.__init__(self, items)
        self.filter_func = filter_func

    def __next__(self):
        while res := next(self.items):
            if self.filter_func(res):
                return res


trait('all')(lambda self, func: all(func(i) for i in self))
trait('any')(lambda self, func: any(func(i) for i in self))

@trait
def collect(self, into=list):
    if into == str:
        return ''.join(str(i) for i in self)
    else:
        return into(self)


@trait
def nth(self, num):
    return self.take(num).last()


# `it.__len__` can never exist because list(), etc. try to use it, consuming it.
trait('count')(lambda self: len(list(self)))


@trait
def last(self):
    item = None
    for i in self:
        item = i
    return item


@trait
def take(self, num_items):
    return it(
        (next(self) for i in range(num_items)),
        (next(self.reverse) for i in range(num_items))
    )


# @trait
# class Take(it):
#     def __init__(self, items, num_items):
#         it.__init__(self, items)
#         self.num_items = num_items

#     def __next__(self):
#         if self.num_items > 0:
#             self.num_items -= 1
#             return next(self.items)
#         else:
#             raise StopIteration()

#     def __reversed__(self):
#         return it(
#             (next(self.reverse) for i in range(self.num_items)),
#             (next(self) for i in range(self.num_items))
#         )


@trait
def take_while(self, closure):
    take_while_ = it(i for i in self if closure(i))
    take_while_.reverse = it(i for i in self.reverse if closure(i))
    return take_while_


@trait
class Peekable(it):
    def __init__(self, items):
        it.__init__(self, items)
        self.ahead = None
        self.done = False

    def peek(self):
        if self.done:
            raise StopIteration()
        if not self.ahead:
            self.ahead = next(self.items)
        return self.ahead

    def __next__(self):
        if self.done:
            raise StopIteration()

        try:
            if not self.ahead:
                self.ahead = next(self.items)
        except StopIteration:
            ...

        ret = self.ahead
        try:
            self.ahead = next(self.items)
        except StopIteration:
            self.done = True
            return ret

        return ret


trait('max')(lambda self: max(self))
trait('min')(lambda self: min(self))

@trait
def max_by_key(self, closure):
    max_val = self.next()
    max_cmp = closure(max_val)
    for i in self:
        comp = closure(i)
        if comp > max_cmp:
            max_val = i
            max_cmp = comp
    return max_val


@trait
def min_by_key(self, closure):
    min_val = self.next()
    min_cmp = closure(min_val)
    for i in self:
        comp = closure(i)
        if comp < min_cmp:
            min_val = i
            min_cmp = comp
    return min_val


from itertools import chain, cycle

trait('chain')(lambda self, collection: it(chain(self, collection)))

#trait('cycle')(lambda self: it(cycle(self)))
@trait('cycle')
def cycle_it(self):
    cycle_ = it(cycle(self))
    cycle_.reverse = it(cycle(self.reverse))
    return cycle_

trait('map')(lambda self, closure: it(map(closure, self)))
trait('sum')(lambda self: sum(self))
trait('enumerate')(lambda self: it(enumerate(self)))


@trait
def go(self):
    for i in self: ...


@trait
class Inspect(it):
    def __init__(self, items, func):
        it.__init__(self, items)
        self.func = func

    def __next__(self):
        item = next(self.items)
        self.func(item)
        return item


trait('zip')(lambda self, other: it(zip(self, other)))

@trait
def unzip(self):
    left, right = [], []
    try:
        for l, r in self:
            left.append(l); right.append(r)
    except ValueError as e:
        raise ChemicalException(
            'unzip: left and right hand sides are unbalanced'
        ).with_traceback(e.__traceback__) from e
    return left, right


@trait
def skip_while(self, closure):
    ahead = self.peekable()

    while closure(ahead.peek()):
        ahead.next()

    return it(ahead)


from enum import Enum, auto

class Ordering(Enum):
    Equal = auto()
    Less = auto()
    Greater = auto()


@trait
def cmp(self, other):
    a, b = self.count(), it(other).count()
    if a == b: return Ordering.Equal
    elif a < b: return Ordering.Less
    elif a > b: return Ordering.Greater


trait('gt')(lambda self, other: self.cmp(other) == Ordering.Greater)
trait('ge')(
    lambda self, other: self.cmp(other) in (Ordering.Greater, Ordering.Equal)
)
trait('lt')(lambda self, other: self.cmp(other) == Ordering.Less)
trait('le')(
    lambda self, other: self.cmp(other) in (Ordering.Less, Ordering.Equal)
)


@trait
def eq_by(self, other, closure):
    other = it(other)

    while True:
        try:
            a = next(self)
        except StopIteration:
            a = StopIteration

        try:
            b = next(other)
        except StopIteration:
            b = StopIteration

        if a == StopIteration and b == StopIteration:
            return True

        elif (a, b) == (StopIteration, b) or (a, b) == (a, StopIteration):
            return False

        elif not closure(a, b):
            return False


trait('eq')(lambda self, other: self.eq_by(other, lambda a, b: a == b))
trait('neq')(lambda self, other: not self.eq(other))


@trait
def find(self, closure):
    try:
        return self.filter(closure).next()
    except StopIteration as e:
        ...
    raise ChemicalException(
        'find: item matching provided lambda could not be found'
    )


@trait
def position(self, closure):
    for i, element in self.enumerate():
        if closure(element):
            return i
    raise ChemicalException(
        'position: item matching provided lambda is not in collection'
    )


@trait
def partition(self, closure):
    """
    This is a code example:

    ```
    asdf.asdf()
    ```
    """
    parts = [], []
    for i in self:
        parts[int(not closure(i))].append(i)
    return parts


@trait
def flatten(self):
    links = it()
    for i in self:
        try:
            iter(i)
            links = links.chain(i)
        except TypeError:
            links = links.chain([i])
    return links

