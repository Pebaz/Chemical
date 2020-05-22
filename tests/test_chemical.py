import pytest
from chemical import it, ChemicalException, Ordering, NothingToPeek


class MyItem:
    def __init__(self, val):
        self.val = val
    def __gt__(self, other):
        return self.val > other.val
    def __eq__(self, other):
        return self.val == other.val


def test_it():
    assert list(it(range(3))) == [0, 1, 2]
    assert list(it('abc')) == ['a', 'b', 'c']
    assert list(it(dict(name='Pebaz'))) == ['name']

    with pytest.raises(ChemicalException):
        a = it('asdf')
        a.next()
        a.rev()

    assert it('asdf').size_hint() == (4, 4)
    assert it(it('asdf')).size_hint() == (4, 4)
    assert it(range(10)).size_hint() == (10, 10)


def test_take():
    assert it('a').take(1).collect() == ['a']
    assert it('abcdefg').take(2).collect() == ['a', 'b']
    assert it('abcdefg').skip(2).take(2).collect() == ['c', 'd']
    assert it('abcdefg').step_by(2).take(3).collect() == ['a', 'c', 'e']

    assert it('a').rev().take(1).collect(str) == 'a'
    assert it('a').take(1).rev().collect(str) == 'a'
    assert it('abc').rev().take(3).collect(str) == 'cba'
    assert it('abc').take(3).rev().collect(str) == 'cba'

    with pytest.raises(ChemicalException):
        a = it('asdf').take(3)
        a.next()
        a.rev()

    assert it('asdf').take(3).size_hint() == (3, 3)
    assert it('asdf').take(3).rev().size_hint() == (3, 3)


def test_collect():
    assert it(range(3)).collect() == [0, 1, 2]
    assert it(range(3)).collect(tuple) == (0, 1, 2)
    assert it(range(3)).collect(set) == {0, 1, 2}
    class MyList(list): ...
    assert it(range(3)).collect(MyList) == MyList((0, 1, 2))
    assert it('abcdef').collect(str) == 'abcdef'
    assert it('asdf').map(lambda x: x.upper()).collect(str) == 'ASDF'
    assert it(range(3)).collect(str) == '012'
    assert it(range(10)).step_by(2).collect(str) == '02468'
    
    assert it(range(3)).rev().collect() == [2, 1, 0]
    assert it('asdf').rev().collect(str) == 'fdsa'
    assert it(it('asdf').rev()).rev().collect(str) == 'asdf'
    assert it(range(3)).rev().rev().rev().collect() == [2, 1, 0]


def test_skip():
    assert it(range(3)).skip(1).collect() == [1, 2]
    assert it(range(100)).skip(10).take(10).collect() == [*range(10, 20)]
    assert it(range(10)).skip(1).skip(1).collect() == [*range(2, 10)]

    assert it(range(3)).skip(1).rev().collect() == [2, 1]
    assert it(range(3)).skip(1).rev().skip(1).rev().collect() == [1]

    with pytest.raises(ChemicalException):
        a = it('asdf').skip(1)
        a.next()
        a.rev()

    assert it('asdf').skip(1).size_hint() == (3, 3)
    assert it('asdf').skip(1).rev().size_hint() == (3, 3)


def test_peekable():
    xs = 1, 2, 3
    i = it(xs).peekable()
    assert i.peek() == xs[0]
    assert i.next() == xs[0]
    assert i.next() == xs[1]
    assert i.peek() == xs[2]
    assert i.peek() == xs[2]
    assert i.next() == xs[2]

    i = it(xs).rev().peekable()
    assert i.peek() == xs[2]
    assert i.next() == xs[2]
    assert i.next() == xs[1]
    assert i.peek() == xs[0]
    assert i.peek() == xs[0]
    assert i.next() == xs[0]

    i = it(xs).rev().skip(1).peekable()
    assert i.peek() == xs[1]
    assert i.next() == xs[1]
    assert i.peek() == xs[0]
    assert i.next() == xs[0]

    with pytest.raises(NothingToPeek):
        i.peek()

    with pytest.raises(StopIteration):
        i.next()

    assert it(xs).take(3).rev().skip(1).collect() == [2, 1]

    with pytest.raises(ChemicalException):
        a = it('asdf').peekable()
        a.peek()
        a.next()
        a.rev()

    assert it('asdf').peekable().size_hint() == (4, 4)
    assert it('asdf').peekable().rev().size_hint() == (4, 4)


