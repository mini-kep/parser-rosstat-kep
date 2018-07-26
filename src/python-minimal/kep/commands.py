from kep.util import iterate, make_label


def extract_command_parameters(command):
    if isinstance(command, str):
        method = command
        arg = None
    elif isinstance(command, dict):
        for method, arg in command.items():
            break
    else:
        raise TypeError(command)
    return method, arg


def as_function(command):
    method, arg = extract_command_parameters(command)

    def foo(cls):
        f = getattr(cls, method)
        if arg:
            f(arg)
        else:
            f()
    return foo


def labels(commands: list):
    for command in commands:
        method, arg = extract_command_parameters(command)
        if method == 'set_name':
            name = arg
        elif method in ['set_units', 'assign_units']:
            units = iterate(arg)
    return [make_label(name, unit) for unit in units]


class CommandSet:
    def __init__(self, commands):
        self.commands = commands

    @property
    def methods(self):
        return [as_function(c) for c in self.commands]

    @property
    def labels(self):
        return labels(self.commands)
