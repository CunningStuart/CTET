# User defined libraries
from Tetris_Game import *

# Pre-built libraries
# Time handling
from time import sleep
from time import time

# System handling
import win32gui
from pynput.keyboard import Key, Controller
import numpy

# Some initial set up of variables and the window
piece_colour = {}
piece_colour[166] = "S"
piece_colour[165] = "S"
piece_colour[136] = "L"
piece_colour[152] = "I"
piece_colour[153] = "I"
piece_colour[170] = "O"
piece_colour[171] = "O"
piece_colour[121] = "T"
piece_colour[99] = "J"
piece_colour[98] = "J"
piece_colour[110] = "Z"
piece_colour[109] = "Z"

piece_colour[218] = "S"
piece_colour[180] = "L"
piece_colour[200] = "I"
piece_colour[220] = "O"
piece_colour[161] = "T"
piece_colour[131] = "J"
piece_colour[145] = "Z"


tetrio = win32gui.FindWindow(None, "TETR.IO")
win32gui.SetForegroundWindow(tetrio)
sleep(0.1)

keyboard = Controller()

sct = mss.mss()
monitor = {"top": 58, "left": 589, "width": 741, "height": 839}

board = numpy.zeros((20, 10))

# Get screenshot of the board, including queue, current piece and hold
board_picture_bgra = sct.grab(monitor)
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
            board[y,x] = 1
        else:
            board[y,x] = 0

print_board(board)

max_row = get_max_height(board)
min_row = get_min_height(board)

print(max_row)
print(min_row)

# Evaluate board on a given heuristic
clear_rows = rows_cleared(
    board, max_row)

cleared_board = clear_filled_rows(
    numpy.copy(board), clear_rows)

height_diff = (min_row - max_row) + clear_rows

# average_height = get_average_height(cleared_board)
# print(average_height)

# height_diff = (20 - max_row) - average_height

num_holes = find_holes(cleared_board) # - self.board.number_of_holes)

# Calculate H function
weights = [2, 3, 4]
H_new = - weights[0] * height_diff - weights[1] * \
    num_holes + weights[2] * clear_rows

roughness = get_roughness(board)

print(f"Height difference      : {height_diff}")
print(f"Number of rows cleared : {clear_rows}")
print(f"Number of holes        : {num_holes}")
print(f"Total roughness        : {roughness}")
print(f"Heuristic H(s) = -{weights[0]}*{height_diff} - {weights[1]}*{num_holes} + {weights[2]}*{clear_rows} = {H_new}")
print()