def test_max():
    assert it([1]).max() == 1
    assert it((1, 2, 3, 4)).max() == 4
    assert it('asdf').max() == 's'
    assert it((MyItem(1), MyItem(2), MyItem(3))).max() == MyItem(3)

    assert it(range(3)).rev().max() == 2
    assert it(range(3)).rev().take(2).rev().max() == 2


def test_min():
    assert it([1]).min() == 1
    assert it((1, 2, 3, 4)).min() == 1
    assert it('asdf').min() == 'a'
    assert it((MyItem(1), MyItem(2), MyItem(3))).min() == MyItem(1)

    assert it(range(3)).rev().min() == 0
    assert it(range(3)).rev().take(2).rev().min() == 1


def test_max_by_key():
    assert it([1]).max_by_key(lambda x: -x) == 1
    assert it((1, 2, 3, 4)).max_by_key(lambda x: -x) == 1

    assert it(range(1, 5)).rev().max_by_key(lambda x: -x) == 1


def test_min_by_key():
    assert it([1]).min_by_key(lambda x: -x) == 1
    assert it((1, 2, 3, 4)).min_by_key(lambda x: -x) == 4

    assert it(range(1, 5)).rev().min_by_key(lambda x: -x) == 4


def test_chain():
    assert it((1, 2, 3)).chain((4, 5, 6)).collect() == [1, 2, 3, 4, 5, 6]
    assert it('as').chain((3.1, 2.4)).collect() == ['a', 's', 3.1, 2.4]

    assert it('as').chain('df').rev().collect(str) == 'fdsa'
    assert it(range(10)).rev().chain('df').collect(str) == '9876543210df'
    assert it(range(10)).rev().chain('df').rev().collect(str) == 'fd0123456789'

    with pytest.raises(ChemicalException):
        a = it('asdf').chain('fdsa')
        a.next()
        a.rev()

    assert it('as').chain('df').size_hint() == (4, 4)
    assert it('as').chain('df').rev().size_hint() == (4, 4)


def test_filter():
    func = lambda x: x > 2; data = 1, 2, 3, 4, 5
    assert it(data).filter(func).collect() == list(filter(func, data))

    assert it(data).filter(func).rev().collect() == [5, 4, 3]
    assert it(data).filter(func).take(3).rev().collect() == [5, 4, 3]

    with pytest.raises(ChemicalException):
        a = it('asdf').filter(lambda x: x.upper() in 'DF')
        a.next()
        a.rev()

    assert it(data).filter(func).size_hint() == (0, 5)
    assert it(data).filter(func).rev().size_hint() == (0, 5)


def test_cycle():
    assert it(range(3)).cycle().take(6).collect() == [0, 1, 2, 0, 1, 2]
    assert it('abc').cycle().take(6).collect() == ['a', 'b', 'c', 'a', 'b', 'c']

    assert it('abc').cycle().rev().take(6).collect(str) == 'cbacba'
    assert it('abc').cycle().rev().take(6).rev().collect(str) == 'abcabc'

    with pytest.raises(ChemicalException):
        a = it('asdf').cycle()
        a.next()
        a.rev()

    assert it('asdf').cycle().size_hint() == (0, None)
    assert it('asdf').cycle().rev().size_hint() == (0, None)


def test_all():
    assert not it('asdf').all(lambda x: x > 'a')
    assert it('bsdf').all(lambda x: x > 'a')

    assert not it('asdf').rev().all(lambda x: x > 'a')
    assert it('bsdf').rev().all(lambda x: x > 'a')


def test_any():
    assert it('asdf').any(lambda x: x > 'a')
    assert not it('bsdf').all(lambda x: x <= 'a')

    assert it('asdf').rev().any(lambda x: x > 'a')
    assert not it('bsdf').rev().all(lambda x: x <= 'a')


