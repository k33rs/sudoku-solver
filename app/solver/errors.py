class ViolationException(Exception):
    def __init__(self, row, col):
        self.row = row
        self.col = col


class NoSolutionException(Exception):
    def __init__(self, message):
        self.message = message
