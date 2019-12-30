LEI MAO'S LOG BOOK
CURRICULUM BLOG ARTICLES PROJECTS READINGS PUBLICATIONS MISCELLANEOUS
Lei Mao bio photo
Lei Mao
Machine Learning, Artificial Intelligence. On the Move.

 Twitter
 Facebook
 LinkedIn
 GitHub
  G. Scholar
 E-Mail
 RSS
Byte Pair Encoding
Introduction
In natural language processing models, the inputs to the model are usually sequences of sentences, such as “I went to New York last week.”. The sequence consists of tokens. In old language models, tokens are usually white-space separated words and punctuations, such as [“i”, “went”, “to”, “new”, “york”, “last”, “week”, “.”]. I remember the word2vec model was using this kind of tokenization method. However, this has some draw backs. For example, if the model learned the relationship between “old”, “older”, and “oldest”, it does not tell the model anything about the relationship between “smart”, “smarter”, and “smartest”. However, in this case, if we use some subtokens such as “er” and “est”, and the model learned the relationship between “old”, “older”, and “oldest”, it will tell the model some information about the relationship between “smart”, “smarter”, and “smartest”. Now that using subtokens sounds a better tokenization method, how do we engineer these subtokens? Preparing subtokens by ourselves is heuristics and label consuming, thus is not desirable. But information theory comes and saves us again.



In information theory, byte pair encoding (BPE) or digram coding is a simple form of data compression in which the most common pair of consecutive bytes of data is replaced with a byte that does not occur within that data. On Wikipedia, there is a very good example of using BPE on a single string. It was also employed in natural language processing models, such as Transformer (trained on standard WMT 2014 English-German dataset) and GPT-2, to tokenize word sequences.



In this blog post, I will talk about how to do byte pair encoding for a whole dataset which consists of sentences or words.

Byte Pair Encoding Algorithm
Token Learning from Dataset
In the paper “Neural Machine Translation of Rare Words with Subword Units” published in 2015, the author has released the source code of doing byte pair encoding for a corpus of words. We count the frequency of each word shown in the corpus. For each word, we append a special stop token “</w>” at the end of the word. We will talk about the motivation behind this later. We then split the word into characters. Initially, the tokens of word are all of its characters plus the additional “</w>” token. For example, the tokens for word “low” are [“l”, “o”, “w”, “</w>”] in order. So after counting all the words in the dataset, we will get a vocabulary for the tokenized word with its corresponding counts, such as

{'l o w </w>': 5, 'l o w e r </w>': 2, 'n e w e s t </w>': 6, 'w i d e s t </w>': 3}
In each iteration, we count the frequency of each consecutive byte pair, find out the most frequent one, and merge the two byte pair tokens to one token.



For the above example, in the first iteration of merge, because byte pair “e” and “s” occurred 6 + 3 = 9 times which is the most frequent. We merge these to into a new token “es”. Note that because token “s” is also gone in this particular example.

{'l o w </w>': 5, 'l o w e r </w>': 2, 'n e w es t </w>': 6, 'w i d es t </w>': 3}
In the second iteration of merge, token “es” and “t” occurred 6 + 3 = 9 times, which is the most frequent. We merge these to into a new token “est”. Note that because token “es” and “t” are also gone.

{'l o w </w>': 5, 'l o w e r </w>': 2, 'n e w est </w>': 6, 'w i d est </w>': 3}
In the third iteration of merge, token “est” and “</w>” pair is the most frequent, etc.



We could count the iteration or the maximum number of tokens to control the number of tokens we want to have.



Stop token “</w>” is also important. Without “</w>”, say if there is a token “st”, this token could be in the word “st ar”, or the wold “wide st”, however, the meaning of them are quite different. With “</w>”, if there is a token “st</w>”, the model immediately know that it is the token for the wold “wide st</w>” but not “st ar</w>”.



After each merge, there could be three scenarios, the number of tokens decreases by one, remains the same or increases by one. But in practice, as the number of merges increases, usually the number of tokens first increases then decreases.

Token Learning Example
I modified the code from the paper “Neural Machine Translation of Rare Words with Subword Units” and used it as a concrete example of how byte pair encoding is working for real dataset. The dataset is a free novel “All Around the Moon” by Jules Verne in text format which could be download from Gutenberg.

import re, collections

