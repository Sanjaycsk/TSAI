import re, os, collections
import bpe

DATA = os.path.join(os.path.dirname(__file__), "data")
def load(l):
    with open(os.path.join(DATA, f"india_{l}.txt"), encoding="utf-8") as f:
        return f.read()

# 1) does \w match Indic letters + their matras?
for s in ["भारत", "భారతదేశం", "ಭಾರತ", "இந்தியா"]:
    print(repr(s), "-> \\w+ finds:", re.findall(r"\w+", s))

# 2) chunk breakdown per language: word-chunks vs punctuation vs whitespace
for l in ["en", "hi", "te", "kn"]:
    t = load(l)
    chunks = bpe.pretokenize(t)
    word_ch = sum(1 for c in chunks if re.fullmatch(r"\s?\w+", c))
    punct_ch = sum(1 for c in chunks if re.fullmatch(r"\s?[^\s\w]+", c))
    ws_ch = sum(1 for c in chunks if c.strip() == "")
    words = len(re.findall(r"\w+", t))
    # how many chunks contain Latin letters (embedded English)?
    latin = sum(1 for c in chunks if re.search(r"[A-Za-z]", c))
    digit = sum(1 for c in chunks if re.search(r"[0-9]", c))
    print(f"\n{l}: {len(chunks):,} chunks | word {word_ch:,} punct {punct_ch:,} "
          f"ws {ws_ch:,} | \\w+ words {words:,} | latin-chunks {latin:,} digit {digit:,}")
    # top punctuation chunks
    pc = collections.Counter(c for c in chunks if re.fullmatch(r"\s?[^\s\w]+", c))
    print("   top punct chunks:", [(repr(c), n) for c, n in pc.most_common(6)])
