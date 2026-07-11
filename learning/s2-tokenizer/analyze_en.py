"""Why is English stuck at 1.20? Break the token bill into: word-tokens vs
punctuation/number-tokens, and count how many words fail to be a single token."""
import os, regex, collections, bpe
DATA = os.path.join(os.path.dirname(__file__), "data")
t = open(os.path.join(DATA, "india_en.txt"), encoding="utf-8").read()

merges, vocab = bpe.train([(t, 1)], vocab_size=10000, verbose=False)
ranks = bpe.build_ranks(merges)

is_word = regex.compile(r"^ ?[\p{L}\p{M}\p{N}]+$")
cache = {}
word_tok = punct_tok = 0
multi = collections.Counter()
n_multi = 0
for chunk in bpe.pretokenize(t):
    toks = bpe.bpe_word(bpe.word_to_byte_chars(chunk), ranks, cache)
    if is_word.match(chunk):
        word_tok += len(toks)
        if len(toks) > 1:
            n_multi += 1
            multi[chunk] += 1
    else:
        punct_tok += len(toks)

words = bpe.word_count(t)
total = len(bpe.encode(t, ranks))
print(f"total tokens {total:,}  words {words:,}  fertility {total/words:.4f}")
print(f"  word-tokens   {word_tok:,}")
print(f"  punct/num-tok {punct_tok:,}   (this is the overhead on top of words)")
print(f"  words that are >1 token: {n_multi:,}")
print("  worst multi-token words:", [(''.join(w).replace('Ġ',' '), len(bpe.bpe_word(bpe.word_to_byte_chars(w),ranks,cache))) for w,_ in multi.most_common(12)])
