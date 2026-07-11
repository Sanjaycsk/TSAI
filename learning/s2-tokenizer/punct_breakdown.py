import os, regex, collections, bpe
DATA = os.path.join(os.path.dirname(__file__), "data")
t = open(os.path.join(DATA, "india_en.txt"), encoding="utf-8").read()
merges, vocab = bpe.train([(t, 1)], vocab_size=10000, verbose=False)
ranks = bpe.build_ranks(merges); cache = {}
is_word = regex.compile(r"^ ?[\p{L}\p{M}\p{N}]+$")
has_digit = regex.compile(r"\p{N}")
num_tok = pure_punct_tok = 0
by_chunk = collections.Counter()
for chunk in bpe.pretokenize(t):
    if is_word.match(chunk):
        continue
    toks = bpe.bpe_word(bpe.word_to_byte_chars(chunk), ranks, cache)
    if has_digit.search(chunk):
        num_tok += len(toks)
    else:
        pure_punct_tok += len(toks)
    by_chunk[chunk.replace('\n','\\n')] += len(toks)
print(f"number-bearing chunk tokens : {num_tok:,}")
print(f"pure-punctuation tokens     : {pure_punct_tok:,}")
print("top non-word chunks by TOKENS spent:")
for c, n in by_chunk.most_common(20):
    print(f"   {n:>4}  {c!r}")
