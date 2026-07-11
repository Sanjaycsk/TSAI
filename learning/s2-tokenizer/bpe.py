"""
Byte-level BPE tokenizer — built from scratch (no tokenizers / HF libraries).

The whole algorithm is "merge the most frequent adjacent pair, repeat":
  1. text -> UTF-8 bytes                (256 base symbols => NEVER any UNK)
  2. pre-tokenize into word-chunks      (so merges never cross word/space lines)
  3. count adjacent byte pairs, merge the top one into a new symbol
  4. repeat until we have `vocab_size` symbols total

`train()` learns the merges. `encode()` applies them (inference). The JS widget
re-implements `encode()` byte-for-byte so the browser reproduces these numbers.
"""
import regex, json, collections, heapq, unicodedata   # `regex` gives \p{L}\p{M}; unicodedata for NFC

# ---------------------------------------------------------------------------
# 1) Byte <-> printable-char map (GPT-2 trick).
#    Bytes like 0x00 or 0x20(space) aren't printable, which makes merges hard to
#    debug and store. GPT-2 maps all 256 bytes to a set of 256 *printable* unicode
#    chars. It's a reversible relabel — the algorithm still works on raw bytes.
# ---------------------------------------------------------------------------
def bytes_to_unicode():
    bs = list(range(33, 127)) + list(range(161, 173)) + list(range(174, 256))
    cs = bs[:]
    n = 0
    for b in range(256):
        if b not in bs:
            bs.append(b)
            cs.append(256 + n)   # spill unprintable bytes into a high, unused range
            n += 1
    return {b: chr(c) for b, c in zip(bs, cs)}

BYTE_ENCODER = bytes_to_unicode()                       # byte value -> byte-char
BYTE_DECODER = {c: b for b, c in BYTE_ENCODER.items()}  # byte-char -> byte value

# ---------------------------------------------------------------------------
# 2) Pre-tokenization regex.
#    A word is letters + their combining marks [\p{L}\p{M}], so an akshara
#    (consonant + its matra) stays glued. Plain \w drops combining marks and
#    shatters every Indic word. We ALSO include ZWNJ (U+200C) and ZWJ (U+200D):
#    these Unicode format chars sit INSIDE Indic words to control consonant
#    joining, so they must stay attached, not fall into the punctuation bucket.
#    Numbers/punctuation are their own runs; a leading ' ?' keeps the space on
#    the word. The JS widget uses the identical pattern (/u flag) so counts match.
PAT = regex.compile(r" ?[\p{L}\p{M}\u200c\u200d]+| ?\p{N}+| ?[^\s\p{L}\p{M}\p{N}\u200c\u200d]+|\s+(?!\S)|\s+")

def pretokenize(text):
    return PAT.findall(text)

# Cleaning = collapse every run of whitespace (newlines, paragraph breaks, double
# spaces from the wiki layout) into a single space. This throws away *layout*, not
# words — every token of content survives. The widget applies the identical rule
# (JS: text.replace(/\s+/g,' ').trim()) so numbers reproduce exactly.
def clean(text):
    text = unicodedata.normalize("NFC", text)   # canonical form: one encoding per character
    return regex.sub(r"\s+", " ", text).strip()

def word_to_byte_chars(word):
    """A word-chunk -> tuple of byte-chars (one per UTF-8 byte)."""
    return tuple(BYTE_ENCODER[b] for b in word.encode("utf-8"))


