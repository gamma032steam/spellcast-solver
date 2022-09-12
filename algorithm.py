from game_board import GameBoard
from letter import Letter

def find_best_word(trie: dict, board) -> tuple:
    best_word, best_score = "", 0
    trie = trie[""]
    print('here')
    for letter in board.graph:
        if letter.char in trie and letter.char == 'r':
            print("here")
            word, score = find_best_word_r(trie[letter.char], letter, [], board)
            if score > best_score:
                best_word, best_score = word, score
    return best_word, best_score

# Modifying in place where I can to avoid overhead of memory allocation
# I've personally observed benefits in doing this in a minimax implementation in python
def find_best_word_r(trie: dict, curr_letter: Letter, used_letters: list, board) -> tuple:
    curr_letter.used_up = True
    best_word, best_score = "", 0
    new_used_letters = used_letters + [curr_letter]
    print(new_used_letters)
    for i, letter in enumerate(board.graph[curr_letter]):
        if not letter.used_up and letter.char in trie:
            board.graph[curr_letter][i] = None
            word, score = find_best_word_r(trie[letter.char], letter, new_used_letters, board)
            if score > best_score:
                best_word, best_score = word, score
            board.graph[curr_letter][i] = letter
    curr_letter.used_up = False
    if best_score == 0:
        return "".join([l.char for l in new_used_letters]), score_letters(new_used_letters)
    return best_word, best_score

def score_letters(used_letters: list):
    has_double_word = sum([letter.does_double_word for letter in used_letters]) > 0
    multiplier = 2 if has_double_word else 1
    score = 0
    for letter in used_letters:
        score += letter.points + letter.diamonds
    return score*multiplier

''' Testing code
from trie import construct_trie
myfile = open("words.txt")
content = myfile.read().split()
content = list(filter(lambda x: not x[0].isdigit(), content))
content = list(map(lambda x: x.lower(), content))
trie = construct_trie(content)

from algorithm import find_best_word
find_best_word(trie, board)
'''
