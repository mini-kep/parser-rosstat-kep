from kep.util import file_or_string, str_to_yaml, iterate
from kep.label import make_label

class Command():
    def __init__(self, command: str):
        if isinstance(command, str):
             self.method = command
             self.arg = None
        if isinstance(command, dict):     
            for self.method, self.arg in command.items():
                break
    
    def __repr__(self):
        return str((self.method, self.arg))
    
    def as_func(self):
        def foo(cls):
            f = getattr(cls, self.method)
            if self.arg:
                f(self.arg)
            else:
                f()
        return foo    


class CommandList:
    def __init__(self, incoming: str):
        doc = file_or_string(incoming)
        self._commands = str_to_yaml(doc)

    def list(self):
        return [Command(x) for x in self._commands]
    
    def functions(self):
        return [x.as_func() for x in self.list()]        

    def _labels(self):
        for c in self.list():     
            if c.method == 'set_name':
                name = c.arg
            elif c.method in ['set_units', 'assign_units']:
                units = iterate(c.arg)
            elif c.method == 'push':
                for unit in units:
                    yield make_label(name, unit)

    @property 
    def labels(self):
        return list(self._labels())
