from game_board import GameBoard
from letter import Letter

def find_best_word(trie: dict, board) -> tuple:
    best_word, best_score = "", 0
    trie = trie[""]
    for letter in board.graph:
        if letter.char in trie and letter.char == 'r':
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
    for i, letter in enumerate(board.graph[curr_letter]):
        if not letter.used_up and letter.char in trie:
            board.graph[curr_letter][i] = None
            word, score = find_best_word_r(trie[letter.char], letter, new_used_letters, board)
            if score > best_score:
                best_word, best_score = word, score
            board.graph[curr_letter][i] = letter
    curr_letter.used_up = False
    if best_score == 0 and "" in trie:
        return "".join([l.char for l in new_used_letters]), score_letters(new_used_letters)
    return best_word, best_score

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
    best_word, best_score = find_best_word(trie_dic, board)
    print(best_word, best_score)
