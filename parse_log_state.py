import sys
import numpy as np
from PIL import Image
from PIL import ImageOps


piece_number = int(sys.argv[1])

log_file = data = open("debug/log.txt","r").read().splitlines()

board_state = log_file[piece_number].split(",")
board_raw = []

for i in range(1,20*10+1):
    board_raw.append(float(board_state[i]))

board = np.asarray(board_raw).reshape([20,10])

board_image = Image.fromarray(np.uint8(board*255)).resize((500,1000), resample=Image.Resampling.BOX)
board_image.save(f"debug/piece{piece_number}.png")
