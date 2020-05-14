# Chemical

Rust-Style Iterators in Python!

> Compose iterator sequences like chemical compounds!

## Installation

```bash
$ pip install chemical
```

> Please note that Chemical was designed to work with Python 3.8+.

## Usage

```python
>>> from chemical import it
>>> [*it(range(100)).skip(10).take(10)]
[10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
>>>
```

