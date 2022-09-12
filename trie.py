def construct_trie(words: list):
    trie_root = {"":{}}
    for word in words:
        trie = trie_root[""]
        for letter in word:
            if letter not in trie:
                trie[letter] = {}
            trie = trie[letter]
    return trie_root

''' Testing code
from trie import construct_trie
myfile = open("words.txt")
content = myfile.read().split()
content = list(filter(lambda x: not x[0].isdigit(), content))
content = list(map(lambda x: x.lower(), content))
trie = construct_trie(content)
'''
