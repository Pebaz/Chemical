# Chemical

Rust-Style Iterators in Python!

> Compose iterator sequences like chemical compounds!

## Quickstart

```python
>>> from chemical import it

>>> my_iter = it([1, 2, 3])
>>> my_iter.next()
1
>>> my_iter.next()
2
>>> my_iter.next()
3

>>> it('abc').map(lambda x: x.upper()).collect(str)
'ABC'

>>> it('abc').inspect(print).go()
a
b
c

>>> for num in it(range(100)).skip(10).take(10).rev().step_by(4):
...     print(num)
19
15
11

>>> # Same as above but written as an expression:
>>> it(range(100)).skip(10).take(10).rev().step_by(4).for_each(print).go()
19
15
11

>>> # Large Chemical compositions can span multiple lines using parentheses:
>>> (it(range(100)
...      .skip(10)
...      .take(10)
...      .rev()
...      .step_by(4)
...      .for_each(print)
...      .go()
... )
19
15
11
```

## About

Chemical takes heavy inspiration from the iterators that can be found in the
[Rust Programming Language](https://www.rust-lang.org/). Chemical provides
composable, customizable, and powerful iterators that can be combined, chained,
aggregated, and so much more.

Although Python has very powerful iterators already, Chemical provides a way to
programatically compose them to create highly compact but comprehendible
behaviors.

You can even add your own "traits" to the `it` class at runtime and they will be
available for use anywhere in your program! This allows you to create custom
functionality without having to use your own type derived from `it`.

## Installation

```bash
$ pip install chemical
```

> Chemical has been tested on:
> * Windows
> * MacOS
> * Linux
> * Python 3.6
> * Python 3.7
> * Python 3.8

To run the unit tests:

```bash
$ git clone https://github.com/Pebaz/Chemical
$ cd Chemical
$ pip install -r requirements.txt
$ pytest
```

## Documentation

You can view the generated documentation
[here](https://pebaz.github.io/Chemical/index.html).

You can also look at the source code for more insight on how you can extend `it`
to have more iterators and aggregators specific to your own application.

The unit tests also provide an abundant amount of examples as they cover every
iterator/aggregator in Chemical.
