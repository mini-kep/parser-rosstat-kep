from kep.util import iterate, make_label

def _extract_command_parameters(command):
    if isinstance(command, str):
        method = command
        arg = None
    elif isinstance(command, dict):
        for method, arg in command.items():
            break
    else:
        raise TypeError(command)
    return method, arg


def _as_function(command):
    method, arg = _extract_command_parameters(command)

    def foo(cls):
        f = getattr(cls, method)
        if arg:
            f(arg)
        else:
            f()
    return foo


def _labels(commands: list):
    for command in commands:
        method, arg = _extract_command_parameters(command)
        if method == 'set_name':
            name = arg
        elif method in ['set_units', 'assign_units']:
            units = iterate(arg)
    return [make_label(name, unit) for unit in units]


class CommandSet:
    """Accept a list of strings or dictionaries and provide
       class manipulation methods or list of labels.
    """
    def __init__(self, commands):
        self.commands = commands

    @property
    def methods(self):
        return [_as_function(c) for c in self.commands]

    @property
    def labels(self):
        return _labels(self.commands)
