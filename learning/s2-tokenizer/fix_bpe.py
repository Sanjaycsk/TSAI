# One-shot fixer: rewrite PAT and WORD_PAT with VISIBLE ‌ / ‍ escapes
# (ZWNJ / ZWJ) so no invisible characters live in the source.
GOOD_PAT = 'PAT = regex.compile(r" ?[\\p{L}\\p{M}\\u200c\\u200d]+| ?\\p{N}+| ?[^\\s\\p{L}\\p{M}\\p{N}\\u200c\\u200d]+|\\s+(?!\\S)|\\s+")'
GOOD_WORD = 'WORD_PAT = regex.compile(r"[\\p{L}\\p{M}\\p{N}\\u200c\\u200d]+")'

p = "bpe.py"
out = []
for line in open(p, encoding="utf-8").read().split("\n"):
    line = "".join("\\u200c" if ord(c) == 0x200c else "\\u200d" if ord(c) == 0x200d else c for c in line)
    if line.startswith("PAT = "):
        line = GOOD_PAT
    elif line.startswith("WORD_PAT = "):
        line = GOOD_WORD
    out.append(line)
open(p, "w", encoding="utf-8").write("\n".join(out))

import importlib, bpe; importlib.reload(bpe)
zwnj = chr(0x200c); zwj = chr(0x200d)
telugu = "ప్రదేశ్" + zwnj   # ప్రదేశ్ + ZWNJ
resid = sum(1 for c in open(p, encoding="utf-8").read() if ord(c) in (0x200c, 0x200d))
print("invisible chars in source:", resid)
print("ZWNJ word -> n chunks:", len(bpe.pretokenize(telugu)), "| word_count:", bpe.word_count(telugu))
print("PAT snippet:", bpe.PAT.pattern[:38])
