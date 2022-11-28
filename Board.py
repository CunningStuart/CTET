import numpy


def rows_cleared(board, max_row):
    """
    rows_cleared documentation
    """
    clear_rows = 0
    row = 19

    for row in range(max_row, 20):
        if numpy.sum(board[row]) == 10:
            clear_rows += 1

    return clear_rows


def find_holes(board):
    holes = 0
    for col in board.T:
        num_blocks = int(numpy.sum(col))
        if num_blocks > 0:
            holes += (20 - numpy.argmax(col > 0)) - int(numpy.sum(col))
    return holes


def clear_filled_rows(board):
    for i, row in enumerate(board):
        if numpy.sum(row) == 10:
            board = numpy.delete(board, i, 0)
            board = numpy.vstack([numpy.zeros([1, 10]), board])
    return board


def get_max_height(board):
    for i, row in enumerate(board):
        if numpy.sum(row) > 0:
            return i
    return 20


def get_min_height(board):
    min = 0
    temp_min = 0
    for col in board.T:
        temp_min = next((i for i, x in enumerate(col) if x == 1), 20)
        if temp_min > min:
            min = temp_min
    return min


def get_average_height(board):
    average = 0
    for col in board.T:
        average += 19 - \
            (next((i for i, x in enumerate(col) if x == 1), 20) - 1)

    return average / 10


def get_roughness(board):
    total_roughness = 0
    t_board = board.T
    for c in range(9):
        col1 = 19 - \
            (next((i for i, x in enumerate(t_board[c]) if x == 1), 20) - 1)
        col2 = 19 - \
            (next((i for i, x in enumerate(t_board[c + 1]) if x == 1), 20) - 1)
        total_roughness += abs(col1 - col2)
    return total_roughness


class Board:
    """
    Board Documentation
    """

    def __init__(self):
        """
        Board init documentation
        """
        self.board = numpy.zeros((20, 10))
        self.max_row = 20
        self.min_row = 20
        self.number_of_holes = 0

    def update_state(self, y, x, new_val):
        """
        Board update documentation
        """
        self.board[y, x] = new_val

    def update(self):
        # For now the minimum row will always be 20
        # Will want to change it in the future so the "lowest point"
        # may not be an intentionally empty column

        self.max_row = get_max_height(self.board)
        self.min_row = get_min_height(self.board)
        self.number_of_holes = find_holes(self.board)
