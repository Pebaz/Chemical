from chemical import it, trait


@trait
class Goodbye(it):
    def __init__(self, items, adder):
        it.__init__(self, items)
        self.adder = adder

    def __next__(self):
        return next(self.items) + self.adder


def test_goodbye():
    assert it('abc').goodbye('!').collect() == ['a!', 'b!', 'c!']


@trait
def blubber(self):
    return 42 + self.count()


def test_blubber():
    assert it('abc').blubber() == 45


trait('hello')(lambda self: list(self))


def test_hello():
    assert it('abc').hello() == ['a', 'b', 'c']

