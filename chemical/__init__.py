import sys, math
from enum import Enum, auto

class Ordering(Enum):
    Equal = auto()
    Less = auto()
    Greater = auto()


class ChemicalException(Exception):
    "Base class for all Chemical Exceptions"


class TraitException(ChemicalException):
    "Any error having to do with traits"


class NothingToPeek(ChemicalException):
    "Raised when a call to .peek() cannot yield another element"


class it:
    """
    You can extend `it` with methods that produce iterators and methods that
    produce a value. Decorate a class or a function with `trait` respectively to
    get this to work.
    """
    traits = {}

    def __init__(self, items=[], reverse_seed=None, bounds=[]):
        self._modified = False
        self.items = iter(items)

        if isinstance(items, it):
            self._lower_bound, self._upper_bound = bounds or items.size_hint()
            self.reverse = reverse_seed or items.reverse

        else:
            if bounds:
                self._lower_bound, self._upper_bound = bounds
            else:
                try:
                    self._lower_bound = len(items)
                    self._upper_bound = len(items)
                except TypeError:
                    self._lower_bound = 0
                    self._upper_bound = None
            try:
                self.reverse = reverse_seed or it(reversed(items))
            except TypeError:
                self.reverse = None

    def __copy__(self):
        from copy import copy
        return it(copy(self.items), copy(self.reverse))

    def __str__(self):
        return f'<{self.__class__.__name__} object at {hex(id(self))}>'

    def __iter__(self):
        return self

    def __reversed__(self):
        if self._modified:
            raise ChemicalException(
                'Cannot reverse an iterator that has already yielded at least '
                'one item with next()'
            )

        if not self.reverse:
            raise ChemicalException('Underlying collection cannot be reversed.')

        else:
            return self.__get_reversed__()

    def __get_reversed__(self):
        return it(self.reverse, self.items, self.size_hint())

    def __next__(self):
        self._modified = True
        return self.__get_next__()

    def __get_next__(self):
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

    def next(self):
        return next(self)

    def rev(self):
        return reversed(self)

    def size_hint(self):
        return self._lower_bound, self._upper_bound


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
        self._lower_bound = max(0, self._lower_bound - times)
        if self._upper_bound:
            self._upper_bound -= times
    
    def __get_next__(self):
        while self.times > 0:
            next(self.items)
            next(self.reverse)
            self.times -= 1

        return next(self.items)

    def __get_reversed__(self):
        """
        Although subtle, it is important that `next(self.items)` is called the
        same amount of times as `self.reverse`.
        """
        last_item = [next(self.items) for _ in range(self.times)]

        if last_item:
            last_item = last_item[-1]
        else:
            raise StopIteration('skip: reversing collection yields no elements')

        revv = it(
            self.reverse,
            self.items,
            self.size_hint()
        ).take_while(lambda x: id(x) != id(last_item))

        # NOTE(pebaz): Manually hide the size-hint that take_while provides
        return it(revv, bounds=self.size_hint())


@trait('step_by')
class Step(it):
    def __init__(self, items, step):
        it.__init__(self, items)
        self.step = step

        self._lower_bound = max(0, int(math.ceil(self._lower_bound / step)))
        if self._upper_bound:
            self._upper_bound = int(math.ceil(self._upper_bound / step))

    def __get_next__(self):
        nxt = next(self.items)
        try:
            for _ in range(self.step - 1):
                next(self.items)
        except StopIteration:
            pass
        return nxt

    def __get_reversed__(self):
        return it(Step(self.reverse, self.step), self.items, self.size_hint())


@trait
def filter(self, filter_func):
    """
    Filters out elements of the iterator based on the provided lambda.

        :::python

        print('hi')
        for i in range(10):
            "Does something"
            print(i)

    As you can see, this is a code example.
    """
    return it(
        (i for i in self if filter_func(i)),
        (i for i in self.reverse if filter_func(i)),
        (0, self._upper_bound)
    )


