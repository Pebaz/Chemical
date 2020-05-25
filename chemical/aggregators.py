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


@trait('sum')
def sum_it(self):
    return sum(self)


@trait
def go(self):
    for i in self: ...


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
def is_sorted(self):
    collection = self.collect()
    return collection == sorted(collection)


@trait
def product(self):
    return self.fold(1, lambda acc, ele: acc(acc._ * ele))