def get_vocab(filename):
    vocab = collections.defaultdict(int)
    with open(filename, 'r', encoding='utf-8') as fhand:
        for line in fhand:
            words = line.strip().split()
            for word in words:
                vocab[' '.join(list(word)) + ' </w>'] += 1
    return vocab

def get_stats(vocab):
    pairs = collections.defaultdict(int)
    for word, freq in vocab.items():
        symbols = word.split()
        for i in range(len(symbols)-1):
            pairs[symbols[i],symbols[i+1]] += freq
    return pairs

def merge_vocab(pair, v_in):
    v_out = {}
    bigram = re.escape(' '.join(pair))
    p = re.compile(r'(?<!\S)' + bigram + r'(?!\S)')
    for word in v_in:
        w_out = p.sub(''.join(pair), word)
        v_out[w_out] = v_in[word]
    return v_out

def get_tokens(vocab):
    tokens = collections.defaultdict(int)
    for word, freq in vocab.items():
        word_tokens = word.split()
        for token in word_tokens:
            tokens[token] += freq
    return tokens

# vocab = {'l o w </w>': 5, 'l o w e r </w>': 2, 'n e w e s t </w>': 6, 'w i d e s t </w>': 3}

# Get free book from Gutenberg
# wget http://www.gutenberg.org/cache/epub/16457/pg16457.txt
vocab = get_vocab('pg16457.txt')

print('==========')
print('Tokens Before BPE')
tokens = get_tokens(vocab)
print('Tokens: {}'.format(tokens))
print('Number of tokens: {}'.format(len(tokens)))
print('==========')

num_merges = 1000
for i in range(num_merges):
    pairs = get_stats(vocab)
    if not pairs:
        break
    best = max(pairs, key=pairs.get)
    vocab = merge_vocab(best, vocab)
    print('Iter: {}'.format(i))
    print('Best pair: {}'.format(best))
    tokens = get_tokens(vocab)
    print('Tokens: {}'.format(tokens))
    print('Number of tokens: {}'.format(len(tokens)))
    print('==========')
It should print out something like this.

