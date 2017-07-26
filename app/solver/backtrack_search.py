import bisect
import copy
import math

from .errors import ViolationException, NoSolutionException


class BacktrackSearch:
    def __init__(self, board, markup, preemptive_set):
        self.board = board
        self.markup = markup
        self.preemptive_set = preemptive_set
        self.children_cells = []
        self.search_path = None
        self.violation_occurred = False

    def position(self):
        if not self.search_path_exists():
            preemptive_pair = self.preemptive_set.find(pair=True)
            cell = self._next_preemptive_cell(
                preemptive_pair, self.children_cells
            )

            if cell is None:
                cell = self._next_empty_cell(self.children_cells)
                self.children_cells.append(cell)
            else:
                self.children_cells.extend(preemptive_pair.cells)

            parent_cells = [cell]
            self.search_path = SearchPath(
                self.board, self.markup, cell, parent_cells)

        elif not self.violation_occurred:
            preemptive_pair = self.preemptive_set.find(pair=True)
            cell = self._next_preemptive_cell(
                preemptive_pair,
                self.search_path.parent_cells + self.search_path.children_cells
            )

            if cell is None:
                cell = self._next_empty_cell(
                    self.search_path.parent_cells + self.search_path.children_cells
                )
                self.search_path.children_cells.append(cell)
            else:
                self.search_path.children_cells.extend(preemptive_pair.cells)

            parent_cells = copy.copy(self.search_path.parent_cells)
            parent_cells.append(cell)
            self.search_path.child = SearchPath(
                self.board, self.markup, cell, parent_cells, self.search_path
            )
            self.search_path = self.search_path.child

        else:
            self.violation_occurred = False

    def search(self):
        self.search_path.search()

    def delete_search_path(self):
        self.search_path.index += 1

        while self.search_path_exists() and self.search_path.dead_end():
            self.search_path.undo_crossouts()
            self.search_path = self.search_path.delete()

        if self.search_path_exists():
            self.search_path.undo_crossouts()

    def crossout_append(self, row, col, val):
        self.search_path.crossout_append(row, col, val)

    def violation_check(self, row, col):
        self.violation_occurred = self._row_violation(row, col) or \
            self._col_violation(row, col) or \
            self._box_violation(row, col)

        if self.violation_occurred:
            self.delete_search_path()
            raise ViolationException(row, col)

    def search_path_exists(self):
        return self.search_path is not None

    @staticmethod
    def _next_preemptive_cell(preemptive_pair, search_cells):
        if preemptive_pair is None:
            return None

        cell = preemptive_pair.cells[0]
        if cell in search_cells:
            return None

        return cell

    def _next_empty_cell(self, search_cells):
        min_markup_len = math.inf
        min_cell = None

        for row in range(9):
            for col in range(9):
                cell = row, col
                markup = self.board[9 * row + col]
                if 1 < len(markup) < min_markup_len and cell not in search_cells:
                    min_cell = cell

        if min_cell is None:
            raise NoSolutionException

        return min_cell

    def _new_search_path(self, cell, parent_cells):
        self.search_path = SearchPath(
            self.board, self.markup, cell, parent_cells)

    def _child_add(self, cell, parent_cells):
        self.search_path.child = SearchPath(
            self.board,
            self.markup,
            cell,
            parent_cells,
            self.search_path
        )
        self.search_path = self.search_path.child

    def _row_violation(self, row, col):
        val = self.board[9 * row + col][0]

        for c in range(9):
            markup = self.board[9 * row + c]
            if c != col and len(markup) == 1 and val == markup[0]:
                return True

        return False

    def _col_violation(self, row, col):
        val = self.board[9 * row + col][0]

        for r in range(9):
            markup = self.board[9 * r + col]
            if r != row and len(markup) == 1 and val == markup[0]:
                return True

        return False

    def _box_violation(self, row, col):
        val = self.board[9 * row + col][0]
        # get index of upper-left cell
        i = (row // 3) * 3
        j = (col // 3) * 3
        # iterate over box
        for r in range(i, i + 3):
            for c in range(j, j + 3):
                markup = self.board[9 * r + c]
                if r != row and c != col and len(markup) == 1 and val == markup[0]:
                    return True

        return False


class SearchPath:
    def __init__(self, board, markup, cell, parent_cells, parent=None):
        self.board = board
        self.markup = markup
        self.row, self.col = cell[0], cell[1]
        self.cell_markup = self.board[9 * self.row + self.col]
        self.cell_markup_len = len(self.cell_markup)
        self.cell = cell
        self.index = 0
        self.crossouts = dict()
        self.parent = parent
        self.child = None
        self.parent_cells = parent_cells
        self.children_cells = []

    def search(self):
        for i in range(0, len(self.cell_markup)):
            if i != self.index:
                self.crossout_append(self.row, self.col, self.cell_markup[i])

        search_choice = self.cell_markup[self.index]
        self.cell_markup.clear()
        self.cell_markup.append(search_choice)
        self.markup.cell_enqueue(self.row, self.col)

    def undo_crossouts(self):
        for c in self.crossouts:
            row = c[0]
            col = c[1]
            values = self.crossouts[c]
            markup = self.board[9 * row + col]

            for val in values:
                bisect.insort_left(markup, val)

        self.crossouts.clear()

    def delete(self):
        # gets called only when this search path is finished
        self.parent.index += 1
        self.parent.child = None
        return self.parent

    def dead_end(self):
        return self.index >= self.cell_markup_len

    def crossout_append(self, row, col, val):
        if self.crossouts.get((row, col)) is None:
            self.crossouts[(row, col)] = [val]
        else:
            self.crossouts[(row, col)].append(val)
