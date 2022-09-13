class TrieNode:
    def __init__(self, char):
        self.char = char
        self.children = [None] * 27

ord_a = ord('a')
def construct_trie_list(words: list):
    trie_root = TrieNode("")
    for word in words:
        word = word.lower()
        curr_trie_node = trie_root
        for letter in word:
            trie_child = curr_trie_node.children[ord(letter)-ord_a]
            if not trie_child:
                trie_child = TrieNode(letter)
                curr_trie_node.children[ord(letter)-ord_a] = trie_child
            curr_trie_node = trie_child
        curr_trie_node.children[26] = True
    return trie_root

def construct_trie_dic(words: list):
    trie_root = {"":{}}
    for word in words:
        word = word.lower()
        trie = trie_root[""]
        for letter in word:
            if letter not in trie:
                trie[letter] = {}
            trie = trie[letter]
        # Word termination
        trie[""] = None
    return trie_root

'''
Trie with children stored as dict is 62109896 bytes in memory.
Trie with children stored as list is 112461624 bytes in memory.
Trie with children stored as dict is 1719158 bytes after pickling.
Trie with children stored as list is 12207107 bytes after pickling.
'''

if __name__ == "__main__":
    from dictionary import build_dictionary
    words = build_dictionary()
    trie_dic = construct_trie_dic(words)
    trie_list = construct_trie_list(words)
    # Compare size in memory
    from pympler import asizeof
    print(f"Trie with children stored as dict is {asizeof.asizeof(trie_dic)} bytes in memory.")
    print(f"Trie with children stored as list is {asizeof.asizeof(trie_list)} bytes in memory.")
    # Compare size after serialization
    import pickle
    print(f"Trie with children stored as dict is {len(pickle.dumps(trie_dic))} bytes after pickling.")
    print(f"Trie with children stored as list is {len(pickle.dumps(trie_list))} bytes after pickling.")
