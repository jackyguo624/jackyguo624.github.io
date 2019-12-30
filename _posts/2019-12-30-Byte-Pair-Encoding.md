---
layout: post
title: Byte Pair Encoding
tags: [nlp, subword]
comments: true
---

Subword算法是一种重要的提升NLP性能的方法。相比于传统的空格分隔的tokenization方法相比有以下优点：
* 可以更好的解决OOV问题
* 更有利于建模词缀之间的关系，并将词缀泛化
  e.g. old”, “older”, and “oldest 泛化到 “smart”, “smarter”, and “smartest”

相比于Character embeding，
* 粒度更大，并包含一定的语言信息
* 可以更好的解决OOV问题

## Byte Pair Encoding
* 优点：
    可以有效地平衡词汇表大小和步数(编码句子所需的token数量)
* 缺点：
    基于贪婪和确定的符号替换，不能提供带概率的多个分片结果

### 主要算法
BPE 使用文本统计所得，主要算法包括：
1. 生成词表（Generate vocabulary）
    * 每轮迭代：统计token pair 出现的次数，每次合并次数最高的pair成一个token
    * 当迭代到达指定次数或下一个最高频的pair出现频率为1，所有的token就是词表
2. 编码文本（Text to tokens）
    * 将得到的词表按长度倒序排列
    * 按词表顺序，使用greedy匹配文本中的character生成指定的token
3. 解码文本 (Tokens to text)
    * 将token合并

#### 生成词表

~~~
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
    p = re.compile(r'(?<!\S)' + bigram + r'(?!\S)') # 前后都为空格
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

# Get free book from Gutenberg
# wget http://www.gutenberg.org/cache/epub/16457/pg16457.txt
vocab = get_vocab('pg16457.txt')

num_merges = 1000
for i in range(num_merges):
    pairs = get_stats(vocab)
    if not pairs:
        break
    best = max(pairs, key=pairs.get)
    vocab = merge_vocab(best, vocab)
    #print('Iter: {}'.format(i))
    #print('Best pair: {}'.format(best))
    #tokens_frequencies, vocab_tokenization = get_tokens_from_vocab(vocab)
    #print('All tokens: {}'.format(tokens_frequencies.keys()))
    #print('Number of tokens: {}'.format(len(tokens_frequencies.keys())))
    #print('==========')

tokens_frequencies, vocab_tokenization = get_tokens_from_vocab(vocab)
~~~

#### 编码文本
~~~

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

~~~


### Reference
[深入理解NLP Subword算法：BPE、WordPiece、ULM](https://zhuanlan.zhihu.com/p/86965595)

[Byte Pair Encoding](https://leimao.github.io/blog/Byte-Pair-Encoding/)