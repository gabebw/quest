# Quest-specific exception classes

class QuestOperationNotAllowedException(Exception):
    """
    Raised when user asks to run an operation and we can't do it, e.g.
    DRILLDOWN when we can't drill down any more.
    """
    def __init__(self, value):
        self.parameter = value
    def __str__(self):
        return repr(self.parameter)
