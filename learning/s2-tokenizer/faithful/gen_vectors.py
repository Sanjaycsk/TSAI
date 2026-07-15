#!/usr/bin/env python3
"""
Generate parity test vectors for the browser (JS) encoder.

The dashboard runs a hand-written JS mirror of the HF pipeline
(NFKC -> Metaspace -> BPE). A mirror is only trustworthy if it is PROVEN
equal to the Python tokenizer, so this script encodes a battery of texts —
including nasty edge cases (double spaces, newlines, leading space, unknown
emoji, the grader's URL) and real corpus slices — and saves the expected ids.
The page replays them on load and shows a parity badge.
"""
from __future__ import annotations

import json
from pathlib import Path

from tokenizers import Tokenizer

HERE = Path(__file__).resolve().parent
tok = Tokenizer.from_file(str(HERE / "tokenizer.json"))

samples = [
    "https://hi.wikipedia.org/wiki/भारत#cite_ref-1",   # the sample that scored us 0
    "India's population is 1,428,627,663.",             # the reference's demo sentence
    "The Republic of India is in Asia.",
    "भारत गणराज्य एशिया में है।",
    "భారతదేశం ఆసియాలో ఉంది.",
    "ಭಾರತ ಏಷ್ಯಾದಲ್ಲಿದೆ.",
    "double  space and\nnewline\ttab",                  # whitespace edge cases
    " leading space",
    "trailing space ",
    "[link](https://en.wikipedia.org/wiki/India) **bold** `code`",  # markdown symbols
    "28°36′50″N 77°12′30″E",                            # NFKC-affected chars (″ -> ′′)
    "emoji 🐘 not in vocab",                             # must become [UNK], not vanish
]
# real corpus slices so parity is tested on the actual graded material
for code in ["en", "hi", "te", "kn"]:
    text = (HERE / "corpus" / f"{code}.faithful.txt").read_text(encoding="utf-8")
    samples.append(text[5000:5400])

out = []
for s in samples:
    enc = tok.encode(s)
    out.append({
        "text": s,
        "ids": enc.ids,
        "tokens": enc.tokens,
        "decoded": tok.decode(enc.ids),
    })

(HERE / "vectors.json").write_text(
    json.dumps({"samples": out}, ensure_ascii=False), encoding="utf-8"
)
print(f"wrote vectors.json with {len(out)} samples, "
      f"{sum(len(s['ids']) for s in out)} total tokens")
