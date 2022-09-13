from game_board import GameBoard
from letter import Letter

TOP_N = 5

def find_best_word(trie: dict, board) -> tuple:
    best_word, best_score = "", 0
    trie = trie[""]
    scored_words = []
    for letter in board.graph:
        scored_words += find_best_word_r(trie[letter.char], letter, [], board)
    return sorted(scored_words, key=lambda x: x[1])[-TOP_N:]

# Modifying in place where I can to avoid overhead of memory allocation
# I've personally observed benefits in doing this in a minimax implementation in python
def find_best_word_r(trie: dict, curr_letter: Letter, used_letters: list, board) -> list:
    curr_letter.used_up = True
    scored_words = []
    # New list to avoid modifying arg in place
    new_used_letters = used_letters + [curr_letter]
    for i, letter in enumerate(board.graph[curr_letter]):
        if not letter.used_up and letter.char in trie:
            board.graph[curr_letter][i] = None
            scored_words += find_best_word_r(trie[letter.char], letter, new_used_letters, board)
            board.graph[curr_letter][i] = letter
    curr_letter.used_up = False
    if "" in trie:
        word = "".join([l.char for l in new_used_letters]), score_letters(new_used_letters)
        scored_words.append((word, score_letters(new_used_letters)))
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
    print(best_scored_words)
