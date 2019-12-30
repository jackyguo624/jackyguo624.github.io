---
layout: post
title: Byte Pair Encoding
subtitle: Each post also has a subtitle
gh-repo: daattali/beautiful-jekyll
gh-badge: [star, fork, follow]
tags: [test]
comments: true
---

Subword算法是一种重要的提升NLP性能的方法。

相比于传统的空格分隔的tokenization方法相比有以下优点：
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