# ---------------------------------------------------------------------------
# 3) TRAIN — the greedy merge loop, with incremental pair-count updates so it's
#    fast enough to learn ~10k merges in pure Python.
# ---------------------------------------------------------------------------
def train(weighted_corpora, vocab_size=10000, verbose=True):
    """
    weighted_corpora: list of (text, weight). `weight` scales how much that text's
    pair-counts matter, which is how we hand more of the shared budget to the
    harder (Indic) scripts. weight is a float multiplier on word frequencies.

    Returns (merges, vocab):
      merges : list of (tokenA_str, tokenB_str) in learned order
      vocab  : list of token strings (index == token id); first 256 are byte-chars
    """
    # --- initial vocab: all 256 byte-chars (this is the no-UNK guarantee) ---
    vocab = [BYTE_ENCODER[b] for b in range(256)]
    tok2id = {t: i for i, t in enumerate(vocab)}

    # --- dedupe corpus into unique word-chunks with (weighted) frequencies ---
    # weights are INTEGERS so pair counts stay exact ints (the heap below relies
    # on exact equality to discard stale entries).
    freqs = collections.Counter()
    for text, weight in weighted_corpora:
        weight = int(round(weight))
        for w, c in collections.Counter(pretokenize(text)).items():
            freqs[w] += c * weight

    # represent each unique word as a list of token-ids; carry its frequency
    words = []          # words[i] = list of token ids
    wfreq = []          # wfreq[i] = weighted frequency
    for w, f in freqs.items():
        ids = [tok2id[ch] for ch in word_to_byte_chars(w)]
        if ids:
            words.append(ids); wfreq.append(f)

    # pair_counts[(a,b)] = total weighted freq of adjacent ids a,b
    # pair_words[(a,b)]  = set of word indices where that pair currently occurs
    # heap = lazy max-heap of (-count,a,b); we validate each pop against
    # pair_counts, so stale entries (from later up/down-dates) are just skipped.
    pair_counts = {}
    pair_words = collections.defaultdict(set)
    heap = []
    for i in range(len(words)):
        ids, f = words[i], wfreq[i]
        for a, b in zip(ids, ids[1:]):
            pair_counts[(a, b)] = pair_counts.get((a, b), 0) + f
            pair_words[(a, b)].add(i)
    for (a, b), c in pair_counts.items():
        heap.append((-c, a, b))
    heapq.heapify(heap)

    merges = []
    n_merges = vocab_size - len(vocab)
    for step in range(n_merges):
        # --- pop the most frequent still-valid pair off the lazy heap ---
        best = None
        while heap:
            negc, a, b = heapq.heappop(heap)
            if pair_counts.get((a, b), 0) == -negc:   # entry is current, not stale
                best = (a, b); break
        if best is None:
            break
        a, b = best
        new_id = len(vocab)
        new_tok = vocab[a] + vocab[b]
        vocab.append(new_tok)
        tok2id[new_tok] = new_id
        merges.append((vocab[a], vocab[b]))

        # --- apply this merge only in the words that contain the pair ---
        affected = list(pair_words[best])
        for i in affected:
            ids = words[i]; f = wfreq[i]
            # remove this word's OLD pair contributions
            for x, y in zip(ids, ids[1:]):
                c = pair_counts.get((x, y), 0) - f
                if c <= 0:
                    pair_counts.pop((x, y), None)
                    pair_words.pop((x, y), None)
                else:
                    pair_counts[(x, y)] = c
                    pair_words[(x, y)].discard(i)
                    heapq.heappush(heap, (-c, x, y))   # push new (lower) value
            # rebuild the word with a,b -> new_id
            merged = []
            j = 0
            while j < len(ids):
                if j < len(ids) - 1 and ids[j] == a and ids[j + 1] == b:
                    merged.append(new_id); j += 2
                else:
                    merged.append(ids[j]); j += 1
            words[i] = merged
            # add its NEW pair contributions (involving the just-created id)
            for x, y in zip(merged, merged[1:]):
                c = pair_counts.get((x, y), 0) + f
                pair_counts[(x, y)] = c
                pair_words[(x, y)].add(i)
                heapq.heappush(heap, (-c, x, y))
        pair_counts.pop(best, None)
        pair_words.pop(best, None)

        if verbose and (step + 1) % 1000 == 0:
            print(f"  merge {step+1:>5}/{n_merges}  '{new_tok}'  (freq {int(pair_counts.get(best,0))})")

    return merges, vocab


# ---------------------------------------------------------------------------
# 4) ENCODE (inference) — apply merges greedily by learned rank, GPT-2 style.
# ---------------------------------------------------------------------------
def build_ranks(merges):
    return {(a, b): i for i, (a, b) in enumerate(merges)}

def bpe_word(byte_chars, ranks, cache):
    """Merge one word's byte-chars using the learned merge ranks."""
    if byte_chars in cache:
        return cache[byte_chars]
    word = list(byte_chars)
    while len(word) >= 2:
        # find the adjacent pair with the smallest (=earliest-learned) rank
        best, best_rank = None, None
        for a, b in zip(word, word[1:]):
            r = ranks.get((a, b))
            if r is not None and (best_rank is None or r < best_rank):
                best, best_rank = (a, b), r
        if best is None:
            break
        a, b = best
        merged, i = [], 0
        while i < len(word):
            if i < len(word) - 1 and word[i] == a and word[i + 1] == b:
                merged.append(a + b); i += 2
            else:
                merged.append(word[i]); i += 1
        word = merged
    cache[byte_chars] = word
    return word

def encode(text, ranks, cache=None):
    """Return the list of token strings for `text`."""
    if cache is None:
        cache = {}
    out = []
    for chunk in pretokenize(text):
        out.extend(bpe_word(word_to_byte_chars(chunk), ranks, cache))
    return out


# ---------------------------------------------------------------------------
# 5) Fertility = tokens / words (words via \w+, the metric the cohort cited).
# ---------------------------------------------------------------------------
# A "word" = a maximal run of letters+marks+numbers. This is the honest,
# language-neutral count (भारत = 1 word, not 2). We deliberately do NOT use naive
# \w+, which splits Indic words on their matras and would inflate the denominator
# — the instructor warned against gaming the word count. Same rule in the widget.
WORD_PAT = regex.compile(r"[\p{L}\p{M}\p{N}\u200c\u200d]+")
def word_count(text):
    return len(WORD_PAT.findall(text))

def fertility(text, ranks, cache=None):
    toks = len(encode(text, ranks, cache))
    words = word_count(text)
    return toks / words, toks, words


if __name__ == "__main__":
    # tiny self-test: prove the loop learns obvious merges and encode is stable
    txt = "the theme of the theatre is the theory of the there there"
    merges, vocab = train([(txt, 1.0)], vocab_size=256 + 12, verbose=False)
    ranks = build_ranks(merges)
    print("vocab size:", len(vocab))
    print("first merges:", ["".join(m) for m in merges[:6]])
    print("encode('the theory'):", encode("the theory", ranks))
