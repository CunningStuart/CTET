# ----------------------------------------------------------------------
#
# ----------------------------------------------------------------------

# User defined libraries
from Tetris_Game import *

# Pre-built libraries
# Time handling
from time import sleep
from time import time
from timeit import default_timer as timer

# System handling
import win32gui
from pynput.keyboard import Key, Controller


def ms2frame(t):
    return t * 60


if __name__ == "__main__":
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

    tetr_board = Tetris_Game({"top": 58, "left": 589, "width": 741,
                        "height": 839}, piece_colour)

    tetrio = win32gui.FindWindow(None, "TETR.IO")
    win32gui.SetForegroundWindow(tetrio)
    sleep(0.1)

    keyboard = Controller()

    # Some condition to keep the program running like a check if TETR.IO
    # is still the window in focus...
    run_while_true = True

    file = open("performance_testing/evaluation_times.txt","w+")

    iterations = 1

    while (run_while_true):
        # 1. Get play area
        #   a. Get current piece
        #   b. Get hold piece
        #   c. Get queue
        #   d. Get board
        #tic = timer()
        tetr_board.update()
        #toc = timer()
        #t = toc - tic
        #print(f"It: {iterations}")
        #iterations += 1
        #print(f"Time taken: {t}")
        #print(f"Frames    : {ms2frame(t)}")
        #print()

        #file.write(f"{t},{ms2frame(t)}\n")


        # 2. For current piece:
        #   a. Calculate all possible moves
        #   b. Evaluate all possible moves

        # 3. Select “best” move
        tic = timer()
        best_or, best_col = tetr_board.evaluate()
        toc = timer()
        t = toc - tic
        #iterations += 1
        #print(f"It: {iterations}")
        #print(f"Time taken: {t}")
        #print(f"Frames    : {ms2frame(t)}")
        #print(f"Current P : {tetr_board.current_piece}")
        #print()

        file.write(f"{t},{ms2frame(t)},{tetr_board.current_piece}\n")

        # 4. For best move, calculate piece movement to make move
        # 5. Generate keyboard inputs
        movement = tetr_board.generate_moves(best_or, best_col)

        # 6. Execute inputs
        keyboard.type(movement)

        # 7. Wait until next piece can be placed

        # run_while_true = False
        sleep(0.02)
        # print("Repeating.")

    # tetr_board.print_state()


# https://github.com/MinusKelvin/cold-clear
# ColdClear Bot, written in Rust O_O
