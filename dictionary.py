LANGUAGES = [] # English language variants that extend the dictionary: american, australian, british, canadian and english
DICTIONARY_LEVEL = 70 # Dictionary level that increase the number of words: 10, 20, 35, 40, 50, 55, 60 or 70

levels = [10, 20, 35, 40, 50, 55, 60, 70]
assert(DICTIONARY_LEVEL in levels)

def build_dictionary():
    '''Get a list of English dictionary words. Based on the wordlist-english 
    package used by SpellCast, with profanities filtered.'''
    profanities = get_profanity_set()
    word_list = []
    curr_level_index = 0
    while curr_level_index < len(levels) and levels[curr_level_index] <= DICTIONARY_LEVEL:
        for lang in LANGUAGES + ["english"]:
            with open(f'dictionary/{lang}-words.{str(levels[curr_level_index])}') as f:
                word_list += [word for word in f.read().splitlines() if is_all_alpha(word) and word not in profanities]
        curr_level_index += 1
    return word_list

def get_profanity_set():
    with open('dictionary/profanities.txt') as f:
        return set([word for word in f.read().splitlines() if is_all_alpha(word)])

def is_all_alpha(word):
    '''Checks if a word contains only chars a-z'''    
    return all([l.isalpha() for l in word])

if __name__ == "__main__":
    print(len(build_dictionary()))