def test_count():
    assert it('abc').count() == 3
    assert it('abc').skip(1).count() == 2
    assert it('abc').skip(1).take(2).count() == 2

    assert it('abc').rev().count() == 3
    assert it('abc').skip(1).rev().count() == 2
    assert it('abc').skip(1).take(2).rev().count() == 2    


def test_last():
    assert it('abc').last() == 'c'
    assert it('abc').skip(1).last() == 'c'
    assert it('abc').cycle().take(8).last() == 'b'

    assert it('abc').rev().last() == 'a'
    assert it('abc').skip(1).rev().last() == 'b'
    assert it('abc').cycle().take(8).rev().last() == 'a'


def test_nth():
    assert it('abc').nth(3) == 'c'
    assert it('abc').skip(1).nth(2) == 'c'
    assert it('abc').cycle().nth(23) == 'b'

    assert it('abc').rev().nth(3) == 'a'
    assert it('abc').skip(1).rev().nth(2) == 'b'
    assert it('abc').cycle().rev().nth(23) == 'b'


def test_step():
    assert it('abcdef').step_by(1).collect() == ['a', 'b', 'c', 'd', 'e', 'f']
    assert it('abcdef').step_by(2).collect() == ['a', 'c', 'e']
    assert it('abcdef').step_by(3).collect() == ['a', 'd']
    assert it('abcdef').cycle().step_by(3).nth(17) == 'a'

    assert it('abcdef').step_by(1).rev().collect(str) == 'fedcba'
    assert it('abcdef').step_by(2).rev().collect(str) == 'fdb'
    assert it('abcdef').step_by(3).rev().collect(str) == 'fc'
    assert it('abcdef').cycle().step_by(3).rev().nth(17) == 'f'
    assert it('abcdef').cycle().step_by(3).rev().take(17).collect(str) == (
        'fcfcfcfcfcfcfcfcf'
    )

    with pytest.raises(ChemicalException):
        a = it('asdf').step_by(2)
        a.next()
        a.rev()

    assert it('asdf').step_by(2).size_hint() == (2, 2)
    assert it('asdfg').step_by(2).size_hint() == (3, 3)
    assert it('asdf').step_by(3).size_hint() == (2, 2)
    assert it('asdf').step_by(2).rev().size_hint() == (2, 2)
    assert it('asdfg').step_by(3).rev().size_hint() == (2, 2)


def test_map():
    assert it('abc').map(lambda x: x.upper()).collect() == ['A', 'B', 'C']
    assert it((1, 2, 3)).map(lambda x: x ** x).collect() == [1, 4, 27]

    assert it((1, 2, 3)).map(lambda x: x ** x).rev().collect() == [
        27, 4, 1
    ]
    assert it((1, 2, 3)).map(lambda x: x ** x).rev().rev().collect() == [
        1, 4, 27
    ]
    assert (it((1, 2, 3))
        .map(lambda x: x ** x)
        .rev()
        .rev()
        .take(3)
        .collect()
    ) == [
        1, 4, 27
    ]
    assert (it((1, 2, 3))
        .map(lambda x: x ** x)
        .rev()
        .rev()
        .take(3)
        .skip(1)
        .rev()
        .collect()
    ) == [
        27, 4
    ]

    with pytest.raises(ChemicalException):
        a = it('asdf').map(lambda x: x.upper())
        a.next()
        a.rev()

    assert it('asdf').map(lambda x: x.upper()).size_hint() == (4, 4)
    assert it('asdf').map(lambda x: x.upper()).rev().size_hint() == (4, 4)
    assert it('ff').skip(1).map(lambda x: x).size_hint() == (1, 1)
    assert it('ff').skip(1).map(lambda x: x).rev().size_hint() == (1, 1)


def test_go():
    seen = []
    it('abc').inspect(lambda x: seen.append(x.upper())).go()
    assert seen == ['A', 'B', 'C']

    seen = []
    it('abc').skip(1).take(1).inspect(lambda x: seen.append(x.upper())).go()
    assert seen == ['B']

    seen = []
    it('abc').inspect(lambda x: seen.append(x.upper())).rev().go()
    assert seen == ['C', 'B', 'A']
    
    seen = []
    (it('abc')
        .skip(1)
        .take(1)
        .inspect(lambda x: seen.append(x.upper()))
        .rev()
        .go()
    )
    assert seen == ['B']


