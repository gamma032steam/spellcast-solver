from game_board import GameBoard
from letter import Letter
from string import ascii_lowercase
from collections import namedtuple

TOP_N = 5
Solution = namedtuple("Solution", "word score path")

def find_best_word(trie: dict, board) -> tuple:
    trie = trie[""]
    scored_words = []
    for letter in board.graph:
        scored_words += find_best_word_r(trie[letter.char], letter, [letter], board)
    return sorted(list(set(scored_words)), key=lambda x: x[1])[-TOP_N:]

# Modifying in place where I can to avoid overhead of memory allocation
# I've personally observed benefits in doing this in a minimax implementation in python
def find_best_word_r(trie: dict, curr_letter: Letter, used_letters: list, board) -> list:
    curr_letter.used_up = True
    scored_words = []
    for i, letter in enumerate(board.graph[curr_letter]):
        if not letter.used_up:
            if board.num_swaps>0:
                board.num_swaps -= 1
                for char in ascii_lowercase:
                    if char in trie:
                        swapped_letter = Letter(char, 0, 1, False, None, True)
                        scored_words += find_best_word_r(trie[char], letter, used_letters+[swapped_letter], board)
                board.num_swaps += 1
                
            if letter.char in trie:
                scored_words += find_best_word_r(trie[letter.char], letter, used_letters+[letter], board)
    curr_letter.used_up = False
    if "" in trie:
        word = "".join([l.char for l in used_letters])
        scored_word = Solution(word=word, score=score_letters(used_letters), path=tuple(used_letters))
        scored_words.append(scored_word)
    return scored_words

def score_letters(used_letters: list):
    has_double_word = sum([letter.does_double_word for letter in used_letters]) > 0
    multiplier = 2 if has_double_word else 1
    score = 0
    for letter in used_letters:
        score += letter.points + letter.diamonds
    return score*multiplier

if __name__ == "__main__":
    from dictionary import build_dictionary
    words = build_dictionary()

    from trie import construct_trie_dic
    trie_dic = construct_trie_dic(words)
    
    from game_board import GameBoard
    board = GameBoard('sample_data/game.png')
    print(board)

    from algorithm import find_best_word
    best_scored_words = find_best_word(trie_dic, board)
    print([(s.word, s.score) for s in best_scored_words])

    from painter import draw_solution
    draw_solution(board, best_scored_words[-1][2])
