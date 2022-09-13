import os
import pytesseract
import cv2
import re

BOARD_SIDE_LEN = 5

# mapping to correct incorrect detections
LETTER_SUBSTITUTIONS = {
    '0': 'o'
}

class GameBoard:
    '''Represents the state of a a game board'''

    def __init__(self, image_path):
        '''Creates a game board based on a provided image'''
        self.image = cv2.imread(image_path)
        bounds = self.image_bounds(self.image)
        assert(len(bounds) == 25)
        self.grid = [[]]
        for i, bound in enumerate(bounds):
            if len(self.grid[-1]) == 5: self.grid.append([])
            letter = self.read_letter(self.image, bound, i+1)                
            self.grid[-1].append(letter)

    def __str__(self):
        edge = "-"*(BOARD_SIDE_LEN*2+1) + '\n'
        str = edge
        for row in self.grid:
            str += "|"
            for letter in row:
                str += '*' if letter is None else letter.upper()
                str += '|'
            str += '\n' + edge
        return str

    def read_letter(self, image, bound, n):
        '''Takes coordinate bounds and identifies the letter. Returns None if no letter is found'''
        lo_y, hi_y, lo_x, hi_x = bound
        cropped_image = image[lo_y:hi_y, lo_x:hi_x]
        # remove colour for special letters
        grey_image = self.get_grayscale(cropped_image)
        if not os.path.isdir('tmp'): os.mkdir('tmp')
        cv2.imwrite(f'tmp/debug-letter-{n}.png', grey_image)

        # run image through ocr
        config = r'--oem 3 --psm 10'
        res = pytesseract.image_to_string(grey_image, config=config)

        res = re.sub(r'\W+', '', res)
        if not res: 
            print(f"WARN: Failed to detect letter {n}: no characters detected. Skipping.") 
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

    def image_bounds(self, image):
        '''Finds the approximate region of the letters. Represents regions as the low
        and high y, then low and high x'''
        vertical_breakpoints = self.find_breakpoints(image, axis=0)
        vertical_breakpoints = [self.shave_bounds(p) for p in vertical_breakpoints]
        horizontal_breakpoints = self.find_breakpoints(image, axis=1)
        horizontal_breakpoints = [self.shave_bounds(p) for p in horizontal_breakpoints]

        squares = []
        for lo_y, hi_y in vertical_breakpoints:
            for lo_x, hi_x in horizontal_breakpoints:
                squares.append((lo_y, hi_y, lo_x, hi_x))
        return squares

    def shave_bounds(self, pair):
        '''Reduces the width of a pair by 20% to cut out gems and score'''
        assert(pair[0] < pair[1])
        shave_amount = (pair[1] - pair[0]) // 5
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


if __name__ == '__main__':
    board = GameBoard('sample_data/game.png')
    print(board)
