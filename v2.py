class It:
    commands = 'skip', 'take'
    def __init__(self, *args, **kwargs):
        self.input = args, kwargs
        self.instructions = []
    def __dir__(self):
        "Needed since __getattr__ is overridden"
        return self.__dict__
    def __getattr__(self, attr):
        if attr not in self.commands:
            return
        self.instructions.append(attr)
        return self
    def __call__(self, *args, **kwargs):
        if self.instructions and isinstance(self.instructions[-1], str):
            self.instructions.append((self.instructions.pop(), args, kwargs))
        return self
    def __iter__(self):
        collection = self.input[0][0]
        index = 0
        for instruction in self.instructions:
            match instruction:
                case ['skip', [amount], kwargs]:
                    index += amount
                case ['take', [amount], kwargs]:
                    for _ in range(amount):
                        yield collection[index]
                        index += 1
                case _:
                    raise Exception("Unreachable")

it = It([1, 2, 3])
it = it.skip(1).take(2)
print(it)
print(list(it))
