from chemical import it


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


def test_take():
    assert it('abcdefg').take(2).collect() == ['a', 'b']
    assert it('abcdefg').skip(2).take(2).collect() == ['c', 'd']
    assert it('abcdefg').step_by(2).take(3).collect() == ['a', 'c', 'e']


def test_collect():
    assert it(range(3)).collect() == [0, 1, 2]
    assert it(range(3)).collect(tuple) == (0, 1, 2)
    assert it(range(3)).collect(set) == {0, 1, 2}
    class MyList(list): ...
    assert it(range(3)).collect(MyList) == MyList((0, 1, 2))


def test_skip():
    assert it(range(3)).skip(1).collect() == [1, 2]
    assert it(range(100)).skip(10).take(10).collect() == [*range(10, 20)]
    assert it(range(10)).skip(1).skip(1).collect() == [*range(2, 10)]


def test_peekable():
    xs = 1, 2, 3
    i = it(xs).peekable()

    assert i.peek() == xs[0]
    assert i.next() == xs[0]

    assert i.next() == xs[1]

    assert i.peek() == xs[2]
    assert i.peek() == xs[2]

    assert i.next() == xs[2]

def test_max():
    assert it((1, 2, 3, 4)).max() == 4
    assert it('asdf').max() == 's'
    assert it((MyItem(1), MyItem(2), MyItem(3))).max() == MyItem(3)


def test_min():
    assert it((1, 2, 3, 4)).min() == 1
    assert it('asdf').min() == 'a'
    assert it((MyItem(1), MyItem(2), MyItem(3))).min() == MyItem(1)


def test_chain():
    assert it((1, 2, 3)).chain((4, 5, 6)).collect() == [1, 2, 3, 4, 5, 6]
    assert it('as').chain((3.1, 2.4)).collect() == ['a', 's', 3.1, 2.4]


def test_filter():
    func = lambda x: x > 2; data = 1, 2, 3, 4, 5
    assert it(data).filter(func).collect() == list(filter(func, data))


def test_cycle():
    assert it(range(3)).cycle().take(6).collect() == [0, 1, 2, 0, 1, 2]
    assert it('abc').cycle().take(6).collect() == ['a', 'b', 'c', 'a', 'b', 'c']


def test_all():
    assert not it('asdf').all(lambda x: x > 'a')
    assert it('bsdf').all(lambda x: x > 'a')


def test_any():
    assert it('asdf').any(lambda x: x > 'a')
    assert not it('bsdf').all(lambda x: x <= 'a')


def test_count():
    assert it('abc').count() == 3
    assert it('abc').skip(1).count() == 2
    assert it('abc').skip(1).take(2).count() == 2


def test_last():
    assert it('abc').last() == 'c'
    assert it('abc').skip(1).last() == 'c'
    assert it('abc').cycle().take(8).last() == 'b'


def test_nth():
    assert it('abc').nth(3) == 'c'
    assert it('abc').skip(1).nth(2) == 'c'
    assert it('abc').cycle().nth(23) == 'b'


def test_step():
    assert it('abcdef').step_by(1).collect() == ['a', 'b', 'c', 'd', 'e', 'f']
    assert it('abcdef').step_by(2).collect() == ['a', 'c', 'e']
    assert it('abcdef').step_by(3).collect() == ['a', 'd']
    assert it('abcdef').cycle().step_by(3).nth(17) == 'a'


def test_map():
    assert it('abc').map(lambda x: x.upper()).collect() == ['A', 'B', 'C']
    assert it((1, 2, 3)).map(lambda x: x ** x).collect() == [1, 4, 27]


def test_go():
    seen = []
    it('abc').inspect(lambda x: seen.append(x.upper())).go()
    assert seen == ['A', 'B', 'C']
    seen = []
    it('abc').skip(1).take(1).inspect(lambda x: seen.append(x.upper())).go()
    assert seen == ['B']


def test_inspect():
    seen = []
    it('abc').inspect(lambda x: seen.append(x.upper())).go()
    assert seen == ['A', 'B', 'C']


def test_sum():
    assert it((1, 2, 3)).sum() == 6
    assert it((1, 2, 3)).skip(1).sum() == 5
    assert it((1, 2, 3)).cycle().take(22).sum() == 43

