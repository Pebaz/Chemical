import math
from . import it, trait, ChemicalException, NothingToPeek, Ref


@trait
class Skip(it):
    """
    Lazily skip a number of items in the iterator chain.

    **Examples**

        :::python

        assert it('asdf').skip(1).collect(str) == 'sdf'
        assert it('asdf').rev().skip(1).rev().collect(str) == 'asd'
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
    """
    If > 1, the number of elements to skip between each returned value.

    **Examples**

        :::python

        assert it(range(10)).step_by(2).collect() == [0, 2, 4, 6, 8]
        assert it(range(10)).rev().step_by(3).collect() == [9, 6, 3, 0]
    """
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

    **Examples**

        :::python

        assert it(range(5)).filter(lambda x: not x % 2).collect() == [0, 2, 4]
        assert it('abcd').filter(lambda x: x in 'bd').collect(str) == 'bd'
    """
    return it(
        (i for i in self if filter_func(i)),
        (i for i in self.reverse if filter_func(i)),
        (0, self._upper_bound)
    )


@trait
def take(self, num_items):
    """
    Returns only the number of items you specify from an iterator.

    **Examples**

        :::python

        assert it(range(5)).take(2).collect() == [0, 1]
        assert it(range(5)).rev().take(3).collect() == [4, 3, 2]
    """
    taken = [next(self) for i in range(num_items)]
    return it(iter(taken), reversed(taken), [num_items] * 2)


@trait
def take_while(self, closure):
    """
    Only returns elements from the iterator while a given function returns True.

    **Examples**

        :::python

        assert it('ab7f').take_while(lambda x: x.isalpha()).collect(str) == 'ab'
    """
    return it(
        (i for i in self if closure(i)),
        it(i for i in self.reverse if closure(i)),
        (0, self.size_hint()[1])
    )


@trait
class Peekable(it):
    """
    Adds a method to any iterator that allows the next element to be revealed
    without consuming it.

    **Examples**

        :::python

        itr = it('cba').rev().peekable()
        assert itr.peek() == 'a'
        assert itr.next() == 'a'
        assert itr.peek() == 'b'
        assert itr.next() == 'b'
        assert itr.peek() == 'c'
        assert itr.next() == 'c'
    """
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


@trait('chain')
def chain_it(self, itr):
    """
    Chains multiple iterators together, yielding each element in turn.

    **Examples**

        :::python

        assert it('ab').chain('cd').collect(str) == 'abcd'
        assert it('ab').chain('cd').rev().collect(str) == 'dcba'
    """
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
    """
    Continuously returns the elements of the underlying iterator.

    Without being limited in some way, this iterator will never raise the
    `StopIteration` exception so be careful when using it in loops.

    **Examples**

        :::python

        assert it('123').cycle().take(6).collect(str) == '123123'
    """
    from itertools import cycle
    return it(cycle(self), it(cycle(self.reverse)))


@trait('map')
def map_it(self, closure):
    """
    Applies a given function to each element and returns the result instead.

    **Examples**

        :::python

        assert it('abc').map(lambda x: x.upper()).collect(str) == 'ABC'
    """
    return it(
        map(closure, self),
        map(closure, self.reverse),
        self.size_hint()
    )


@trait('enumerate')
def enumerate_it(self):
    """
    Yields a tuple containing the position and the value of each element.

    **Examples**

        :::python

        assert it((1, 2, 3)).enumerate().collect() == [(0, 1), (1, 2), (2, 3)]
    """
    return it(enumerate(self), enumerate(self.reverse), self.size_hint())


@trait
class Inspect(it):
    """
    Allows a function to be applied to each element in an iterator without
    modifying it in any way.

    This is useful for inspecting the results of an iterator.

    **Examples**

        :::python

        # Prints each element on it's own line
        it('abc').inspect(print).go()

        (it('abc')
            .inspect(lambda x: print('Before:', x))
            .map(lambda x: x.upper())
            .inspect(lambda x: print('After:', x))
            .go()
        )
    """
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
    """
    Combines the elements from two iterators into a single iterator that returns
    tuples containing the elements of each.

    Discards elements of iterators longer than the other.

    **Examples**

        :::python

        assert it(range(2)).zip(range(1000)).collect() == [(0, 0), (1, 1)]
    """
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
def skip_while(self, closure):
    """
    Returns any element after each one that doesn't match the given function.

    **Examples**

        :::python

        assert (it('abDF')
            .skip_while(lambda x: x.upper() != x)
            .collect(str)
        ) == 'DF'
    """
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
def flatten(self):
    """
    Removes one level of grouping from each element in an iterator.

    Can be used to flatten a list of lists. However, it will not flatten a list
    containing lists of lists.

    **Examples**

        :::python

        assert it([[1], [2], [3]]).flatten().collect() == [1, 2, 3]
    """
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
    """
    Iterator version of a `for` loop.

    Executes a function on each element without modifying the element.

    **Examples**

        :::python

        # Prints each element on its own line.
        assert it('asdf').for_each(print)
    """
    return it(
        (closure(i) for i in self),
        (closure(i) for i in self.reverse),
        self.size_hint()
    )


