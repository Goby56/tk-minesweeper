import numpy as np
from utils import Utils

class Solver:
    def __init__(self, board: np.ndarray, start_pos: tuple):
        self.board_values = np.array(board, dtype=int)
        self.board_states = np.zeros(board.shape, dtype=int)

        self.rows, self.columns = board.shape

        # self.instructions = None

        self.open_cell(start_pos[0], start_pos[1])

    def __repr__(self):
        char_arr = [""]
        for r in range(self.rows):
            for c in range(self.columns):
                if self.board_states[r,c] == -1:
                    char_arr.append("F")
                elif self.board_states[r,c] == 1:
                    if self.board_values[r,c] == -1:
                        char_arr.append("B")
                        continue
                    char_arr.append(str(self.board_values[r,c]))
                else:
                    char_arr.append("□")
            char_arr.append("\n")
        return " ".join(char_arr)

    def solve_board(self):
        # self.instructions = []
        while not self.board_is_solved():
            if self.simple_search() == False: # No more easy openenings
                if self.pair_search() == False: # No 100% guaranteed solution
                    # print(self)
                    return False
        return True
        # print(self)

    def simple_search(self):
        for row, column in Utils.get_matrix_indicies(self.rows, self.columns):
            if self.board_states[row,column] == 1 and str(self.board_values[row,column]) in "123456789":
                unopened_set = self.unopened_neighbors(row, column)
                flagged_set = self.flagged_neighbors(row, column)

                if self.board_values[row,column] - len(flagged_set) == len(unopened_set):
                    # print("unopened set", row, column, unopened_set)
                    for r, c in unopened_set:
                        self.flag_cell(r, c)

                unopened_set = self.unopened_neighbors(row, column)
                flagged_set = self.flagged_neighbors(row, column)

                if self.board_values[row,column] == len(flagged_set) and len(unopened_set) != 0:
                    # print("flagged set", row, column, flagged_set)
                    for r, c in unopened_set:
                        self.open_cell(r, c)
                    return True
        return False

    def pair_search(self):
        for row1, column1 in Utils.get_matrix_indicies(self.rows, self.columns):
            if self.board_states[row1,column1] != 1 or str(self.board_values[row1,column1]) not in "123456789":
                continue
            unopened_a = self.unopened_neighbors(row1, column1)
            if len(unopened_a) == 0:
                continue

            for row2, column2 in Utils.get_surrounding_indices(row1, column1, self.rows, self.columns):
                if self.board_states[row1,column1] != 1 or str(self.board_values[row1,column1]) not in "123456789":
                    continue
                unopened_b = self.unopened_neighbors(row2, column2)
                if len(unopened_b) == 0:
                    continue

                value_a = self.board_values[row1,column1] - len(self.flagged_neighbors(row1, column1))
                value_b = self.board_values[row2,column2] - len(self.flagged_neighbors(row2, column2))

                if value_a - value_b == len(unopened_a - unopened_b) and value_a - value_b != 0:
                    # print("a - b", row1, column1, "and", row2, column2, unopened_a - unopened_b)
                    for r, c in (unopened_a - unopened_b):
                        self.flag_cell(r, c)
                    for r, c in (unopened_b - unopened_a):
                        self.open_cell(r, c)
                    return True
        return False



    def unopened_neighbors(self, row, column):
        return set(filter(lambda pos: self.board_states[pos[0]][pos[1]] == 0, 
                                Utils.get_surrounding_indices(row, column, self.rows, self.columns)))
    
    def flagged_neighbors(self, row, column):
        return set(filter(lambda pos: self.board_states[pos[0]][pos[1]] == -1, 
                                Utils.get_surrounding_indices(row, column, self.rows, self.columns)))

    def board_is_solved(self):
        rows, columns = self.board_states.shape
        number_of_opened_cells = 0
        for r, c in Utils.get_matrix_indicies(self.rows, self.columns):
            number_of_opened_cells += self.board_states[r,c]
        return number_of_opened_cells == rows*columns

    def open_cell(self, row: int, column: int):
        if self.board_states[row,column] in [-1, 1]:
            return # If cell already is opened or flagged
        self.board_states[row,column] = 1 # Acts as opening the cell
        # print("OPENED", row, column)
        # if self.instructions != None:
        #     self.instructions.append(("OPEN", row, column))
        if self.board_values[row,column] == -1:
            return # If cell is bomb
        if self.board_values[row,column] == 0:
            # If there aren't any surrounding bombs nearby, reveal recursively
            for r, c in Utils.get_surrounding_indices(row, column, self.rows, self.columns):
                self.open_cell(r, c)

    def flag_cell(self, row: int, column: int):
        self.board_states[row,column] = -1
        # self.instructions.append(("FLAG", row, column))
        # print("FLAGGED", row, column)

if __name__ == "__main__":
    print("You bad, wrong file")