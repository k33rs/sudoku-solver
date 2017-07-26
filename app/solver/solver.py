import copy

from .backtrack_search import BacktrackSearch
from .errors import NoSolutionException
from .markup import Markup
from .preemptive_set import PreemptiveSetProxy


class SolverIO:
    @staticmethod
    def from_file(filein):
        cells = []
        for row in range(9):
            line = filein[row]
            for col in range(9):
                val = int(line[col])
                if val != 0:
                    cell = row, col, val
                    cells.append(cell)

        return cells

    @staticmethod
    def from_list(str_puzzle):
        cells = []
        for row in range(9):
            for col in range(9):
                index = row * 9 + col
                val = str_puzzle[index]
                if val != '':
                    cell = row, col, int(val)
                    cells.append(cell)

        return cells

    @staticmethod
    def to_list(int_puzzle):
        str_puzzle = []
        for i in int_puzzle:
            if i == 0:
                str_puzzle.append('')
            else:
                str_puzzle.append(str(i))

        return str_puzzle


class Solver:
    def __init__(self, cells):
        self.board = [list(range(1, 10)) for i in range(9 ** 2)]

        for e in cells:
            row = e[0]
            col = e[1]
            val = e[2]
            self.board[9 * row + col] = [val]

    def solve(self):
        markup = Markup(self.board)
        preemptive_set = PreemptiveSetProxy(self.board)
        search = BacktrackSearch(self.board, markup, preemptive_set)
        # step 1: find all forced numbers in the puzzle
        markup.forced_numbers(search)
        # step 2: markup the puzzle
        markup.markup(search)
        # step 3: iteratively search for preemptive sets (or make a random choice)
        while not self._solved():
            # find preemptive set and cross out
            preemptive_set.find_and_crossout(markup, search)
            # generate search path on the fly
            if preemptive_set.failed():
                try:
                    search.position()
                except NoSolutionException:
                    return False

                search.search()

            # update markup
            markup.markup(search)

        return True

    def _solved(self):
        for row in range(9):
            for col in range(9):
                if len(self.board[9 * row + col]) != 1:
                    return False

        return True

    def get_board(self):
        board = copy.deepcopy(self.board)

        for i in range(9):
            for j in range(9):
                k = 9 * i + j
                if len(board[k]) == 1:
                    board[k] = board[k][0]
                else:
                    board[k] = 0

        return board

    def __str__(self):
        board = self.get_board()
        to_str = str()

        for i in range(9):
            to_str += str(board[9 * i: 9 * i + 9]) + '\n'

        return to_str
