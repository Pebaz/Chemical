from chemical import it, trait

@trait
def blubber(self):
    return 42 + self.count()

def test_traits():
    assert it('abc').blubber() == 45
