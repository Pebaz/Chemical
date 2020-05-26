from . import it, trait, ChemicalException, Ordering


@trait('all')
def all_it(self, func):
    """
    Returns a boolean indicating the results of calling `func` on each element.

    If all results are True, then True is returned, else False.

    **Examples**

        :::python

        assert it(range(3)).all(lambda x: x < 10000)
        assert it('asdf').all(lambda x: x in 'asdf')
    """
    return all(func(i) for i in self)


@trait('any')
def any_it(self, func):
    """
    Returns True if any calling the given function returns True for any item.

    **Examples**

        :::python

        assert it('asdf').any(lambda x: x > 'a')
        assert not it('bsdf').all(lambda x: x <= 'a')
    """
    return any(func(i) for i in self)


@trait
def collect(self, into=list):
    """
    Consumes the iterator and returns a collection of the given type.

    Special handling is given to the `str` type. `__str__()` is called on each
    element and then the resulting list of strings are concatenated together to
    form one string.

    All other collections are formed by passing the iterator to the constructor.

    **Examples**

        :::python

        assert it(range(3)).collect() == [0, 1, 2]
        assert it(range(3)).collect(tuple) == (0, 1, 2)
        assert it(range(3)).collect(set) == {0, 1, 2}
        assert it('abc').collect(str) == 'abc'
    """
    if into == str:
        return ''.join(str(i) for i in self)
    else:
        return into(self)


@trait
def nth(self, num):
    """
    Returns the nth element from an iterator.

    If 3 is passed, this returns the 3rd element, and so on.

    If a negative number is passed, this is the equivalent of the following:

        :::python

        itr = it('abc')
        assert itr.nth(-1) == itr.rev().nth(1)

    **Examples**

        :::python

        assert it('abc').nth(3) == 'c'
        assert it('abc').skip(1).nth(2) == 'c'
        assert it('abc').cycle().nth(23) == 'b'
    """
    if num == 0:
        raise ChemicalException('nth: to take the first item, use integer 1')

    for i in range(abs(num)):
        item = next(self if num > 0 else self.reverse)

    return item


@trait
def count(self):
    """
    Returns the length of the iterator, consuming it.

    Unfortunately, a `__len__()` method cannot be added to `it` because loops
    such as `for` will call it if it exists, which will consume the iterator
    before it even runs the loop.

    However, it is better than no `__len__()` method exists because the length
    of an iterator is seldom known. See also `size_hint()`.

    **Examples**

        :::python

        assert it('abc').count() == 3
        assert it('abc').skip(1).count() == 2
        assert it('abc').skip(1).take(2).count() == 2
    """
    # NOTE(pebaz): `it.__len__` can never exist because list(), etc. would try
    # to use it, which would consume it.
    index = 0
    for _ in self:
        index += 1
    return index


@trait
def last(self):
    """
    Returns the last element of an iterator, consuming it.

    **Examples**

        :::python

        assert it('abc').last() == 'c'
        assert it('abc').skip(1).last() == 'c'
        assert it('abc').cycle().take(8).last() == 'b'
    """
    item = None
    for i in self:
        item = i
    return item


@trait('max')
def max_it(self):
    """
    Returns the largest item in the iterator, consuming it.

    **Examples**

        :::python

        assert it([1]).max() == 1
        assert it((1, 2, 3, 4)).max() == 4
        assert it('asdf').max() == 's'
    """
    return max(self)


@trait('min')
def min_it(self):
    """
    Returns the smallest item in the iterator, consuming it.

    **Examples**

        :::python

        assert it([1]).min() == 1
        assert it((1, 2, 3, 4)).min() == 1
        assert it('asdf').min() == 'a'
    """
    return min(self)


@trait
def max_by_key(self, closure):
    """
    Uses a function to determine the largest item in an iterator.

    **Examples**

        :::python

        assert it([1]).max_by_key(lambda x: -x) == 1
        assert it((1, 2, 3, 4)).max_by_key(lambda x: -x) == 1
    """
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
    """
    Uses a function to determine the smallest item in an iterator.

    **Examples**

        :::python

        assert it([1]).min_by_key(lambda x: -x) == 1
        assert it((1, 2, 3, 4)).min_by_key(lambda x: -x) == 4
    """
    min_val = self.next()
    min_cmp = closure(min_val)
    for i in self:
        comp = closure(i)
        if comp < min_cmp:
            min_val = i
            min_cmp = comp
    return min_val


@trait('sum')
def sum_it(self):
    """
    Adds all elements in the iterator together.

    **Examples**

        :::python

        assert it((1, 2, 3)).sum() == 6
        assert it((1, 2, 3)).skip(1).sum() == 5
        assert it((1, 2, 3)).cycle().take(22).sum() == 43
    """
    return sum(self)


@trait
def go(self):
    """
    Consumes the iterator without returning anything.

    Useful for situations in which you want to avoid a large numbers of
    allocations. For instance, without `go()`, you would have to consume the
    iterator using a `for` loop, or calling `list(it)`. Either option is less
    convenient than just using `go()`.

    **Examples**

        :::python

        seen = []
        it('abc').inspect(lambda x: seen.append(x.upper())).go()
        assert seen == ['A', 'B', 'C']
    """
    for i in self: ...


