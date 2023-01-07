# Core OCR component. There's some experimentation with two different
# algorithms, pytesseract and easyocr in here. You can also read the letters
# in manually.

import math
import os
import pytesseract
import cv2
import re
from letter import Letter
from multiprocessing import Pool
from itertools import repeat
from collections import namedtuple
import numpy as np

Bound = namedtuple("Bound", "lo_y hi_y lo_x hi_x")

BOARD_SIDE_LEN = 5

# how much of the tile to cut to be left with just the letter
LETTER_HOZ_TRIM_PERCENT = 0.23
LETTER_VERT_TRIM_PERCENT = 0.10

# mapping to correct incorrect detections
LETTER_SUBSTITUTIONS = {'0': 'o', '': 'i', '2':'z', '5':'s'}

NUM_PROCS = 8

class GameBoard:
    '''Represents the state of a game board'''

    def __init__(self, image_path):
        '''Creates a game board based on a provided image'''
        self.image = cv2.imread(image_path)
        self.tile_bounds = self.find_tile_bounds(self.image)
        letter_bounds = self.find_letter_bounds(self.tile_bounds)
        self.grid = [[]]
        #self.letter_bitmasks, self.multiplier_bitmasks = GameBoard.read_in_bitmasks()
        assert(len(letter_bounds) == 25)
        
        # ocr everything in parallel
        letters = []
        with Pool(processes=NUM_PROCS) as pool:
           letters = pool.starmap(self.read_tile, zip(repeat(self.image), letter_bounds, range(len(letter_bounds))))
        for _, letter in enumerate(letters):
            if len(self.grid[-1]) == 5: self.grid.append([])
            self.grid[-1].append(letter)
        self.graph = GameBoard.construct_graph_from_grid(self.grid)
        
        self.num_swaps = int(input("How many swaps can you perform: "))
        if self.num_swaps > 3:
            print("WARN: It should not be possible to have more than three swaps. Continuing, but this will be slow.")
    
    def get_position(i):
        return (i%BOARD_SIDE_LEN, i//BOARD_SIDE_LEN)
    
    def read_letters_manually():
        print("All inputs should be read from the board going left to right, top to bottom.")
        print("Inputs, should have no separator (spaces, commas, etc)")
        all_letters = input("Enter all 25 letters on the board: ")
        all_letters = all_letters.lower()
        Letters = []
        for i, letter in enumerate(all_letters):
            Letters.append(Letter(letter, 0, 1, False, GameBoard.get_position(i), False))
        all_diamonds = input("y if a diamond is present, n otherwise for all 25 tiles on the board: ")
        all_diamonds = [True if "y" else False for char in all_diamonds]
        for letter, has_diamond in zip(Letters, all_diamonds):
            letter.has_diamond = has_diamond
        print("For X and Y coordinates, the origin is the top left tile. eg:(2 4)")
        print("Leave blank if not present")
        def get_letter(coord):
            x,y = int(coord[0]), int(coord[2])
            return Letters[x+BOARD_SIDE_LEN*y]
        dw = input("Coordinate of double word tile: ")
        if dw:
            get_letter(dw).does_double_word = True
        tl = input("Coordinate of triple letter tile: ")
        if tl:
            get_letter(tl).multiplier = 2
        dl = input("Coordinate of double letter tile: ")
        if dl:
            get_letter(dl).multiplier = 3
        return Letters
    
    def read_in_bitmasks():
        letter_bitmasks = {}
        multiplier_bitmasks = {}
        for file_name in os.listdir("bitmasks"):
            im = cv2.imread(f'bitmasks/{file_name}')
            # drop the color dimension
            im = im[:,:,0]
            file_name = file_name.replace(".png","")
            if len(file_name)>1:
                multiplier_bitmasks[file_name] = im
            else:
                letter_bitmasks[file_name] = im
        return (letter_bitmasks, multiplier_bitmasks)
    
    def construct_graph_from_grid(letters: list):
        graph = {}
        for i in range(BOARD_SIDE_LEN):
            for j in range(BOARD_SIDE_LEN):
                adjacents = []
                for k in [-1, 0, 1]:
                    for l in [-1, 0, 1]:
                        x, y = i+k, j+l
                        if x>0 and y>0 and x<BOARD_SIDE_LEN and y<BOARD_SIDE_LEN:
                            adjacents.append(letters[x][y])
                graph[letters[i][j]] = adjacents
        return graph

    def __str__(self):
        edge = "-"*(BOARD_SIDE_LEN*2+1) + '\n'
        str = edge
        for row in self.grid:
            str += "|"
            for letter in row:
                str += '*' if letter.char is None else letter.char.upper()
                str += '|'
            str += '\n' + edge
        return str
    
    def read_text_w_bitmasks(text_image, bitmasks):
        '''Return None or empty string if nothing is found'''
        # run image through bitmask
        matches = []
        for char, mask in bitmasks.items():
            # Size of the mask must be bigger than the size of the image, otherwise sliding window
            # is impossible.
            if mask.shape > text_image.shape:
                continue
            window_view = np.lib.stride_tricks.sliding_window_view(text_image, mask.shape)
            # Get the absolute difference in brightness levels
            abs_diffs = np.abs(window_view - mask)
            # Sum across each place that the window was placed on the image
            summed_diffs = np.sum(abs_diffs, axis=(2,3))
            # Find the lowest diff in any window
            min_diff = np.min(summed_diffs)
            matches.append((char, min_diff))
        
        def debug_print_arr(arr):
            val = ""
            for row in arr:
                val += "".join(["." if x < 10 else "#" for x in row]) + "\n"
            return val
        pdb.set_trace()
        return sorted(matches, key=lambda x: x[1])[0][0].lower()
    
    # Doesn't work with multiprocessing
    def read_text_w_easy_ocr(text_image, reader, n):
        res = reader.readtext(text_image)
        if not res:
            res = [(None, '', None)]
        
        # res is a tuple of bounds, char, and confidence
        # here we remove the bounds from the tuple
        res = [(x[1], x[2]) for x in res]
        
        letter = res[0][0].lower()
        if len(res) > 1: 
            # we occasionally get double letters, one uppercase and one lower case.
            # just take the first letter, capitalised
            print(f"WARN: More than one letter detected for letter {n}. Guessing that '{res}'' is '{letter}'.")

        if letter in LETTER_SUBSTITUTIONS:
            print(f"WARN: Detected invalid character '{letter}' for letter {n}. Replacing with '{LETTER_SUBSTITUTIONS[letter]}'.") 
            letter = LETTER_SUBSTITUTIONS[letter]
        
        return letter
    
    def read_text_w_tesseract(text_image, n):
        # run image through ocr
        config = r'--oem 3 --psm 10'
        res = pytesseract.image_to_string(text_image, config=config)

        return re.sub(r'\W+', '', res)

    def save_debug_image(self, name, img):
        if not os.path.isdir('tmp'): os.mkdir('tmp', exist_ok=True)
        cv2.imwrite(name, img)

    def read_letter(self, image, bound, n):
        '''Reads the letter in the middle of the tile'''
        # crop image
        cropped_image = image[bound.lo_y:bound.hi_y, bound.lo_x:bound.hi_x]
        # remove colour
        grey_image = self.get_grayscale(cropped_image)
        debug_filename = f'tmp/debug-letter-{n}.png'  
        self.save_debug_image(debug_filename, grey_image)

        # read text
        res = GameBoard.read_text_w_tesseract(grey_image, n)
        if not res: 
            print(f"WARN: Failed to detect letter {n}: no characters detected. Saved a debug image to to {debug_filename}. Skipping.") 
            return None

        letter = res[0].lower()
        if len(res) > 1: 
            # we occasionally get double letters, one uppercase and one lower case.
            # just take the first letter, capitalised
            print(f"WARN: More than one letter detected for letter {n}. Guessing that '{res}'' is '{letter}'.")

        if letter in LETTER_SUBSTITUTIONS:
            print(f"WARN: Detected invalid character '{letter}' for letter {n}. Replacing with '{LETTER_SUBSTITUTIONS[letter]}'.") 
            letter = LETTER_SUBSTITUTIONS[letter]
        elif not res[0].isalpha(): 
            print(f"WARN: First character of letter {n} detected as non-alpha char '{res[0]}'. Skipping.") 
            return None

        return letter

    def read_multiplier(self, image, bound, n):
        '''Tries to OCR the multiplier in the top-left of the tile'''
        # crop image with modified bounds, original bounds identified the letter.
        # modified bounds will identify the multiplier
        y_len = bound.hi_y - bound.lo_y
        x_len = bound.hi_x - bound.lo_x
        cropped_image = image[bound.lo_y - int(y_len*0.35):bound.hi_y- int(y_len*1.05), bound.lo_x- int(x_len*0.8):bound.hi_x- int(x_len*1.1)]
        # remove colour
        grey_image = self.get_grayscale(cropped_image)
        self.save_debug_image(f'tmp/debug-multiplier-{n}.png', grey_image)
        # read text
        multiplier_text = GameBoard.read_text_w_tesseract(grey_image, n).lower()

        does_double_word = False
        multiplier = 1
        if multiplier_text in ["2x", "2k"]:
            does_double_word = True
        elif multiplier_text == "dl":
            multiplier = 2
        elif multiplier_text == "tl":
            multiplier = 3
        elif multiplier_text == "":
            pass
        else:
            print(f"WARN: Detected invalid multiplier text: {multiplier_text}.") 
        return multiplier, does_double_word

    def read_tile(self, image, bound, n):
        '''Takes coordinate bounds and identifies the letter and the multiplier if any.'''
        position = (n%BOARD_SIDE_LEN, n//BOARD_SIDE_LEN)
        letter = self.read_letter(image, bound, n)
        multiplier, does_double_word = self.read_multiplier(image, bound, n)
        return Letter(letter, 0, multiplier, does_double_word, position, False)

    def find_tile_bounds(self, image):
        '''Finds the approximate region of the tiles. Represents regions as the low
        and high y, then low and high x'''
        vertical_breakpoints = self.find_breakpoints(image, axis=0)
        horizontal_breakpoints = self.find_breakpoints(image, axis=1)

        squares = []
        for lo_y, hi_y in vertical_breakpoints:
            for lo_x, hi_x in horizontal_breakpoints:
                squares.append(Bound(lo_y, hi_y, lo_x, hi_x))
        return squares

    def find_letter_bounds(self, tile_bounds):
        '''Finds the approximate region of the letters. Represents regions as the low
        and high y, then low and high x'''
        letter_bounds = []
        for lo_y, hi_y, lo_x, hi_x in tile_bounds:
            lo_x, hi_x = self.shave_bounds((lo_x, hi_x), LETTER_HOZ_TRIM_PERCENT)
            lo_y, hi_y = self.shave_bounds((lo_y, hi_y), LETTER_VERT_TRIM_PERCENT)
            letter_bounds.append(Bound(lo_y, hi_y, lo_x, hi_x))
        return letter_bounds

    def shave_bounds(self, pair, percent):
        '''Reduces the width of a pair by 20% to cut out gems and score'''
        assert(pair[0] < pair[1])
        shave_amount = math.floor((pair[1] - pair[0]) * percent)
        new_pair = (pair[0] + shave_amount, pair[1] - shave_amount)
        assert(new_pair[0] < new_pair[1])
        return new_pair

    def find_breakpoints(self, image, axis):
        '''Find the pixel locations of tiles in a grid'''
        h, w, _ = image.shape
        white = (255, 255, 255)
        breakpoints = []
        in_tile = False
        for a in range(h if axis == 0 else w):
            seen_tile = False
            for b in range(w if axis == 0 else h):
                b, g, r = image[a][b] if axis == 0 else image[b][a]
                if (r, g, b) == white:
                    seen_tile = True
                    if not in_tile:
                        # found the tile colour, must be a tile
                        in_tile = True
                        seen_tile = True
                        breakpoints.append(a)
                    break
            if in_tile and not seen_tile:
                # no tile edges for a whole row/column, must be a gap
                in_tile = False
                breakpoints.append(a)

        assert(len(breakpoints) == 10)
        return self.array_to_pairs(breakpoints)

    def array_to_pairs(self, arr):
        return [(arr[i], arr[i+1]) for i in range(0, len(arr), 2)]

    def get_grayscale(self, image):
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# The text below can be used for manual input
'''
uuifioplgzreiilotdioaqyio
yyynnnynnnynynynnnynnnyyn
4 0
3 4

2
'''

if __name__ == '__main__':
    board = GameBoard('sample_data/game.png')
    print(board)
