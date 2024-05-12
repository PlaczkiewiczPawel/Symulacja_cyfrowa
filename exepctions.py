class MyProjectError(Exception):
    """A base class for MyProject exceptions."""

class Beta_too_small(MyProjectError):
    def __init__(self, *args):
        super().__init__(*args)