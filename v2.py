class It:
    commands = 'next', 'skip', 'take', 'step_by'
    def __init__(self, *args, **kwargs):
        self.input = args, kwargs
        self.instructions = []
    def __dir__(self):
        "Needed since __getattr__ is overridden"
        return self.__dict__
    def __getattr__(self, attr):
        # Surprisingly, there are a lot of probes to __getattr__ (ipython, etc.)
        if attr not in self.commands:
            return
        self.instructions.append(attr)
        return self
    def __call__(self, *args, **kwargs):
        if self.instructions and isinstance(self.instructions[-1], str):
            self.instructions.append((self.instructions.pop(), args, kwargs))
        return self
    def __iter__(self):
        # In order for pausing and resuming to work, these have to be fields
        collection = self.input[0][0]
        index = 0
        step = 1
        for instruction in self.instructions:
            match instruction:
                case ['next', args, kwargs]:
                    yield collection[index]
                    index += amount
                case ['skip', [amount], kwargs]:
                    index += amount
                case ['take', [amount], kwargs]:
                    for _ in range(amount):
                        yield collection[index]
                        index += step
                case ['step_by', [amount], kwargs]:
                    step = amount
                case _:
                    raise Exception("Unreachable")
            if index == len(collection):
                return

    # TODO(pbz): If the instructions are defined on the class, do user's care?
    def skip(self, amount):
        # The utility of this is to validate parameters at first call when
        # building the iterator chain and then when actually iterating, perform
        # the instruction
        if not self.iterating:
            return

# Syntax example: it([1, 2, 3])( ??? )
# Exception.with_traceback()
# How can users implement their own iterators or aggregators?

it = It([1, 2, 3, 4, 5])
it = it.skip(1).step_by(2).take(2)
print(it)
print(list(it))
print(it.next())
