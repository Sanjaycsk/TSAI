#!/usr/bin/env python3
"""
Train + evaluate the shared 10k tokenizer for en/hi/te/kn on the faithful
Markdown corpus. Pipeline is IDENTICAL to the reference solution:

    BPE(unk_token=[UNK]) + NFKC normalizer
    + Metaspace(replacement=U+2581, prepend_scheme=never) pretok & decoder
    BpeTrainer(vocab_size=10000, min_frequency=1)

Only two things differ from the reference: the fourth language (kn, not mai)
and the training weights, which exist to balance fertility across languages —
a language's weight duplicates its corpus file in the training list, giving
its byte-pair statistics more votes in the merge election.

Usage:
    python train_eval.py                 # train with WEIGHTS below, save + report
    python train_eval.py sweep           # hill-climb integer weights to minimize spread
"""
from __future__ import annotations

import json
import math
import sys
import tempfile
from pathlib import Path

import regex
from tokenizers import Tokenizer
from tokenizers.decoders import Metaspace as MetaspaceDecoder
from tokenizers.models import BPE
from tokenizers.normalizers import NFKC
from tokenizers.pre_tokenizers import Metaspace
from tokenizers.trainers import BpeTrainer

HERE = Path(__file__).resolve().parent
CORPUS = HERE / "corpus"
OUT_TOKENIZER = HERE / "tokenizer.json"
OUT_METRICS = HERE / "metrics.json"

LANGS = ["en", "hi", "te", "kn"]
WEIGHTS = {"en": 3, "hi": 4, "te": 4, "kn": 2}  # starting point = reference's shape
FAITHFUL_UNIT_RE = regex.compile(r"[\p{L}\p{M}\p{N}]+|[^\s\p{L}\p{M}\p{N}]")

TEXTS = {c: (CORPUS / f"{c}.faithful.txt").read_text(encoding="utf-8") for c in LANGS}
UNITS = {c: len(FAITHFUL_UNIT_RE.findall(t)) for c, t in TEXTS.items()}


def make_tokenizer() -> Tokenizer:
    tokenizer = Tokenizer(BPE(unk_token="[UNK]"))
    tokenizer.normalizer = NFKC()
    tokenizer.pre_tokenizer = Metaspace(replacement="▁", prepend_scheme="never")
    tokenizer.decoder = MetaspaceDecoder(replacement="▁", prepend_scheme="never")
    return tokenizer


def train(weights: dict) -> Tokenizer:
    with tempfile.TemporaryDirectory() as tmp:
        files: list[str] = []
        tmpdir = Path(tmp)
        for code, text in TEXTS.items():
            path = tmpdir / f"{code}.txt"
            path.write_text(text, encoding="utf-8")
            files.extend([str(path)] * weights[code])
        tokenizer = make_tokenizer()
        trainer = BpeTrainer(vocab_size=10000, min_frequency=1, special_tokens=["[UNK]"])
        tokenizer.train(files, trainer)
    return tokenizer


def evaluate(tokenizer: Tokenizer, weights: dict) -> dict:
    token_counts = {c: len(tokenizer.encode(t).ids) for c, t in TEXTS.items()}
    ratios = {c: token_counts[c] / UNITS[c] for c in LANGS}
    spread = max(ratios.values()) - min(ratios.values())
    score = 1000 / spread
    hindi_penalty = math.exp(max(0.0, ratios["hi"] / 1.2 - 1.0))
    return {
        "variant": "wiki_faithful_markdown",
        "languages": {"en": "English", "hi": "Hindi", "te": "Telugu", "kn": "Kannada"},
        "weights": weights,
        "vocab_size": tokenizer.get_vocab_size(),
        "faithful_units": UNITS,
        "unit_policy": "Counts each contiguous Unicode letter/mark/number run as one unit and each visible non-space punctuation/symbol character as one unit.",
        "token_counts": token_counts,
        "ratios": ratios,
        "spread": spread,
        "score": score,
        "hindi_exp1_penalty_factor": hindi_penalty,
        "hindi_exp1_adjusted_score": score / hindi_penalty,
    }


def run(weights: dict) -> dict:
    m = evaluate(train(weights), weights)
    r = m["ratios"]
    print(f"w={weights}  " + "  ".join(f"{c}={r[c]:.4f}" for c in LANGS)
          + f"  spread={m['spread']:.5f}  score={m['score']:.0f}")
    return m


def sweep() -> None:
    # Hill-climb over integer weights 1..8: try +/-1 on each language, keep any
    # move that shrinks the spread. Each train is seconds, so this is cheap.
    best_w = dict(WEIGHTS)
    best = run(best_w)
    seen = {tuple(sorted(best_w.items())): best}
    improved = True
    while improved:
        improved = False
        for code in LANGS:
            for delta in (+1, -1):
                w = dict(best_w)
                w[code] = w[code] + delta
                if not (1 <= w[code] <= 8):
                    continue
                key = tuple(sorted(w.items()))
                m = seen.get(key) or run(w)
                seen[key] = m
                if m["spread"] < best["spread"]:
                    best, best_w, improved = m, w, True
        # restart the +/-1 scan from the new best until no neighbor improves
    print("\nBEST:", json.dumps({"weights": best_w, "ratios": best["ratios"],
                                  "spread": best["spread"], "score": best["score"]},
                                 ensure_ascii=False, indent=2))
    save(best_w, best)


def save(weights: dict, metrics: dict) -> None:
    tokenizer = train(weights)  # retrain at the chosen weights for the saved file
    tokenizer.save(str(OUT_TOKENIZER))
    OUT_METRICS.write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"saved {OUT_TOKENIZER.name} + {OUT_METRICS.name}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "sweep":
        sweep()
    else:
        m = run(WEIGHTS)
        save(WEIGHTS, m)
        print(json.dumps(m, ensure_ascii=False, indent=2))