@trait('all')
def all_it(self, func):
    return all(func(i) for i in self)


@trait('any')
def any_it(self, func):
    return any(func(i) for i in self)


@trait
def collect(self, into=list):
    if into == str:
        return ''.join(str(i) for i in self)
    else:
        return into(self)


@trait
def nth(self, num):
    if num <= 0:
        raise ChemicalException('nth: to take the first item, use integer 1')
    for i in range(num):
        item = next(self)
    return item


@trait
def count(self):
    """
    """
    # NOTE(pebaz): `it.__len__` can never exist because list(), etc. would try
    # to use it, which would consume it.
    return len(list(self))


@trait
def last(self):
    item = None
    for i in self:
        item = i
    return item


@trait
def take(self, num_items):
    taken = [next(self) for i in range(num_items)]
    return it(iter(taken), reversed(taken), [num_items] * 2)

@trait
def take_while(self, closure):
    return it(
        (i for i in self if closure(i)),
        it(i for i in self.reverse if closure(i)),
        (0, self.size_hint()[1])
    )


@trait
class Peekable(it):
    def __init__(self, items):
        it.__init__(self, items)
        self.ahead = None
        self.done = False

    def peek(self):
        if self.done:
            raise NothingToPeek()

        if not self.ahead:
            try:
                self.ahead = next(self.items)
            except StopIteration as e:
                raise NothingToPeek().with_traceback(e.__traceback__) from e

        return self.ahead

    def __get_next__(self):
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


@trait('max')
def max_it(self):
    return max(self)


@trait('min')
def min_it(self):
    return min(self)



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


@trait('chain')
def chain_it(self, itr):
    from itertools import chain
    chained = it(itr)
    return it(
        chain(self, chained),
        chain(
            chained.rev() if isinstance(chained, it) else reversed(chained),
            self.rev()
        ),
        (
            self._lower_bound + chained._lower_bound,
            self._upper_bound + chained._upper_bound
        )
    )


@trait('cycle')
def cycle_it(self):
    from itertools import cycle
    return it(cycle(self), it(cycle(self.reverse)))


@trait('map')
def map_it(self, closure):
    return it(
        map(closure, self),
        map(closure, self.reverse),
        self.size_hint()
    )


@trait('sum')
def sum_it(self):
    return sum(self)


@trait('enumerate')
def enumerate_it(self):
    return it(enumerate(self), enumerate(self.reverse), self.size_hint())


@trait
def go(self):
    for i in self: ...


@trait
class Inspect(it):
    def __init__(self, items, func):
        it.__init__(self, items)
        self.func = func

    def __get_next__(self):
        item = next(self.items)
        self.func(item)
        return item

    def __get_reversed__(self):
        return it(
            Inspect(self.reverse, self.func), self.items, self.size_hint()
        )


@trait('zip')
def zip_it(self, other):
    other_it = it(other)
    return it(
        zip(self, other_it),
        zip(self.reverse, reversed(other_it)),
        (
            self._lower_bound + other_it._lower_bound,
            self._upper_bound + other_it._upper_bound
        )
    )


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

    try:
        while closure(ahead.peek()):
            ahead.next()
    except NothingToPeek:
        "Don't crash on account of this"

    behind = self.reverse.peekable()

    try:
        while closure(behind.peek()):
            behind.next()
    except NothingToPeek:
        "Don't crash on account of this"

    return it(ahead, behind, (0, self._upper_bound))


@trait
def cmp(self, other):
    a, b = self.count(), it(other).count()
    if a == b: return Ordering.Equal
    elif a < b: return Ordering.Less
    elif a > b: return Ordering.Greater



@trait
def gt(self, other):
    return self.cmp(other) == Ordering.Greater


@trait
def ge(self, other):
    return self.cmp(other) in (Ordering.Greater, Ordering.Equal)


@trait
def lt(self, other):
    return self.cmp(other) == Ordering.Less