@trait
def unzip(self):
    """
    Returns two lists created from the first and second index of every
    collection found within the iterator.

    **Examples**

        :::python

        gold = [*range(9)], [*range(8, -1, -1)]
        assert it(range(9)).zip(range(8, -1, -1)).unzip() == gold
    """
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
def cmp(self, other):
    """
    Lexicographically compares elements of an iterator with those of another.

    Essentially, this compares the length of one iterator with another.

    **Examples**

        :::python

        assert it('asdf').cmp((1, 2, 3, 4)) == Ordering.Equal
        assert it('asdf').cmp((1, 2, 3, 4, 5)) == Ordering.Less
        assert it('asdf').cmp((1, 2, 3)) == Ordering.Greater
    """
    a, b = self.count(), it(other).count()
    if a == b: return Ordering.Equal
    elif a < b: return Ordering.Less
    elif a > b: return Ordering.Greater


@trait
def gt(self, other):
    """
    Returns if an iterator is lexicographically longer than another.

    **Examples**

        :::python

        assert it('asdf').gt('asd')
        assert it('asdf').cycle().take(5).gt('asd')
    """
    return self.cmp(other) == Ordering.Greater


@trait
def ge(self, other):
    """
    Returns if an iterator is lexicographically longer/equal to another.

    **Examples**

        :::python

        assert it('asdf').ge('asd')
        assert it('asdf').cycle().take(5).ge('asd')
    """
    return self.cmp(other) in (Ordering.Greater, Ordering.Equal)


@trait
def lt(self, other):
    """
    Returns if an iterator is lexicographically shorter than another.

    **Examples**

        :::python

        assert it('asdf').lt('asddfas')
        assert it('asdf').cycle().take(5).lt('asdfas')
    """
    return self.cmp(other) == Ordering.Less


@trait
def le(self, other):
    """
    Returns if an iterator is lexicographically shorter/equal to another.

    **Examples**

        :::python

        assert it('as').le('asd')
        assert it('asdf').cycle().take(5).le('asdfa')
    """
    return self.cmp(other) in (Ordering.Less, Ordering.Equal)


@trait
def cmp_by(self, other, closure):
    """
    Checks if this iterator is equal with another using a comparison function.

    **Examples**

        :::python

        func = lambda a, b: a.upper() == b.upper()
        assert it('asdf').cmp_by('asdf', func)
        assert not it('bsdf').cmp_by('asdf', func)
    """
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
    """
    Returns if the elements of this iterator are equal to another, consuming
    them both.

    **Examples**

        :::python

        assert it('asdf').eq('asdf')
        assert not it('asdf').eq('asdfasdfasdfasdf')
        assert it('asdf').skip(1).eq('sdf')
        assert not it('asdf').eq((2, 1, 23))
    """
    return self.cmp_by(other, lambda a, b: a == b)


@trait
def neq(self, other):
    """
    Returns if the elements of this iterator are not equal to another, consuming
    them both.

    **Examples**

        :::python

        assert it('asdf').neq('asdf1')
        assert it('asdf').skip(1).neq('asdf')
    """
    return not self.eq(other)


@trait
def find(self, closure):
    """
    Uses a function to search for an item if it exists and returns the item.

    The function should return True if the item is found.

    **Examples**

        :::python

        assert it('asdf').find(lambda x: x.upper() == 'S') == 's'
        assert it('asdf').rev().find(lambda x: x.upper() == 'S') == 's'
    """
    try:
        return self.filter(closure).next()
    except StopIteration as e:
        ...
    raise ChemicalException(
        'find: item matching provided lambda could not be found'
    )


@trait
def position(self, closure):
    """
    Uses a function to obtain the index of an element within an iterator.

    The function should return True if the item is found.

    **Examples**

        :::python

        assert it('asdf').position(lambda x: x == 'd') == 2
        assert it('asdf').rev().position(lambda x: x == 'd') == 1
    """
    for i, element in self.enumerate():
        if closure(element):
            return i
    raise ChemicalException(
        'position: item matching provided lambda is not in collection'
    )


@trait
def partition(self, closure):
    """
    Takes a Lambda that returns a boolean and returns two lists containing the
    items that returned `True` and the items that returned `False`.

    **Examples**

        :::python

        assert it((1, 2, 3)).partition(lambda x: x % 2 == 0) == (
            [2], [1, 3]
        )
        assert it('aSdF').partition(lambda x: x.upper() == x) == (
            ['S', 'F'], ['a', 'd']
        )

        assert it((1, 2, 3)).rev().partition(lambda x: x % 2 == 0) == (
            [2], [3, 1]
        )
        assert it('aSdF').rev().partition(lambda x: x.upper() == x) == (
            ['F', 'S'], ['d', 'a']
        )
    """
    parts = [], []
    for i in self:
        parts[int(not closure(i))].append(i)
    return parts


@trait
def is_sorted(self):
    """
    Returns `True` if the iterator is sorted, consuming it.

    **Examples**

        :::python

        assert it((1, 2, 3)).is_sorted()
        assert not it((2, 3, 1)).is_sorted()
    """
    collection = self.collect()
    return collection == sorted(collection)


@trait
def product(self):
    """
    Multiplies all the elements together, consuming the iterator.

    **Examples**

        :::python

        assert it((1, 2, 3)).product() == 6
        assert it((-1, 2, 3)).product() == -6
    """
    return self.fold(1, lambda acc, ele: acc(acc._ * ele))
