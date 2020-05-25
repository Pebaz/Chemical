import sys, math
from enum import Enum, auto


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


class Ordering(Enum):
    Equal = auto()
    Less = auto()
    Greater = auto()


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


# Allow all iterators and aggregators to be available upon import
from . aggregators import *
from . iterators import *
