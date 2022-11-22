import mss.tools
import mss
import numpy
from PIL import Image
from PIL import ImageOps

from Board import *


def print_board(b):
    """

    """
    size = numpy.shape(b)
    print("|----TETRIS--BOARD----|")
    for y in range(size[0]):  # ITERATE ROWS
        print("|", end="")
        for x in range(size[1]):  # ITERATE COLS
            if b[y, x] > 0:
                print(" #", end="")
            else:
                print("  ", end="")
        print(" |")
    print("|---------------------|")


class Tetris_Game:
    """
    A class to contain the board state of a Tetr.io instance.

    ATTRIBUTES
    ----------
    board : numpy array
        contains board state, i.e. the state of previously placed pieces

    current_piece : string
        piece that is about to be placed

    hold_piece : string
        piece that is currently being held

    hold_state : int
        is 1 if the hold piece can be swapped, 0 otherwise

    monitor : dict{string : int}
        defines section of screen to screenshot

    piece_colour : dict{int : string}
        converts greyscale colour to corresponding piece

    queue : list[string]
        upcoming five pieces

    sct : MSS
        mss instance for screenshots

    METHODS
    -------
    update():
        update board state

    evaluate():
        simulates all possible moves and evaluates them with a given heuristic

    print_state():
        prints the tetris board, current/hold piece and queue
    """

    def __init__(self, monitor, piece_colour):
        """
        Constructs all the necessary attributes the board.

        PARAMETERS
        ----------
            monitor : dict{string : int}
        defines section of screen to screenshot

            piece_colour : dict{int : string}
            converts greyscale colour to corresponding piece
        """

        self.sct = mss.mss()
        self.monitor = monitor
        self.piece_colour = piece_colour

        # 20 is number of rows, 10 is number of cols
        self.board = Board()
        self.current_piece = ""
        self.hold_piece = ""
        self.hold_state = 1
        self.queue = ["", "", "", "", ""]

        # Define shape of all pieces
        #   Pieces will be defined from state 0: horizontal
        #   Then rotated counterclockwise until no new states are found
        #   Piece state denoted by "{piece}{state_number}", e.g. L0, L1
        # Eventually convert this to something I can read in
        # NEED TO FINISH THIS
        self.piece_shape = {}
        self.piece_shape["I0"] = numpy.ones([1, 4])  # flat
        self.piece_shape["I1"] = numpy.ones([4, 1])  # vert

        self.piece_shape["O0"] = numpy.ones([2, 2])  # O

        self.piece_shape["T0"] = numpy.array([[0, 1, 0],
                                              [1, 1, 1]])
        self.piece_shape["T1"] = numpy.array([[0, 1],
                                              [1, 1],
                                              [0, 1]])
        self.piece_shape["T2"] = numpy.array([[1, 1, 1],
                                              [0, 1, 0]])
        self.piece_shape["T3"] = numpy.array([[1, 0],
                                              [1, 1],
                                              [1, 0]])

        self.piece_shape["S0"] = numpy.array([[0, 1, 1],
                                              [1, 1, 0]])
        self.piece_shape["S1"] = numpy.array([[1, 0],
                                              [1, 1],
                                              [0, 1]])

        self.piece_shape["Z0"] = numpy.array([[1, 1, 0],
                                              [0, 1, 1]])
        self.piece_shape["Z1"] = numpy.array([[0, 1],
                                              [1, 1],
                                              [1, 0]])

        self.piece_shape["J0"] = numpy.array([[1, 0, 0],
                                              [1, 1, 1]])
        self.piece_shape["J1"] = numpy.array([[0, 1],
                                              [0, 1],
                                              [1, 1]])
        self.piece_shape["J2"] = numpy.array([[1, 1, 1],
                                              [0, 0, 1]])
        self.piece_shape["J3"] = numpy.array([[1, 1],
                                              [1, 0],
                                              [1, 0]])

        self.piece_shape["L0"] = numpy.array([[0, 0, 1],
                                              [1, 1, 1]])
        self.piece_shape["L1"] = numpy.array([[1, 1],
                                              [0, 1],
                                              [0, 1]])
        self.piece_shape["L2"] = numpy.array([[1, 1, 1],
                                              [1, 0, 0]])
        self.piece_shape["L3"] = numpy.array([[1, 0],
                                              [1, 0],
                                              [1, 1]])

        # The number of rotated states a piece can take
        self.num_piece_states = {}
        self.num_piece_states["I"] = 2
        self.num_piece_states["O"] = 1
        self.num_piece_states["T"] = 4
        self.num_piece_states["S"] = 2
        self.num_piece_states["Z"] = 2
        self.num_piece_states["J"] = 4
        self.num_piece_states["L"] = 4

    def update(self):
        """
        Function to update the board state.

        PARAMETERS
        ----------
        None

        RETURNS
        -------
        None
        """
        # Get screenshot of the board, including queue, current piece and hold
        board_picture_bgra = self.sct.grab(self.monitor)
        board_picture_rgb = Image.frombytes(
            "RGB",
            board_picture_bgra.size,
            board_picture_bgra.bgra,
            "raw",
            "BGRX")
        board_picture_bw = ImageOps.grayscale(board_picture_rgb)

        # Find board layout from screenshot
        for y in range(20):  # ITERATE ROWS
            for x in range(10):  # ITERATE COLS
                pix = board_picture_bw.getpixel((207 + 36 * x, 127 + 36 * y))
                if pix > 40:
                    self.board.update_state(y, x, 1)
                else:
                    self.board.update_state(y, x, 0)
        self.board.update()

        # Get hold piece
        hold_pix = board_picture_bw.getpixel((98, 199))
        if hold_pix == 0:  # No piece in hold
            self.hold_piece = ""
        elif hold_pix > 0 and hold_pix < 90:  # Piece just held
            self.hold_piece = "U"
        else:  # Piece in hold
            self.hold_piece = self.piece_colour[hold_pix]

        # Get current piece
        # Will need to change if gravity gets high?? Test
        # can do based on queue, only need to know first ever piece
        current_pix = board_picture_bw.getpixel((356, 38))
        if current_pix == 0:
            self.current_piece = ""
        else:
            self.current_piece = self.piece_colour[current_pix]

        # Get current queue
        for i in range(5):
            queue_pix = board_picture_bw.getpixel((650, 199 + 109 * i))
            self.queue[i] = self.piece_colour[queue_pix]

    def evaluate(self):
        """
        BRUH
        """
        # Get number of possible orientations
        num_states = self.num_piece_states[self.current_piece]

        # Get current max and min row of the board
        max_row = self.board.max_row
        min_row = self.board.min_row

        # create a board to mess around with
        board_copy = numpy.copy(self.board.board)

        # Set Heuristic to minimum
        H = -99999

        # copy a board to store the best move
        # this may be redundant, but useful for visualising the move it picks
        best_move = numpy.copy(self.board.board)
        best_orientation = 0
        best_col = 0
        best_height_diff = 0
        best_clear_rows = 0
        best_num_holes = 0

        # Iterate through all piece rotations
        for s in range(num_states):
            # for s in range(1):

            # Get the piece and the shape of the piece
            piece = self.piece_shape[self.current_piece + str(s)]
            piece_shape = numpy.shape(piece)

            # Calculate the number of places it can go
            num_moves = int((10 - piece_shape[1]) / 1 + 1)

            # Iterate through all the possible moves for the current
            # orientation
            for moves in range(num_moves):
                # for moves in range(1):

                valid_upper = 0
                valid_lower = 0

                # Start at the current max height +1 and check if it's a valid spot. If yes,
                # check the spot underneath. Repeat until bottom of board is reached or a
                #  non-viable position is reached.
                found_valid = False
                for upper in range(
                        max_row - piece_shape[0],
                        21 - piece_shape[0]):
                    # section = board_copy[upper:upper + piece_shape[0],
                    #                     moves:moves + piece_shape[1]] + piece

                    section = board_copy[upper:upper + piece_shape[0],
                                         moves:moves + piece_shape[1]]

                    section_shape = numpy.shape(section)
                    # print(section_shape[0] == piece_shape[0])

                    if section_shape[0] == piece_shape[0]:
                        section = section + piece
                        if 2 not in section:
                            valid_upper = upper
                            valid_lower = upper + piece_shape[0]
                            found_valid = True
                        else:
                            break

                if found_valid:
                    # Place piece on board
                    board_copy[valid_upper:valid_lower,
                               moves:moves + piece_shape[1]] += piece

                    # Evaluate board on a given heuristic
                    clear_rows = rows_cleared(
                        board_copy, max_row)

                    cleared_board = clear_filled_rows(
                        numpy.copy(board_copy))

                    max_row = get_max_height(cleared_board)
                    min_row = get_min_height(cleared_board)

                    height_diff = min_row - max_row

                    # average_height = get_average_height(cleared_board)
                    # print(average_height)

                    # height_diff = (20 - max_row) - average_height

                    # - self.board.number_of_holes)
                    num_holes = find_holes(cleared_board)

                    roughness = get_roughness(cleared_board)

                    # Calculate H function
                    weights = [0, 3, 3, 0.5]
                    H_new = - weights[0] * height_diff - weights[1] * \
                        num_holes + weights[2] * clear_rows - weights[3] * roughness

                    if H_new > H:
                        H = H_new
                        best_move = numpy.copy(board_copy)
                        best_orientation = s
                        best_col = moves
                        best_height_diff = height_diff
                        best_clear_rows = clear_rows
                        best_num_holes = num_holes

                    # print_board(board_copy)

                    """print_board(board_copy)
                    print(f"Height difference      : {height_diff}")
                    print(f"Number of rows cleared : {clear_rows}")
                    print(f"Number of holes        : {num_holes}")
                    print(f"Heuristic H(s) = -{weights[0]}*{height_diff} - {weights[1]}*{num_holes} + {weights[2]}*{clear_rows} = {H_new}")
                    print()"""

                    board_copy[valid_upper:valid_lower,
                               moves:moves + piece_shape[1]] -= piece

        """print(f"Height difference      : {best_height_diff}")
        print(f"Number of rows cleared : {best_clear_rows}")
        print(f"Number of holes        : {best_num_holes}")
        print(f"Heuristic H(s) = -{weights[0]}*{best_height_diff} - {weights[1]}*{best_num_holes} + {weights[2]}*{best_clear_rows} = {H}")
        print()"""

        # print_board(best_move)
        return best_orientation, best_col

    def generate_moves(self, best_orientation, best_col):
        starting_col = 3
        if self.current_piece == "O":
            starting_col = 4

        # MOVEMENTS:
        # a : left
        # d : right
        # w : drop
        # j : cc rotation
        # l : c rotation
        # k : 180 flip

        # Rotation
        if best_orientation == 1:
            movement = "j"
            if self.current_piece == "I":
                starting_col += 1
        elif best_orientation == 2:
            movement = "k"
        elif best_orientation == 3:
            movement = "l"
            if self.current_piece == "T" or self.current_piece == "L" or self.current_piece == "J":
                starting_col += 1
        else:
            movement = ""

        # lateral movement
        difference = starting_col - best_col
        # print(f"Difference: {difference}")
        if difference > 0:
            # left movement
            movement += "a" * difference + "w"
        elif difference < 0:
            movement += "d" * abs(difference) + "w"
        else:
            movement += "w"

        return movement

    def print_state(self):
        """
        Function to print all board state parameters.

        PARAMETERS
        ----------
        None

        RETURNS
        -------
        None
        """
        print(f"Current Piece : {self.current_piece}")
        print(f"Hold Piece    : {self.hold_piece}")
        print(f"Queue         : {self.queue}")
        print()
        print("Board State:")
        print_board(self.board.board)
