#          ░░░░░░░░░░░░░░░░░░░░░░░░░░░
#   ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
# ░░░░█████╗░░░░░░░████████╗███████╗████████╗░░
# ░░░██╔══██╗░░░░░░╚══██╔══╝██╔════╝╚══██╔══╝░░
# ░░░██║░░╚═╝█████╗░░░██║░░░█████╗░░░░░██║░░░░░
# ░░░██║░░██╗╚════╝░░░██║░░░██╔══╝░░░░░██║░░░░░
# ░░░╚█████╔╝░░░░░░░░░██║░░░███████╗░░░██║░░░░░
# ░░░░╚════╝░░░░░░░░░░╚═╝░░░╚══════╝░░░╚═╝░░░░░
#   ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
#          ░░░░░░░░░░░░░░░░░░░░░░░░░░░
# ---------------------------------------------
#     Competetive Tetris Engine for TETR.IO
#               Stuart Cunningham
# ---------------------------------------------


# ---------------------------------------------
# USER DEFINED LIBRARIES
#   - Any libraries and imports written by me.
# ---------------------------------------------
from Tetris_Game import *


# ---------------------------------------------
# EXTERNAL LIBRARIES
#   - Any libraries and imports written by a
#     3rd party and are freely available.
# ---------------------------------------------

# Time handling
from time import sleep
from time import time
from timeit import default_timer as timer

# System handling
import win32gui
from pynput.keyboard import Key, Controller
import sys


# ---------------------------------------------
# HELPER FUNCTIONS
#   - May move these to a different file later.
# ---------------------------------------------

def ms2frame(t):
    """
    Convert time in seconds to time in frames per second

    PARAMETERS
    ----------
    t : float
        time in seconds

    RETURNS
    -------
    frames : float
        time in frames per seconds
    """
    return t * 60


# ---------------------------------------------
# MAIN FUNCTION
#   - Contains the juice. Handles init and runs
#     the program loop
#
# Running modes:
#   - loop
#       - standard running mode and will
#         continuously make predictions
#   - single
#       - runs a single prediction
#   - may add more as needed (like debug...)
# ---------------------------------------------
if __name__ == "__main__":
    # Create instance of Tetris_Game
    tetr_board = Tetris_Game()

    # Get TETR.IO to be focused window and wait for it to be in focus
    tetrio = win32gui.FindWindow(None, "TETR.IO")
    win32gui.SetForegroundWindow(tetrio)
    sleep(0.1)

    keyboard = Controller()

    # Get AI PPS
    PPS = float(sys.argv[1])

    # Determine what mode to run in
    mode = sys.argv[2]
    if mode == "loop":
        run_while_true = True
    elif mode == "single":
        run_while_true = False
    else:
        mode = True  # default mode

    debug_file = open("debug/log.txt", "w+")

    # Get whether system is to reset
    if sys.argv[3] == "reset":
        keyboard.press("r")
        sleep(0.3)
        keyboard.release("r")

    tetr_board.init_update()
    # tetr_board.print_state()

    piece_number = 0

    ## DEBUG FILES ##
    debug_file.write(f"{piece_number},")
    for row in tetr_board.board.board:
        for col in row:
            debug_file.write(f"{col},")
    debug_file.write(f"{tetr_board.current_piece},")
    if tetr_board.hold_piece == "":
        debug_file.write("-,")
    else:
        debug_file.write(f"{tetr_board.hold_piece},")
    for piece in tetr_board.queue:
        debug_file.write(f"{piece},")
    debug_file.write(f"{piece_number}\n")

    PPS_timer_tic = timer()
    while (run_while_true):
        # loop mode
        
        # 1. Get play area
        #   a. Get current piece
        #   b. Get hold piece
        #   c. Get queue
        #   d. Get board
        #tic = timer()
        #       tetr_board.update_old()
        #toc = timer()
        #t = toc - tic
        #print(f"It: {iterations}")
        #iterations += 1
        #print(f"Time taken: {t}")
        #print(f"Frames    : {ms2frame(t)}")
        # print()

        # file.write(f"{t},{ms2frame(t)}\n")

        # 2. For current piece:
        #   a. Calculate all possible moves
        #   b. Evaluate all possible moves

        # 3. Select “best” move
        #tic = timer()
        best_or, best_col, hold_select = tetr_board.evaluate()
        #toc = timer()
        #t = toc - tic
        #iterations += 1
        #print(f"It: {iterations}")
        #print(f"Time taken: {t}")
        #print(f"Frames    : {ms2frame(t)}")
        #print(f"Current P : {tetr_board.current_piece}")
        # print()

        # file.write(f"{t},{ms2frame(t)},{tetr_board.current_piece}\n")

        # 4. For best move, calculate piece movement to make move
        # 5. Generate keyboard inputs
        movement = tetr_board.generate_moves(best_or, best_col, hold_select)

        # 6. Execute inputs
        keyboard.type(movement)
        # sleep(0.03)

        PPS_timer_toc = timer()

        # tetr_board.print_state()
        # Wait to place nest piece
        #   Equation doesn't quite work, but it's good enough for now
        sleep_time = (1 / PPS) - (PPS_timer_toc - PPS_timer_tic)
        if sleep_time > 0:
            sleep(sleep_time)
        
        PPS_timer_tic = timer()

        tetr_board.update()

        ## DEBUG FILES ##
        """piece_number += 1
        debug_file.write(f"{piece_number},")
        for row in tetr_board.board.board:
            for col in row:
                debug_file.write(f"{col},")
        debug_file.write(f"{tetr_board.current_piece},")
        if tetr_board.hold_piece == "":
            debug_file.write("-,")
        else:
            debug_file.write(f"{tetr_board.hold_piece},")
        for piece in tetr_board.queue:
            debug_file.write(f"{piece},")
        debug_file.write(f"{piece_number}\n")"""

    else:
        # Single mode

        best_or, best_col, hold_select = tetr_board.evaluate()
        movement = tetr_board.generate_moves(best_or, best_col, hold_select)
        keyboard.type(movement)
        sleep(0.025)
        tetr_board.update()

        ## DEBUG FILES ##
        piece_number += 1
        debug_file.write(f"{piece_number},")
        for row in tetr_board.board.board:
            for col in row:
                debug_file.write(f"{col},")
        debug_file.write(f"{tetr_board.current_piece},")
        if tetr_board.hold_piece == "":
            debug_file.write("-,")
        else:
            debug_file.write(f"{tetr_board.hold_piece},")
        for piece in tetr_board.queue:
            debug_file.write(f"{piece},")
        debug_file.write("\n")

    tetr_board.print_state()


# ---------------------------------------------
# OTHER NOTES
#   - Mainly for me to keep track of stuff
# ---------------------------------------------

# https://github.com/MinusKelvin/cold-clear
# ColdClear Bot, written in Rust O_O