@trait
def fold(self, seed, closure):
    """
    An iterator method that applies a function, producing a single, final value.

    `fold()` takes two arguments: an initial value, and a closure with two
    arguments: an 'accumulator', and an element. The closure returns the value
    that the accumulator should have for the next iteration.

    The initial value is the value the accumulator will have on the first call.

    After applying this closure to every element of the iterator, `fold()`
    returns the accumulator.

    This operation is sometimes called 'reduce' or 'inject'.

    Folding is useful whenever you have a collection of something, and want to
    produce a single value from it.

    In order to achieve this in Python, a special type had to be created in
    order to retain a reference to a value over the lifetime of the loop.

    The `Ref` type is used to allow you to assign within a lambda function.

    To get the value contained with a reference (dereference), simply access the
    `_` attribute. To assign to the same value within an expression, you can
    simply call the reference. A common pattern with the `Ref` type is to
    assign and dereference in the same expression like this:
    `my_ref(my_ref._ + 1)`

    **Examples**

        :::python

        assert it((1, 2, 3)).fold(1, lambda a, i: a(a._ * i)) == 6

        # These are equivalent:
        my_ref = Ref(2)

        print(my_ref.val)
        print(my_ref.get())
        print(my_ref._)

        my_ref.val = 123
        my_ref.set(123)
        my_ref(123)  # Assignment within an expression
    """
    return self.scan(seed, closure).last()


@trait
def scan(self, seed, closure):
    """
    An iterator adaptor similar to fold that holds internal state and produces a
    new iterator.

    `scan()` takes two arguments: an initial value which seeds the internal
    state, and a closure with two arguments, the first being a mutable reference
    to the internal state and the second an iterator element. The closure can
    assign to the internal state to share state between iterations.

    On iteration, the closure will be applied to each element of the iterator
    and the return value from the closure.

    **Examples**

        :::python

        assert (it((1, 2, 3))
            .scan(1, lambda acc, ele: acc(acc._ * ele))
            .collect()
        ) == [1, 2, 6]
    """
    the_seed = Ref(seed)

    return it(
        (closure(the_seed, i) for i in self),
        (closure(the_seed, i) for i in self.reverse),
        self.size_hint()
    )


@trait
def par_iter(self):
    """
    Iterate through the elements of an iterator concurrently.

    Since CPython is only able to execute 1 true thread at a time, only the
    illusion of parallelism is achievable, which can definitely be highly useful
    in situations where tasks need to not execute sequencially.

    Please see [this talk](https://blog.golang.org/waza-talk) on why concurrency
    is not the same as parallelism.

    It should be noted that the name "par_iter" was taken from Rayon's
    [par_iter](https://docs.rs/rayon/0.6.0/rayon/par_iter/index.html) function.

    The order of items in the underlying iterator are maintained.

    If your item handling code has side-effects, `par_iter` may not be the best
    solution for you because it handles each item concurrently and those side
    effects may occur in a different order.

    **Examples**

    The order of the returned elements is maintained even though they are
    processed concurrently.

        :::python

        itr = it(range(3)).par_iter()
        assert itr.next() == 0
        assert itr.next() == 1
        assert itr.next() == 2

    Making HTTP requests is faster using `par_iter`:

        :::python
        from requests import get as GET

        urls = [...]

        results = (it(urls)
            .map(lambda u: GET(u))
            .map(lambda u: u.text if u.ok else u.reason)
            .par_iter()
            .collect()
        )
    """

    def _process_items(the_items):
        yield

        from concurrent.futures import ThreadPoolExecutor, as_completed, Future
        import multiprocessing

        num_cores = multiprocessing.cpu_count()

        pool = ThreadPoolExecutor(max_workers=num_cores)
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
