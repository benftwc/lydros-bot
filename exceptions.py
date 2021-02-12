class CommandException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class ScanException(CommandException):
    """
    Raised if Scan command fails
    """