# Chemical

Rust-Style Iterators in Python!

## Usage

```python
>>> from chemical import it
>>> [i for i in it(range(100)).skip(10).take(10)]
[10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
>>> 
```
