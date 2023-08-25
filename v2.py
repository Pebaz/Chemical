class Ag: ...
class It:
    iterators = 'next', 'skip', 'take', 'step_by', 'rev'
    aggregators = 'count',
    def __init__(self, *args, **kwargs):
        self.input = args, kwargs
        self.instructions = []
    def __dir__(self):
        "Needed since __getattr__ is overridden"
        return self.__dict__
    def __getattr__(self, attr):
        # Surprisingly, there are a lot of probes to __getattr__ (ipython, etc.)
        if attr not in self.iterators and attr not in self.aggregators:
            return
        self.instructions.append(attr)
        return self
    def __call__(self, *args, **kwargs):
        if self.instructions and isinstance(self.instructions[-1], str):
            command = self.instructions.pop()
            if command not in self.aggregators:
                self.instructions.append((command, args, kwargs))
            else:
                return self.aggregate(command, *args, **kwargs)
        return self
    # Instructions take arguments as input and incrementally produce output
    def __iter__(self):
        # In order for pausing and resuming to work, these have to be fields
        input = self.input[0][0]
        forward, backward = iter(input), reversed(input)
        reversing = False
        consume = lambda: (next(forward), next(backward))[reversing]
        index = 0  # TODO(pbz): Not strictly needed but may be useful
        step = 1
        for instruction in self.instructions:
            match instruction:
                case ['skip', [amount], _]:
                    index += amount
                    for _ in range(amount):
                        consume()
                case ['take', [amount], _]:
                    for _ in range(amount):
                        index += step
                        yield consume()
                case ['step_by', [amount], _]:
                    step = amount
                case ['rev', *_]:
                    reversing = not reversing
                case _:
                    raise Exception("Unreachable")
        try:
            while True:
                yield consume()
                index += step
                for _ in range(step - 1):
                    consume()
        except StopIteration:
            ...
    # Aggregators take self as input and produces a singular output
    def aggregate(self, command, *args, **kwargs):
        if command == 'count':
            count = 0
            for _ in self:
                count += 1
            return count

# Syntax example: it([1, 2, 3])( ??? )
# Exception.with_traceback()
# How can users implement their own iterators or aggregators?

it = It([1, 2, 3, 4, 5])
it = it.skip(1).step_by(2).take(2)
print(it.count())
print(list(It([1, 2, 3, 4, 5]).rev().step_by(2).take(2)))
