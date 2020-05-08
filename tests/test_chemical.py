from chemical import it


def test_it():
    assert list(it(range(3))) == [0, 1, 2]
    assert list(it('abc')) == ['a', 'b', 'c']