==========
Tokens Before BPE
Tokens: defaultdict(<class 'int'>, {'\ufeff': 1, 'T': 1610, 'h': 26094, 'e': 59152, '</w>': 101830, 'P': 780, 'r': 29540, 'o': 34983, 'j': 857, 'c': 13891, 't': 44258, 'G': 300, 'u': 13731, 'n': 32499, 'b': 7428, 'g': 8744, 'E': 901, 'B': 1163, 'k': 2726, 'f': 10469, 'A': 1381, 'l': 20632, 'd': 17576, 'M': 1206, ',': 8068, 'y': 8812, 'J': 80, 's': 28320, 'V': 104, 'i': 31435, 'a': 36692, 'w': 8133, 'm': 9812, 'v': 4880, '.': 4055, 'Y': 250, 'p': 8040, '-': 1128, 'L': 429, ':': 209, 'R': 369, 'D': 327, '6': 77, '2': 158, '0': 401, '5': 131, '[': 32, '#': 1, '1': 295, '4': 104, '7': 65, ']': 32, '*': 44, 'S': 860, 'O': 510, 'F': 422, 'H': 689, 'I': 1432, 'C': 863, 'U': 170, 'N': 796, 'K': 42, '/': 52, '"': 4086, '!': 1214, 'W': 579, '3': 105, "'": 1243, 'Q': 33, 'X': 49, 'Z': 10, '?': 651, '8': 75, '9': 38, '_': 1426, 'à': 3, 'x': 937, 'z': 365, '°': 41, 'q': 575, ';': 561, '(': 56, ')': 56, '{': 23, '}': 16, 'è': 2, 'é': 14, '+': 2, '=': 3, 'ö': 2, 'ê': 5, 'â': 1, 'ô': 1, 'Æ': 3, 'æ': 2, '%': 1, '@': 2, '$': 2})
Number of tokens: 98
==========
Iter: 0
Best pair: ('e', '</w>')
Tokens: defaultdict(<class 'int'>, {'\ufeff': 1, 'T': 1610, 'h': 26094, 'e</w>': 17749, 'P': 780, 'r': 29540, 'o': 34983, 'j': 857, 'e': 41403, 'c': 13891, 't': 44258, '</w>': 84081, 'G': 300, 'u': 13731, 'n': 32499, 'b': 7428, 'g': 8744, 'E': 901, 'B': 1163, 'k': 2726, 'f': 10469, 'A': 1381, 'l': 20632, 'd': 17576, 'M': 1206, ',': 8068, 'y': 8812, 'J': 80, 's': 28320, 'V': 104, 'i': 31435, 'a': 36692, 'w': 8133, 'm': 9812, 'v': 4880, '.': 4055, 'Y': 250, 'p': 8040, '-': 1128, 'L': 429, ':': 209, 'R': 369, 'D': 327, '6': 77, '2': 158, '0': 401, '5': 131, '[': 32, '#': 1, '1': 295, '4': 104, '7': 65, ']': 32, '*': 44, 'S': 860, 'O': 510, 'F': 422, 'H': 689, 'I': 1432, 'C': 863, 'U': 170, 'N': 796, 'K': 42, '/': 52, '"': 4086, '!': 1214, 'W': 579, '3': 105, "'": 1243, 'Q': 33, 'X': 49, 'Z': 10, '?': 651, '8': 75, '9': 38, '_': 1426, 'à': 3, 'x': 937, 'z': 365, '°': 41, 'q': 575, ';': 561, '(': 56, ')': 56, '{': 23, '}': 16, 'è': 2, 'é': 14, '+': 2, '=': 3, 'ö': 2, 'ê': 5, 'â': 1, 'ô': 1, 'Æ': 3, 'æ': 2, '%': 1, '@': 2, '$': 2})
Number of tokens: 99
==========
Iter: 1
Best pair: ('t', 'h')
Tokens: defaultdict(<class 'int'>, {'\ufeff': 1, 'T': 1610, 'h': 12065, 'e</w>': 17749, 'P': 780, 'r': 29540, 'o': 34983, 'j': 857, 'e': 41403, 'c': 13891, 't': 30229, '</w>': 84081, 'G': 300, 'u': 13731, 'n': 32499, 'b': 7428, 'g': 8744, 'E': 901, 'B': 1163, 'k': 2726, 'f': 10469, 'A': 1381, 'l': 20632, 'd': 17576, 'th': 14029, 'M': 1206, ',': 8068, 'y': 8812, 'J': 80, 's': 28320, 'V': 104, 'i': 31435, 'a': 36692, 'w': 8133, 'm': 9812, 'v': 4880, '.': 4055, 'Y': 250, 'p': 8040, '-': 1128, 'L': 429, ':': 209, 'R': 369, 'D': 327, '6': 77, '2': 158, '0': 401, '5': 131, '[': 32, '#': 1, '1': 295, '4': 104, '7': 65, ']': 32, '*': 44, 'S': 860, 'O': 510, 'F': 422, 'H': 689, 'I': 1432, 'C': 863, 'U': 170, 'N': 796, 'K': 42, '/': 52, '"': 4086, '!': 1214, 'W': 579, '3': 105, "'": 1243, 'Q': 33, 'X': 49, 'Z': 10, '?': 651, '8': 75, '9': 38, '_': 1426, 'à': 3, 'x': 937, 'z': 365, '°': 41, 'q': 575, ';': 561, '(': 56, ')': 56, '{': 23, '}': 16, 'è': 2, 'é': 14, '+': 2, '=': 3, 'ö': 2, 'ê': 5, 'â': 1, 'ô': 1, 'Æ': 3, 'æ': 2, '%': 1, '@': 2, '$': 2})
Number of tokens: 100
==========
Iter: 2
Best pair: ('t', '</w>')
Tokens: defaultdict(<class 'int'>, {'\ufeff': 1, 'T': 1610, 'h': 12065, 'e</w>': 17749, 'P': 780, 'r': 29540, 'o': 34983, 'j': 857, 'e': 41403, 'c': 13891, 't</w>': 9271, 'G': 300, 'u': 13731, 't': 20958, 'n': 32499, 'b': 7428, 'g': 8744, '</w>': 74810, 'E': 901, 'B': 1163, 'k': 2726, 'f': 10469, 'A': 1381, 'l': 20632, 'd': 17576, 'th': 14029, 'M': 1206, ',': 8068, 'y': 8812, 'J': 80, 's': 28320, 'V': 104, 'i': 31435, 'a': 36692, 'w': 8133, 'm': 9812, 'v': 4880, '.': 4055, 'Y': 250, 'p': 8040, '-': 1128, 'L': 429, ':': 209, 'R': 369, 'D': 327, '6': 77, '2': 158, '0': 401, '5': 131, '[': 32, '#': 1, '1': 295, '4': 104, '7': 65, ']': 32, '*': 44, 'S': 860, 'O': 510, 'F': 422, 'H': 689, 'I': 1432, 'C': 863, 'U': 170, 'N': 796, 'K': 42, '/': 52, '"': 4086, '!': 1214, 'W': 579, '3': 105, "'": 1243, 'Q': 33, 'X': 49, 'Z': 10, '?': 651, '8': 75, '9': 38, '_': 1426, 'à': 3, 'x': 937, 'z': 365, '°': 41, 'q': 575, ';': 561, '(': 56, ')': 56, '{': 23, '}': 16, 'è': 2, 'é': 14, '+': 2, '=': 3, 'ö': 2, 'ê': 5, 'â': 1, 'ô': 1, 'Æ': 3, 'æ': 2, '%': 1, '@': 2, '$': 2})
Number of tokens: 101
==========
Encoding and Decoding
Decoding is extremely simple, you just have to concatenate all the tokens together and you will get the original whole word. For example, if the encoded sequence is [“the</w>”, “high”, “est</w>”, “moun”, “tain</w>”], we immediately know the decoded sequence “the</w> highest</w> mountain</w>”.



