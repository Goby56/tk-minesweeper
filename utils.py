class Utils:

    def get_surrounding_indices(row: int, column: int, upper_limit_row: int, upper_limit_column: int):
        for r in range(max(row-1, 0), min(row+2, upper_limit_row)):
            for c in range(max(column-1, 0), min(column+2, upper_limit_column)):
                yield (r, c)

    def get_matrix_indicies(rows, columns):
        for r in range(rows):
            for c in range(columns):
                yield (r,c)

if __name__ == "__main__":
    print("You bad, wrong file")