def test_inspect():
    seen = []
    it('abc').inspect(lambda x: seen.append(x.upper())).go()
    assert seen == ['A', 'B', 'C']

    seen = []
    it('abc').inspect(lambda x: seen.append(x.upper())).rev().go()
    assert seen == ['C', 'B', 'A']

    with pytest.raises(ChemicalException):
        a = it('asdf').inspect(print)
        a.next()
        a.rev()

    assert it('abc').inspect(lambda x: ()).size_hint() == (3, 3)
    assert it('abc').inspect(lambda x: ()).rev().size_hint() == (3, 3)


def test_sum():
    assert it((1, 2, 3)).sum() == 6
    assert it((1, 2, 3)).skip(1).sum() == 5
    assert it((1, 2, 3)).cycle().take(22).sum() == 43

    assert it((1, 2, 3)).rev().sum() == 6
    assert it((1, 2, 3)).skip(1).rev().sum() == 5
    assert it((1, 2, 3)).cycle().take(22).rev().sum() == 43


def test_enumerate():
    assert it((1, 2, 3)).enumerate().collect() == [(0, 1), (1, 2), (2, 3)]
    assert it((1, 2, 3)).skip(1).take(2).enumerate().collect() == [
        (0, 2), (1, 3)
    ]

    assert it((1, 2, 3)).enumerate().rev().collect() == [(0, 3), (1, 2), (2, 1)]
    assert it((1, 2, 3)).skip(1).take(2).enumerate().rev().collect() == [
        (0, 3), (1, 2)
    ]

    with pytest.raises(ChemicalException):
        a = it('asdf').enumerate()
        a.next()
        a.rev()

    assert it('asdf').enumerate().size_hint() == (4, 4)
    assert it('asdf').enumerate().rev().size_hint() == (4, 4)


def test_zip():
    gold = [(0, 7), (1, 6), (2, 5), (3, 4), (4, 3), (5, 2), (6, 1), (7, 0)]
    assert it(range(8)).zip(range(7, -1, -1)).collect() == gold
    assert it(range(8)).zip(range(7, -100000, -1)).collect() == gold

    assert it('abc').zip('123').rev().collect() == [
        ('c', '3'), ('b', '2'), ('a', '1')
    ]
    assert it('abc').zip('123456').rev().collect() == [
        ('c', '6'), ('b', '5'), ('a', '4')
    ]

    with pytest.raises(ChemicalException):
        a = it('asdf').zip('fdsa')
        a.next()
        a.rev()

    assert it('asdf').zip('fdsa').size_hint() == (8, 8)
    assert it('asdf').zip('fdsa').rev().size_hint() == (8, 8)


def test_unzip():
    gold = [*range(9)], [*range(8, -1, -1)]
    assert it(range(9)).zip(range(8, -1, -1)).unzip() == gold
    with pytest.raises(ChemicalException):
        it(([3, 2, 1, 0], ['a', 'b'])).unzip()
        assert False, "Should never get here"

    assert it('abc').zip('123').rev().unzip() == (
        ['c', 'b', 'a'], ['3', '2', '1']
    )

    assert it('abc').zip('123').rev().take(2).unzip() == (
        ['c', 'b'], ['3', '2']
    )


def test_take_while():
    assert it(range(10)).take_while(lambda x: x < 4).collect() == [0, 1, 2, 3]
    assert it([10, 2, 20]).take_while(lambda x: x < 4).collect() == [2]

    assert it([3, 10, 2, 20]).take_while(lambda x: x < 4).rev().collect() == [
        2, 3
    ]

    with pytest.raises(ChemicalException):
        a = it('asdf').take_while(lambda x: x.upper() in 'AS')
        a.next()
        a.rev()

    assert it('asdf').take_while(lambda _: ()).size_hint() == (0, 4)
    assert it('asdf').take_while(lambda _: ()).rev().size_hint() == (0, 4)


