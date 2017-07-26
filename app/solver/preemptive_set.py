from .errors import ViolationException


class PreemptiveSetProxy:
    def __init__(self, board):
        self.row = 0
        self.col = 0
        self.cross_out_occurred = False
        self.failure = False
        self.board = board

    def find_and_crossout(self, markup, search):
        preemptive_set = self.find()

        try:
            while not (self.failure or self._cross_out(preemptive_set, markup, search)):
                preemptive_set = self.find()
        except ViolationException:
            return

    def find(self, pair=False):
        while not self.failure:
            markup = self.board[9 * self.row + self.col]
            len_cond = self._len_condition(markup, pair)

            if len_cond:
                in_row = self._find_in_row(markup, self.row, self.col, pair)
                if in_row is not None:
                    self._next_cell()
                    return in_row

                in_col = self._find_in_col(markup, self.row, self.col, pair)
                if in_col is not None:
                    self._next_cell()
                    return in_col

                in_box = self._find_in_box(markup, self.row, self.col, pair)
                if in_box is not None:
                    self._next_cell()
                    return in_box

            self._next_cell()

        if pair:
            self.failure = False

    def failed(self):
        failure = self.failure
        self.failure = False
        return failure

    def _cross_out(self, preemptive_set, markup, search):
        success = False

        for cell in preemptive_set.range:
            row = cell[0]
            col = cell[1]

            for val in preemptive_set.values:
                cell_markup = self.board[9 * row + col]

                if len(cell_markup) > 1:
                    try:
                        cell_markup.remove(val)
                    except ValueError:
                        continue

                    if search.search_path_exists():
                        search.crossout_append(row, col, val)

                    if len(cell_markup) == 1:
                        if search.search_path_exists():
                            search.violation_check(row, col)

                        markup.cell_enqueue(row, col)

                    self.cross_out_occurred = True
                    success = True

        return success

    def _next_cell(self):
        self.col += 1

        if self.col == 9:
            self.col = 0
            self.row += 1

            if self.row == 9:
                self.row = 0

                if self.cross_out_occurred:
                    self.cross_out_occurred = False
                else:
                    self.failure = True

    def _find_in_row(self, markup, row, col, pair):
        cells = [(row, col)]
        markup_set = set(markup)

        for c in range(9):
            m = self.board[9 * row + c]
            len_cond = self._len_condition(m, pair)

            if len_cond and c != col:
                m_set = set(m)

                if m_set <= markup_set:
                    cells.append((row, c))

        return self._valid_preemptive_set(markup, cells)

    def _find_in_col(self, markup, row, col, pair):
        cells = [(row, col)]
        markup_set = set(markup)

        for r in range(9):
            m = self.board[9 * r + col]
            len_cond = self._len_condition(m, pair)

            if len_cond and r != row:
                m_set = set(m)

                if m_set <= markup_set:
                    cells.append((r, col))

        return self._valid_preemptive_set(markup, cells)

    def _find_in_box(self, markup, row, col, pair):
        cells = [(row, col)]
        markup_set = set(markup)
        # get index of upper-left cell
        i = (row // 3) * 3
        j = (col // 3) * 3
        # iterate over square
        for r in range(i, i + 3):
            for c in range(j, j + 3):
                m = self.board[9 * r + c]
                len_cond = self._len_condition(m, pair)

                if len_cond and not (r == row and c == col):
                    m_set = set(m)

                    if m_set <= markup_set:
                        cells.append((r, c))

        return self._valid_preemptive_set(markup, cells)

    @staticmethod
    def _len_condition(markup, pair):
        if pair:
            return len(markup) == 2

        return len(markup) > 1

    def _valid_preemptive_set(self, markup, cells):
        if len(markup) == len(cells):
            return PreemptiveSet(self.board, markup, cells)


class PreemptiveSet:
    def __init__(self, board, values, cells):
        self.board = board
        self.values = values
        self.cells = cells
        self.range = self._range()

    def _range(self):
        range_full = []
        # get row index of first cell
        row1 = self.cells[0][0]
        range_full.extend(self._range_row(row1))
        # get column index of first cell
        col1 = self.cells[0][1]
        range_full.extend(self._range_col(col1))
        range_full.extend(self._range_box(row1, col1))

        return range_full

    def _range_row(self, row):
        range_row = []

        for k in range(1, len(self.cells)):
            r = self.cells[k][0]

            if r != row:
                return range_row

        for col in range(9):
            self._range_append_cell(range_row, row, col)

        return range_row

    def _range_col(self, col):
        range_col = []

        for k in range(1, len(self.cells)):
            c = self.cells[k][1]

            if c != col:
                return range_col

        for row in range(9):
            self._range_append_cell(range_col, row, col)

        return range_col

    def _range_box(self, row, col):
        # get index of upper-left cell
        i = (row // 3) * 3
        j = (col // 3) * 3

        range_box = []

        # check all other cells
        for k in range(1, len(self.cells)):
            r = self.cells[k][0]
            c = self.cells[k][1]

            if not (r in range(i, i + 3) and c in range(j, j + 3)):
                return range_box

        for r in range(i, i + 3):
            for c in range(j, j + 3):
                self._range_append_cell(range_box, r, c)

        return range_box

    def _range_append_cell(self, range_list, row, col):
        cell = row, col
        markup = self.board[9 * row + col]

        if len(markup) > 1 and cell not in self.cells:
            range_list.append(cell)
