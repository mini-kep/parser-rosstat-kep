from kep.util import iterate, make_label

__all__ = ['CommandSet']

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
        if method == 'var':
            name = arg
        elif method in ['units', 'force_units']:
            units = iterate(arg)
    return [make_label(name, unit) for unit in units]


class CommandSet:
    """Provide class manipulation functions or list of labels
       based on parsing commands from yaml file.
    """
    def __init__(self, commands: str):
        """
        Args
        ====        
        commands(list) - parsing commands as list of strings or dictionaries. 
        """
        self.commands = iterate(commands)

    @property
    def methods(self):
        """List of functions to manipulate `kep.parser.Worker` instance."""
        return [_as_function(c) for c in self.commands]

    @property
    def labels(self):
        """List of labels contained in parsing commands."""
        return _labels(self.commands)
