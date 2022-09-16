class Letter:
    '''Represents a letter on the game board'''
    char_to_points = {'a':1,'b':4,'c':5,'d':3,'e':1,'f':5,'g':3,'h':4,'i':1,'j':7,'k':6,'l':3,'m':4,'n':2,'o':1,'p':4,'q':8,'r':2,'s':2,'t':2,'u':4,'v':5,'w':5,'x':7,'y':4,'z':8}
    assert(len(char_to_points) == 26)

    def __init__(self, char: str, has_diamond: bool, multiplier: int, does_double_word: bool, position: tuple, swapped_letter: bool):
        self.char = char
        self.swapped_letter = swapped_letter
        if swapped_letter:
            self.points = 0
        else:
            if char not in Letter.char_to_points:
                print(f"WARN: {char} is not in the mapping from character to points.")
                self.points = 0
            else:
                self.points = Letter.char_to_points[char]*multiplier
        self.has_diamond = has_diamond
        self.does_double_word = does_double_word
        self.position = position
        # We use this bool to track whether the letter is used up when searching
        # for the best word on the board.
        self.used_up = False
    
    # Hash and Eq only depend on the position of the letter
    def __hash__(self):
        return hash(self.position) + hash(self.swapped_letter)
    def __eq__(self, other):
        if not isinstance(other, type(self)): return NotImplemented
        return self.position == other.position and self.swapped_letter == other.swapped_letter
    
    def __str__(self):
        return self.char
