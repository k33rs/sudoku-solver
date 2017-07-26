from .errors import ViolationException


class Markup:
    def __init__(self, board):
        self.board = board
        self.queue = []

        # initialize queue of non empty cells
        for row in range(9):
            for col in range(9):
                if len(self.board[9 * row + col]) == 1:
                    self.cell_enqueue(row, col)

    def cell_enqueue(self, row, col):
        self.queue.append((row, col))

    def markup(self, search):
        for cell in self.queue:
            row, col = cell[0], cell[1]
            try:
                self._markup_row(row, col, search)
                self._markup_col(row, col, search)
                self._markup_box(row, col, search)

            except ViolationException:
                break

        self.queue.clear()

    def _markup_row(self, row, col, search):
        val = self.board[9 * row + col][0]
        # iterate over row
        for c in range(9):
            markup = self.board[9 * row + c]

            if len(markup) > 1:
                try:
                    markup.remove(val)
                except ValueError:
                    continue

                if search.search_path_exists():
                    search.crossout_append(row, c, val)

                if len(markup) == 1:
                    if search.search_path_exists():
                        search.violation_check(row, c)

                    self.cell_enqueue(row, c)

    def _markup_col(self, row, col, search):
        val = self.board[9 * row + col][0]
        # iterate over column
        for r in range(9):
            markup = self.board[9 * r + col]

            if len(markup) > 1:
                try:
                    markup.remove(val)
                except ValueError:
                    continue

                if search.search_path_exists():
                    search.crossout_append(r, col, val)

                if len(markup) == 1:
                    if search.search_path_exists():
                        search.violation_check(r, col)

                    self.cell_enqueue(r, col)

    def _markup_box(self, row, col, search):
        val = self.board[9 * row + col][0]
        # get index of upper-left cell
        i = (row // 3) * 3
        j = (col // 3) * 3
        # iterate over box
        for r in range(i, i + 3):
            for c in range(j, j + 3):
                markup = self.board[9 * r + c]
                if len(markup) > 1:
                    try:
                        markup.remove(val)
                    except ValueError:
                        continue

                    if search.search_path_exists():
                        search.crossout_append(r, c, val)

                    if len(markup) == 1:
                        if search.search_path_exists():
                            search.violation_check(r, c)

                        self.cell_enqueue(r, c)

    def forced_numbers(self, search):
        self.markup(search)

        for row in range(9):
            for col in range(9):
                markup = self.board[9 * row + col]

                if len(markup) > 1:
                    for val in markup:
                        if self._forced_in_row(val, row, col) or \
                                self._forced_in_col(val, row, col) or \
                                self._forced_in_box(val, row, col):
                            markup.clear()
                            markup.append(val)
                            self.cell_enqueue(row, col)
                            break

    def _forced_in_row(self, val, row, col):
        for c in range(9):
            if c != col:
                markup = self.board[9 * row + c]
                if val in markup:
                    return False

        return True

    def _forced_in_col(self, val, row, col):
        for r in range(9):
            if r != row:
                markup = self.board[9 * r + col]
                if val in markup:
                    return False

        return True

    def _forced_in_box(self, val, row, col):
        # get index of upper-left cell
        i = (row // 3) * 3
        j = (col // 3) * 3
        # iterate over square
        for r in range(i, i + 3):
            for c in range(j, j + 3):
                if not (r == row and c == col):
                    markup = self.board[9 * r + c]
                    if val in markup:
                        return False

        return True