How about encoding then? Given word sequence, say, [“the</w>”, “highest</w>”, “mountain</w>”]. We have the all the tokens listed in the order from long tokens to short tokens. For each word, we iterate through all the tokens and check if each token is a substring of the word, if so, that token is one of the tokens in the word. In this example, we assume the tokens are [“errrr</w>”, “tain</w>”, “moun”, “est</w>”, “high”, “the</w>”, “a</w>”]. We iterate from the longest token “errrr</w>” to the shortest token “a</w>” trying to replace the sub string in each of the word to tokens. Eventually, we all the tokens will be iterated, and all the substrings will be replaced to tokens. If there is still substring left but all the tokens were iterated, we replace the remaining subwords to tokens like for unknown tokens. In this example, we get tokenization ["the</w>"] for word "the</w>", tokenization ["high", "est</w>"] for word "highest</w>", and tokenization ["moun", "tain</w>"] for "mountain</w>".



Encoding is very computational expensive. In practice, we could pre-tokenize all the words and save how a word should be tokenized in a dictionary. If we saw an unknown word which does not exist in the dictionary. We apply the above encoding method to tokenize the word, and add the tokenization of the new word to the dictionary for future reference.

Encoding and Decoding Example
Here is an example of encoding known and unknown words using tokens learned from the dataset. To get better tokenizations, the number of merges was set to a large number.

import re, collections

def get_vocab(filename):
    vocab = collections.defaultdict(int)
    with open(filename, 'r', encoding='utf-8') as fhand:
        for line in fhand:
            words = line.strip().split()
            for word in words:
                vocab[' '.join(list(word)) + ' </w>'] += 1

    return vocab

def get_stats(vocab):
    pairs = collections.defaultdict(int)
    for word, freq in vocab.items():
        symbols = word.split()
        for i in range(len(symbols)-1):
            pairs[symbols[i],symbols[i+1]] += freq
    return pairs

def merge_vocab(pair, v_in):
    v_out = {}
    bigram = re.escape(' '.join(pair))
    p = re.compile(r'(?<!\S)' + bigram + r'(?!\S)')
    for word in v_in:
        w_out = p.sub(''.join(pair), word)
        v_out[w_out] = v_in[word]
    return v_out

def get_tokens_from_vocab(vocab):
    tokens_frequencies = collections.defaultdict(int)
    vocab_tokenization = {}
    for word, freq in vocab.items():
        word_tokens = word.split()
        for token in word_tokens:
            tokens_frequencies[token] += freq
        vocab_tokenization[''.join(word_tokens)] = word_tokens
    return tokens_frequencies, vocab_tokenization

def measure_token_length(token):
    if token[-4:] == '</w>':
        return len(token[:-4]) + 1
    else:
        return len(token)

