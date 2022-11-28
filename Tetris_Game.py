import mss.tools
import mss
import numpy
from PIL import Image
from PIL import ImageOps

from Board import *


def print_board(b):
    """
    Function to print Tetris board in readable format.

    PARAMETERS
    ----------
    b : numpy.array(float)
        board containing game state

    RETURNS
    -------
    None
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
    board : Board object
        Board object containing board state, i.e. the state of previously 
        placed pieces

    current_piece : string
        piece that is about to be placed

    hold_piece : string
        piece that is currently being held

    monitor : dict{string : int}
        defines section of screen to screenshot
    
    num_piece_states : dict{string : int}
        contains the number of rotations for each piece

    piece_colour : dict{int : string}
        converts greyscale colour to corresponding piece

    piece_shape : dict{string : numpy.array(float)}
        contains a numpy representation of each rotation for every piece

    queue : list[string]
        upcoming five pieces

    sct : MSS
        mss instance for screenshots

    METHODS
    -------
    init_update():
        inital update to get current and hold pieces, queue, and board
    
    update():
        update board state

    simulate_piece():
        for a given piece, simulate it's placement on the board

    calculate_heuristic():
        for a given board state, find the heuristic evaluation

    evaluate():
        find the best move for a given current piece

    generate_moves():
        for a given "best move" find the sequence of key presses that
        execute the move

    print_state():
        prints the tetris board, current/hold piece and queue
    """

    def __init__(self):
        """
        Constructs all the necessary attributes the board.

        PARAMETERS
        ----------
        NONE
        """
        self.sct = mss.mss()
        self.monitor_full_board = {
            "top": 58,
            "left": 589,
            "width": 741,
            "height": 839}
        self.monitor_last_piece = {
            "top": 654,
            "left": 1163,
            "width": 146,
            "height": 72}

        self.piece_colour = {}
        self.piece_colour[166] = "S"
        self.piece_colour[165] = "S"
        self.piece_colour[136] = "L"
        self.piece_colour[152] = "I"
        self.piece_colour[153] = "I"
        self.piece_colour[170] = "O"
        self.piece_colour[171] = "O"
        self.piece_colour[121] = "T"
        self.piece_colour[99] = "J"
        self.piece_colour[98] = "J"
        self.piece_colour[110] = "Z"
        self.piece_colour[109] = "Z"
        self.piece_colour[218] = "S"
        self.piece_colour[180] = "L"
        self.piece_colour[200] = "I"
        self.piece_colour[220] = "O"
        self.piece_colour[161] = "T"
        self.piece_colour[131] = "J"
        self.piece_colour[145] = "Z"

        # 20 is number of rows, 10 is number of cols
        self.board = Board()
        self.current_piece = ""
        self.hold_piece = ""
        self.queue = ["", "", "", "", ""]

        # Define shape of all pieces
        #   Pieces will be defined from state 0: horizontal
        #   Then rotated counterclockwise until no new states are found
        #   Piece state denoted by "{piece}{state_number}", e.g. L0, L1
        # Eventually convert this to something I can read in
        self.piece_shape = {}
        self.piece_shape["I0"] = numpy.ones([1, 4])
        self.piece_shape["I1"] = numpy.ones([4, 1])

        self.piece_shape["O0"] = numpy.ones([2, 2])

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

    def init_update(self):
        """
        Function to get the initial board state, i.e. the current piece and 
        hold piece

        PARAMETERS
        ----------
        None

        RETURNS
        -------
        None
        """
        # Get screenshot of the board, including queue, current piece and hold
        board_picture_bgra = self.sct.grab(self.monitor_full_board)
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
        current_pix = board_picture_bw.getpixel((356, 38))
        if current_pix == 0:
            self.current_piece = ""
        else:
            self.current_piece = self.piece_colour[current_pix]

        # Get current queue
        for i in range(5):
            queue_pix = board_picture_bw.getpixel((650, 199 + 109 * i))
            self.queue[i] = self.piece_colour[queue_pix]

        self.board.update()

    def update(self):
        """
        Function to get board state at any time

        PARAMETERS
        ----------
        None

        RETURNS
        -------
        None
        """
        # Get screenshot of the board, including queue, current piece and hold
        board_picture_bgra = self.sct.grab(self.monitor_full_board)
        board_picture_rgb = Image.frombytes(
            "RGB",
            board_picture_bgra.size,
            board_picture_bgra.bgra,
            "raw",
            "BGRX")
        board_picture_bw = ImageOps.grayscale(board_picture_rgb)
        # board_picture_bw.save("test_pic.png")

        self.current_piece = self.queue[0]

        temp_queue = ["", "", "", "", ""]

        # Get current queue
        for i in range(5):
            queue_pix = board_picture_bw.getpixel((650, 199 + 109 * i))
            temp_queue[i] = self.piece_colour[queue_pix]

        if self.queue == temp_queue:
            while self.queue == temp_queue:
                # print("STINKY")
                board_picture_bgra = self.sct.grab(self.monitor_full_board)
                board_picture_rgb = Image.frombytes(
                    "RGB",
                    board_picture_bgra.size,
                    board_picture_bgra.bgra,
                    "raw",
                    "BGRX")
                board_picture_bw = ImageOps.grayscale(board_picture_rgb)

                for i in range(5):
                    queue_pix = board_picture_bw.getpixel((650, 199 + 109 * i))
                    temp_queue[i] = self.piece_colour[queue_pix]

        self.queue = temp_queue

        # queue_pix = board_picture_bw.getpixel((76, 39))
        # self.queue.append(self.piece_colour[queue_pix])

    def update_old(self):
        """
        Function to update the board state. Soon to be obsolete function.

        PARAMETERS
        ----------
        None

        RETURNS
        -------
        None
        """
        # Get screenshot of the board, including queue, current piece and hold
        board_picture_bgra = self.sct.grab(self.monitor_full_board)
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
        current_pix = board_picture_bw.getpixel((356, 38))
        if current_pix == 0:
            self.current_piece = ""
        else:
            self.current_piece = self.piece_colour[current_pix]

        # Get current queue
        for i in range(5):
            queue_pix = board_picture_bw.getpixel((650, 199 + 109 * i))
            self.queue[i] = self.piece_colour[queue_pix]

    def simulate_piece(self, board, piece, piece_shape, max_row, col):
        """
        Description

        PARAMETERS
        ----------
        board : numpy.array(float)


        piece : numpy.array(float)


        piece_shape : tuple(float)


        max_row : int


        col : int


        RETURNS
        -------
        None
        """
        valid_upper = 0
        valid_lower = 0
        found_valid = False

        for upper in range(
                max_row - piece_shape[0],
                21 - piece_shape[0]):

            section = board[upper:upper + piece_shape[0],
                            col:col + piece_shape[1]]

            section_shape = numpy.shape(section)

            if section_shape[0] == piece_shape[0]:
                section = section + piece
                if 2 not in section:
                    valid_upper = upper
                    valid_lower = upper + piece_shape[0]
                    found_valid = True
                else:
                    break

        return valid_upper, valid_lower, found_valid

    def calculate_heuristic(self, board, max_row):
        """
        BRUH
        """
        # Calculate number of cleared rows given piece placement
        clear_rows = rows_cleared(
            board, max_row)

        # Clear rows, if any, from board
        if clear_rows > 0:
            cleared_board = clear_filled_rows(numpy.copy(board))
        else:
            cleared_board = numpy.copy(board)

        # Get new max and min rows
        max_row = get_max_height(cleared_board)
        min_row = get_min_height(cleared_board)

        # Calculate height difference
        height_diff = min_row - max_row

        # Calculate number of holes in board
        num_holes = find_holes(cleared_board)

        # Calculate roughness of board
        roughness = get_roughness(cleared_board)

        # Calculate H function
        weights = [0, 3, 2, 0.5]

        # print(f"Holes: {num_holes}")
        # print(f"Clear Rows: {clear_rows}")
        # print(f"Roughness: {roughness}")

        # Calculate Heuristic
        # H(s) = - w0*D(s) - w1*O(s) + w2*C(s) - w3*R(s)
        H = - weights[0] * height_diff - weights[1] * \
            num_holes + weights[2] * clear_rows - weights[3] * roughness

        return H, cleared_board

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
        # redundant while board is screenshot every frame
        best_move = numpy.copy(self.board.board)
        best_orientation = 0
        best_col = 0
        hold_select = False

        # Iterate through all current piece rotations
        for states in range(num_states):
            # Get the piece and the shape of the piece
            piece = self.piece_shape[self.current_piece + str(states)]
            piece_shape = numpy.shape(piece)

            # Calculate the number of places it can go
            num_moves = int((10 - piece_shape[1]) / 1 + 1)

            for col in range(num_moves):
                valid_upper, valid_lower, found_valid = self.simulate_piece(
                    board_copy, piece, piece_shape, max_row, col)

                if found_valid:
                    # Place piece on board
                    board_copy[valid_upper:valid_lower,
                               col:col + piece_shape[1]] += piece

                    H_new, cleared_board = self.calculate_heuristic(
                        board_copy, max_row)

                    if H_new > H:
                        H = H_new
                        best_move = numpy.copy(cleared_board)
                        best_orientation = states
                        best_col = col

                    board_copy[valid_upper:valid_lower,
                               col:col + piece_shape[1]] -= piece

        # Consider hold piece
        #   Will add a threshold to consider using hold piece so it's not checked
        #   every single time for trivial choices

        # Get hold piece
        if self.hold_piece == "":
            hold_option = self.queue[0]
        else:
            hold_option = self.hold_piece

        # Get number of possible orientations
        num_states = self.num_piece_states[hold_option]

        for states in range(num_states):
            # Get the piece and the shape of the piece
            piece = self.piece_shape[hold_option + str(states)]
            piece_shape = numpy.shape(piece)

            # Calculate the number of places it can go
            num_moves = int((10 - piece_shape[1]) / 1 + 1)

            for col in range(num_moves):
                valid_upper, valid_lower, found_valid = self.simulate_piece(
                    board_copy, piece, piece_shape, max_row, col)

                if found_valid:
                    # Place piece on board
                    board_copy[valid_upper:valid_lower,
                               col:col + piece_shape[1]] += piece

                    H_new, cleared_board = self.calculate_heuristic(
                        board_copy, max_row)

                    if H_new > H:
                        H = H_new
                        best_move = numpy.copy(cleared_board)
                        best_orientation = states
                        best_col = col
                        hold_select = True

                    board_copy[valid_upper:valid_lower,
                               col:col + piece_shape[1]] -= piece

        if hold_select:
            if self.hold_piece == "":
                self.hold_piece = self.current_piece
                self.current_piece = self.queue.pop(0)
                self.queue.append("")
            else:
                self.hold_piece = self.current_piece
                self.current_piece = hold_option

        self.board.board = best_move
        self.board.update()
        return best_orientation, best_col, hold_select

        """def evaluate_old(self):
        
        BRUH
        
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
        # redundant while board is screenshot every frame
        best_move = numpy.copy(self.board.board)
        best_orientation = 0
        best_col = 0
        best_height_diff = 0
        best_clear_rows = 0
        best_num_holes = 0

        # Iterate through all piece rotations
        for s in range(num_states):
            # Get the piece and the shape of the piece
            piece = self.piece_shape[self.current_piece + str(s)]
            piece_shape = numpy.shape(piece)

            # Calculate the number of places it can go
            num_moves = int((10 - piece_shape[1]) / 1 + 1)

            # Iterate through all the possible moves for the current
            # orientation
            for moves in range(num_moves):

                valid_upper = 0
                valid_lower = 0

                # Start at the current max height +1 and check if it's a valid spot. If yes,
                # check the spot underneath. Repeat until bottom of board is reached or a
                #  non-viable position is reached.
                found_valid = False
                for upper in range(
                        max_row - piece_shape[0],
                        21 - piece_shape[0]):

                    section = board_copy[upper:upper + piece_shape[0],
                                         moves:moves + piece_shape[1]]

                    section_shape = numpy.shape(section)

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

                    # Calculate number of cleared rows given piece placement
                    clear_rows = rows_cleared(
                        board_copy, max_row)

                    # Clear rows, if any, from board
                    if clear_rows > 0:
                        cleared_board = clear_filled_rows(
                            numpy.copy(board_copy))
                    else:
                        cleared_board = numpy.copy(board_copy)

                    # Get new max and min rows
                    max_row = get_max_height(cleared_board)
                    min_row = get_min_height(cleared_board)

                    # Calculate height difference
                    height_diff = min_row - max_row

                    # Calculate number of holes in board
                    num_holes = find_holes(cleared_board)

                    # Calculate roughness of board
                    roughness = get_roughness(cleared_board)

                    # Calculate H function
                    weights = [0, 3, 2, 0.5]

                    # print(f"Holes: {num_holes}")
                    # print(f"Clear Rows: {clear_rows}")
                    # print(f"Roughness: {roughness}")

                    H_new = - weights[0] * height_diff - weights[1] * \
                        num_holes + weights[2] * clear_rows - weights[3] * roughness

                    # print(f"Heuristic: {H_new}")
                    # print()

                    if H_new > H:
                        H = H_new
                        best_move = numpy.copy(cleared_board)
                        best_orientation = s
                        best_col = moves
                        best_height_diff = height_diff
                        best_clear_rows = clear_rows
                        best_num_holes = num_holes

                    board_copy[valid_upper:valid_lower,
                               moves:moves + piece_shape[1]] -= piece

        #print(f"Best H: {H}")
        hold_thresh = -7  # RESEARCH ON HOW TO SET THIS???
        if H < hold_thresh:
            print("Consider hold piece...")

        self.board.board = best_move
        self.board.update()
        return best_orientation, best_col"""

    def generate_moves(self, best_orientation, best_col, hold_select):
        """
        BRUH
        """
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

        movement = ""

        # Check whether to hold
        if hold_select:
            movement += "i"

        # Rotation
        if best_orientation == 1:
            movement += "j"
            if self.current_piece == "I":
                starting_col += 1
        elif best_orientation == 2:
            movement += "k"
        elif best_orientation == 3:
            movement += "l"
            if self.current_piece == "T" or self.current_piece == "L" or self.current_piece == "J":
                starting_col += 1
        else:
            movement += ""

        # lateral movement
        difference = starting_col - best_col
        if difference > 0:
            # left movement
            movement += "a" * difference + "w"
        elif difference < 0:
            # right movement
            movement += "d" * abs(difference) + "w"
        else:
            # straight down
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
        print("Board State:")
        print_board(self.board.board)
        print(f"Current Piece : {self.current_piece}")
        print(f"Hold Piece    : {self.hold_piece}")
        print(f"Queue         : {self.queue}")
        print()
