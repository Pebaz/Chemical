# Chemical

Rust-Style Iterators in Python!

> Compose iterator sequences like chemical compounds!

## Usage

```python
>>> from chemical import it
>>> [*it(range(100)).skip(10).take(10)]
[10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
>>> 
```