def tokenize_word(string, sorted_tokens, unknown_token='</u>'):
    
    if string == '':
        return []
    if sorted_tokens == []:
        return [unknown_token]

    string_tokens = []
    for i in range(len(sorted_tokens)):
        token = sorted_tokens[i]
        token_reg = re.escape(token.replace('.', '[.]'))

        matched_positions = [(m.start(0), m.end(0)) for m in re.finditer(token_reg, string)]
        if len(matched_positions) == 0:
            continue
        substring_end_positions = [matched_position[0] for matched_position in matched_positions]

        substring_start_position = 0
        for substring_end_position in substring_end_positions:
            substring = string[substring_start_position:substring_end_position]
            string_tokens += tokenize_word(string=substring, sorted_tokens=sorted_tokens[i+1:], unknown_token=unknown_token)
            string_tokens += [token]
            substring_start_position = substring_end_position + len(token)
        remaining_substring = string[substring_start_position:]
        string_tokens += tokenize_word(string=remaining_substring, sorted_tokens=sorted_tokens[i+1:], unknown_token=unknown_token)
        break
    return string_tokens

# vocab = {'l o w </w>': 5, 'l o w e r </w>': 2, 'n e w e s t </w>': 6, 'w i d e s t </w>': 3}

vocab = get_vocab('pg16457.txt')

print('==========')
print('Tokens Before BPE')
tokens_frequencies, vocab_tokenization = get_tokens_from_vocab(vocab)
print('All tokens: {}'.format(tokens_frequencies.keys()))
print('Number of tokens: {}'.format(len(tokens_frequencies.keys())))
print('==========')

num_merges = 10000
for i in range(num_merges):
    pairs = get_stats(vocab)
    if not pairs:
        break
    best = max(pairs, key=pairs.get)
    vocab = merge_vocab(best, vocab)
    print('Iter: {}'.format(i))
    print('Best pair: {}'.format(best))
    tokens_frequencies, vocab_tokenization = get_tokens_from_vocab(vocab)
    print('All tokens: {}'.format(tokens_frequencies.keys()))
    print('Number of tokens: {}'.format(len(tokens_frequencies.keys())))
    print('==========')

# Let's check how tokenization will be for a known word
word_given_known = 'mountains</w>'
word_given_unknown = 'Ilikeeatingapples!</w>'

sorted_tokens_tuple = sorted(tokens_frequencies.items(), key=lambda item: (measure_token_length(item[0]), item[1]), reverse=True)
sorted_tokens = [token for (token, freq) in sorted_tokens_tuple]

print(sorted_tokens)

word_given = word_given_known 

print('Tokenizing word: {}...'.format(word_given))
if word_given in vocab_tokenization:
    print('Tokenization of the known word:')
    print(vocab_tokenization[word_given])
    print('Tokenization treating the known word as unknown:')
    print(tokenize_word(string=word_given, sorted_tokens=sorted_tokens, unknown_token='</u>'))
else:
    print('Tokenizating of the unknown word:')
    print(tokenize_word(string=word_given, sorted_tokens=sorted_tokens, unknown_token='</u>'))

word_given = word_given_unknown 

print('Tokenizing word: {}...'.format(word_given))
if word_given in vocab_tokenization:
    print('Tokenization of the known word:')
    print(vocab_tokenization[word_given])
    print('Tokenization treating the known word as unknown:')
    print(tokenize_word(string=word_given, sorted_tokens=sorted_tokens, unknown_token='</u>'))
else:
    print('Tokenizating of the unknown word:')
    print(tokenize_word(string=word_given, sorted_tokens=sorted_tokens, unknown_token='</u>'))
You should be able to see the output like this:

Tokenizing word: mountains</w>...
Tokenization of the known word:
['mountains</w>']
Tokenization treating the known word as unknown:
['mountains</w>']
Tokenizing word: Ilikeeatingapples!</w>...
Tokenizating of the unknown word:
['I', 'like', 'ea', 'ting', 'app', 'l', 'es!</w>']
The known word “mountains</w>” was tokenized as “mountains</w>” using the comprehensive encoding method described above. It did also match the learned tokenization of the known words saved in the dictionary. The unknown invented word “Ilikeeatingapples!</w>” was also tokenized as [‘I’, ‘like’, ‘ea’, ‘ting’, ‘app’, ‘l’, ‘es!</w>’].

References
Neural Machine Translation of Rare Words with Subword Units
All Around the Moon - Jules Verne
Byte Pair Encoding was published on July 19, 2019 and last modified on July 19, 2019 by Lei Mao.


© 2019 Lei Mao. Powered by Jekyll and the Minimal Mistakes Theme.