def test_skip_while():
    assert it(range(10)).skip_while(lambda x: x < 6).collect() == [6, 7, 8, 9]
    assert (it(range(100))
        .skip(10)
        .step_by(5)
        .skip(10)
        .skip_while(lambda x: x < 80)
        .take(4)
        .collect()
    ) == [80, 85, 90, 95]

    assert it(range(10)).skip_while(lambda x: x < 6).rev().collect() == [
        9, 8, 7, 6, 5, 4, 3, 2, 1, 0
    ]

    with pytest.raises(ChemicalException):
        a = it('asdf').skip_while(lambda x: x not in 'as')
        a.next()
        a.rev()

    assert it('asdf').skip_while(lambda _: ()).size_hint() == (0, 4)
    assert it('asdf').skip_while(lambda _: ()).rev().size_hint() == (0, 4)


def test_cmp():
    assert it('asdf').cmp((1, 2, 3, 4)) == Ordering.Equal
    assert it('asdf').cmp((1, 2, 3, 4, 5)) == Ordering.Less
    assert it('asdf').cmp((1, 2, 3)) == Ordering.Greater

    assert it('asdf').rev().cmp((1, 2, 3, 4)) == Ordering.Equal
    assert it('asdf').rev().cmp((1, 2, 3, 4, 5)) == Ordering.Less
    assert it('asdf').rev().cmp((1, 2, 3)) == Ordering.Greater


def test_gt():
    assert it('asdf').gt('asd')
    assert it('asdf').cycle().take(5).gt('asd')

    assert it('asdf').rev().gt('asd')
    assert it('asdf').cycle().take(5).rev().gt('asd')


def test_ge():
    assert it('asdf').ge('asd')
    assert it('asdf').cycle().take(5).ge('asd')
    assert it('asdf').ge('asdf')
    assert it('asdf').cycle().take(5).ge('asdfa')

    assert it('asdf').rev().ge('asd')
    assert it('asdf').cycle().take(5).rev().ge('asd')
    assert it('asdf').rev().ge('asdf')
    assert it('asdf').cycle().take(5).rev().ge('asdfa')


def test_lt():
    assert it('asdf').lt('asddfas')
    assert it('asdf').cycle().take(5).lt('asdfas')

    assert it('asdf').rev().lt('asddfas')
    assert it('asdf').cycle().take(5).rev().lt('asdfas')


def test_le():
    assert it('as').le('asd')
    assert it('asdf').cycle().take(5).le('asdfa')
    assert it('asdf').le('asdf')
    assert it('asdf').cycle().take(5).le('asdfa')

    assert it('as').rev().le('asd')
    assert it('asdf').cycle().take(5).rev().le('asdfa')
    assert it('asdf').rev().le('asdf')
    assert it('asdf').cycle().take(5).rev().le('asdfa')


def test_cmp_by():
    func = lambda a, b: a.upper() == b.upper()
    assert it('asdf').cmp_by('asdf', func)
    assert not it('bsdf').cmp_by('asdf', func)
    assert (it('abc')
        .cycle()
        .take(10)
        .cmp_by('abcabcabca', func)
    )

    assert it('asdf').rev().cmp_by('fdsa', func)
    assert not it('bsdf').rev().cmp_by('fdsa', func)
    assert (it('abc')
        .cycle()
        .take(10)
        .rev()
        .cmp_by('acbacbacba', func)
    )

    assert it((8, 9)).cmp_by((4, 3), lambda x, y: x > y)


def test_eq():
    assert it('asdf').eq('asdf')
    assert not it('asdf').eq('asdfasdfasdfasdf')
    assert it('asdf').skip(1).eq('sdf')
    assert not it('asdf').eq((2, 1, 23))

    assert it('asdf').rev().eq('fdsa')
    assert not it('asdf').rev().eq('fdsafdsafdsa')
    assert it('asdf').skip(1).rev().eq('fds')
    assert not it('asdf').rev().eq((2, 1, 23))


def test_neq():
    assert it('asdf').neq('asdf1')
    assert it('asdf').skip(1).neq('asdf')

    assert it('asdf').rev().neq('asdf1')
    assert it('asdf').skip(1).rev().neq('asdf')
    assert not it('asdf').rev().neq('fdsa')


def test_find():
    assert it('asdf').find(lambda x: x.upper() == 'S') == 's'
    with pytest.raises(ChemicalException):
        it('asdf').find(lambda x: x == 'say what?')

    assert it('asdf').rev().find(lambda x: x.upper() == 'S') == 's'
    with pytest.raises(ChemicalException):
        it('asdf').rev().find(lambda x: x == 'say what?')