@trait
def le(self, other):
    return self.cmp(other) in (Ordering.Less, Ordering.Equal)



@trait
def cmp_by(self, other, closure):
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


@trait
def eq(self, other):
    return self.cmp_by(other, lambda a, b: a == b)


@trait
def neq(self, other):
    return not self.eq(other)


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


@trait
def for_each(self, closure):
    return it(
        (closure(i) for i in self),
        (closure(i) for i in self.reverse),
        self.size_hint()
    )


@trait
def is_sorted(self):
    collection = self.collect()
    return collection == sorted(collection)


class Ref:
    def __init__(self, val):
        self.val = val

    def __call__(self, val):
        self.val = val
        return val

    def __getattr__(self, name):
        if name != '_':
            raise ChemicalException("To get a reference's value, use: `ref._`")
        return self.val

    def set(self, val):
        self.val = val

    def get(self):
        return self.val


@trait
def fold(self, seed, closure):
    # it((1, 2, 3)).fold(1, lambda a, i: a(a._ * i))
    

    # the_seed = Ref(seed)
    # for i in self.items:
    #     closure(the_seed, i)
    # return the_seed.get()

    return self.scan(seed, closure).last()


@trait
def scan(self, seed, closure):
    the_seed = Ref(seed)

    return it(
        (closure(the_seed, i) for i in self),
        (closure(the_seed, i) for i in self.reverse),
        self.size_hint()
    )


@trait
def product(self):
    return self.fold(1, lambda acc, ele: acc(acc._ * ele))


@trait
def par_iter(self):
    from concurrent.futures import ThreadPoolExecutor, as_completed, Future
    import multiprocessing

    num_cores = multiprocessing.cpu_count()

    pool = ThreadPoolExecutor() # max = ...
    submitted = [None] * num_cores
    completed = False

    while not completed:
        for i in range(num_cores):
            submitted[i] = pool.submit(
                lambda s, idx: (idx, next(s)), self, i
            )

        for value in as_completed(submitted):
            try:
                index, val = value.result()
                submitted[index] = val
            except StopIteration:
                completed = True

        for value in submitted:
            if not isinstance(value, Future):
                yield value


@trait
class Par_Iter(it):
    def __init__(self, items):
        it.__init__(self, self._process_items(it(items)))

    def process_items(the_items):
        from concurrent.futures import ThreadPoolExecutor, as_completed, Future
        import multiprocessing

        num_cores = multiprocessing.cpu_count()

        pool = ThreadPoolExecutor() # max = ...
        submitted = [None] * num_cores
        completed = False

        while not completed:
            for i in range(num_cores):
                submitted[i] = pool.submit(
                    lambda s, idx: (idx, next(s)), the_items, i
                )

            for value in as_completed(submitted):
                try:
                    index, val = value.result()
                    submitted[index] = val
                except StopIteration:
                    completed = True

            for value in submitted:
                if not isinstance(value, Future):
                    yield value


@trait
def par_iter(self):
    def _process_items(the_items):
        yield

        from concurrent.futures import ThreadPoolExecutor, as_completed, Future
        import multiprocessing

        num_cores = multiprocessing.cpu_count()

        pool = ThreadPoolExecutor() # max = ...
        submitted = [None] * num_cores
        completed = False

        while not completed:
            for i in range(num_cores):
                submitted[i] = pool.submit(
                    lambda s, idx: (idx, next(s)), the_items, i
                )

            for value in as_completed(submitted):
                try:
                    index, val = value.result()
                    submitted[index] = val
                except StopIteration:
                    completed = True

            for value in submitted:
                if not isinstance(value, Future):
                    yield value


    # Prevent from continuing right off the bat by returning None initially.
    # E.g. subsequent calls to next() will yield actual values.
    forward = _process_items(self.items)
    backward = _process_items(self.rev())
    next(forward)
    next(backward)

    return it(forward, backward, self.size_hint())
