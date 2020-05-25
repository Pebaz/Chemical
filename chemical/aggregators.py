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
    

    **Examples**

        :::python

        assert it('asdf').any(lambda x: x > 'a')
        assert not it('bsdf').all(lambda x: x <= 'a')
    """
    return any(func(i) for i in self)


@trait
def collect(self, into=list):
    """
    

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
    

    **Examples**

        :::python

        assert it('abc').nth(3) == 'c'
        assert it('abc').skip(1).nth(2) == 'c'
        assert it('abc').cycle().nth(23) == 'b'
    """
    if num <= 0:
        raise ChemicalException('nth: to take the first item, use integer 1')
    for i in range(num):
        item = next(self)
    return item


@trait
def count(self):
    """
    

    **Examples**

        :::python

        assert it('abc').count() == 3
        assert it('abc').skip(1).count() == 2
        assert it('abc').skip(1).take(2).count() == 2
    """
    # NOTE(pebaz): `it.__len__` can never exist because list(), etc. would try
    # to use it, which would consume it.
    return len(list(self))


@trait
def last(self):
    """
    

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
    

    **Examples**

        :::python

        assert it('asdf').gt('asd')
        assert it('asdf').cycle().take(5).gt('asd')
    """
    return self.cmp(other) == Ordering.Greater


@trait
def ge(self, other):
    """
    

    **Examples**

        :::python

        assert it('asdf').ge('asd')
        assert it('asdf').cycle().take(5).ge('asd')
    """
    return self.cmp(other) in (Ordering.Greater, Ordering.Equal)


@trait
def lt(self, other):
    """
    

    **Examples**

        :::python

        assert it('asdf').lt('asddfas')
        assert it('asdf').cycle().take(5).lt('asdfas')
    """
    return self.cmp(other) == Ordering.Less


@trait
def le(self, other):
    """
    

    **Examples**

        :::python

        assert it('as').le('asd')
        assert it('asdf').cycle().take(5).le('asdfa')
    """
    return self.cmp(other) in (Ordering.Less, Ordering.Equal)


@trait
def cmp_by(self, other, closure):
    """
    

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
    

    **Examples**

        :::python

        assert it('asdf').neq('asdf1')
        assert it('asdf').skip(1).neq('asdf')
    """
    return not self.eq(other)


@trait
def find(self, closure):
    """
    

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
    

    **Examples**

        :::python

        assert it((1, 2, 3)).product() == 6
        assert it((-1, 2, 3)).product() == -6
    """
    return self.fold(1, lambda acc, ele: acc(acc._ * ele))