def test_position():
    assert it('asdf').position(lambda x: x == 'd') == 2
    with pytest.raises(ChemicalException):
        it('asdf').position(lambda x: x == 'say what?')

    assert it('asdf').rev().position(lambda x: x == 'd') == 1
    with pytest.raises(ChemicalException):
        it('asdf').rev().position(lambda x: x == 'say what?')


def test_partition():
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


def test_flatten():
    assert it([[1, 2, 3], [4, 5, 6]]).flatten().collect() == [1, 2, 3, 4, 5, 6]
    assert it([[1, 2, 3], [4, 5, 6], 4]).flatten().collect() == [
        1, 2, 3, 4, 5, 6, 4
    ]

    assert it([[1, 2, 3], [4, 5, 6]]).flatten().rev().collect() == [
        6, 5, 4, 3, 2, 1
    ]
    assert it('abc').zip('123').flatten().rev().collect(str) == '3c2b1a'

    assert it('abc').zip('123').flatten().size_hint() == (6, 6)
    assert it('abc').zip('123').flatten().rev().size_hint() == (6, 6)


def test_intermittent_usage():
    a = it('asdf')
    assert a.next() == 'a'
    assert a.next() == 's'
    a = a.take(2)
    assert a.next() == 'd'
    assert a.next() == 'f'

    a = it('asdf')
    assert a.next() == 'a'
    assert a.next() == 's'
    a = a.take(2).peekable()
    assert a.peek() == 'd'
    assert a.next() == 'd'
    assert a.peek() == 'f'
    assert a.next() == 'f'


def test_for_each():
    stuff = []
    it((1, 2, 3)).for_each(lambda x: stuff.append(x)).go()
    assert stuff == [1, 2, 3]

    stuff = []
    it((1, 2, 3)).for_each(lambda x: stuff.append(x)).rev().go()
    assert stuff == [3, 2, 1]

    with pytest.raises(ChemicalException):
        stuff = []
        a = it((1, 2, 3)).for_each(lambda x: stuff.append(x))
        a.next()
        a.rev()

    assert it('asdf').for_each(lambda _: ()).size_hint() == (4, 4)
    assert it('asdf').for_each(lambda _: ()).rev().size_hint() == (4, 4)


def test_is_sorted():
    assert it((1, 2, 3)).is_sorted()
    assert not it((2, 3, 1)).is_sorted()

    assert not it((1, 2, 3)).rev().is_sorted()


def test_product():
    assert it((1, 2, 3)).product() == 6
    assert it((-1, 2, 3)).product() == -6

    assert it((1, 2, 3)).rev().product() == 6
    assert it((-1, 2, 3)).rev().product() == -6


def test_fold():
    assert it((1, 2, 3)).fold(1, lambda a, i: a(a._ * i)) == 6
    assert it((1, 2, 3)).rev().fold(1, lambda a, i: a(a._ * i)) == 6


def test_scan():
    assert (it((1, 2, 3))
        .scan(1, lambda acc, ele: acc(acc._ * ele))
        .collect()
    ) == [1, 2, 6]

    class Scanner:
        def __init__(self):
            self.chars = []
            self.state = 'GET'

    def state_machine(state, char):
        if state._.state == 'PRINT':
            print(char)
            state._.state = 'GET'
        elif state._.state == 'GET':
            state._.chars.append(char)
            state._.state = 'PRINT'
        else:
            raise Exception('Unreachable')

    scanner = Scanner()
    it('abcd').scan(scanner, state_machine).go()
    assert scanner.chars == ['a', 'c']

    assert it('abcd').scan(None, lambda _, __: ()).size_hint() == (4, 4)
    assert it('abcd').scan(None, lambda _, __: ()).rev().size_hint() == (4, 4)


def test_size_hint():
    assert it('asdf').size_hint() == (4, 4)
    assert it(range(10)).filter(lambda x: not x % 2).size_hint() == (0, 10)

    assert (it(range(10))
        .filter(lambda x: not x % 2)
        .chain(range(15, 20))
        .size_hint()
    ) == (5, 15)
