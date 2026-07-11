# S2 — TokenSangam · a multilingual BPE tokenizer: two attempts, one budget

> **TokenSangam** — *sangam* (संगम) = confluence. A tokenizer literally built from 9,744 merges,
> flowing four languages (en/hi/te/kn) into one 10k vocabulary.

The deliverable is [`assignment/s2-bpe-tokenizer.html`](../../assignment/s2-bpe-tokenizer.html) — a
story-first, fully live dashboard holding **both** tokenizers — plus the staged submission
[`assignment/tokenizer_v3.json`](../../assignment/tokenizer_v3.json) (the currently-submitted
`tokenizer.json` is the word-scope attempt; swap on instructor's OK for multi-word tokens).
This folder is the reproducible pipeline. Score = `1000 / (max − min fertility)`, fertility =
tokens ÷ words, **strict akshara-aware counting at a hard 10k vocab**.

## Attempt 1 — word-scope feedback BPE (the measured wall)

Merges never cross word edges (GPT-2 style); each merge goes to the language currently worst
against its gate; English freezes at 1.19 (it is the score's minimum — improving it widens the gap).
Result at V=10,000: en 1.1899 ✓ but hi/te/kn 2.058 — and the **price list** (`pricelist.py`) proves no
allocation could fix it: en@1.19 costs 6,364 targeted merges, en@1.19 + all@1.8 totals **11,019 > 9,744
available**. Splits (40/20/20/20) and multi-run token harvesting only re-slice this too-small pie —
an imported token must bring its whole merge chain, which is exactly the cost already counted.

## Final — sentence-scope feedback BPE ("phrase tokens")

One rule change (`feedback3.py`): pretokenize at sentence enders (। ॥ . ! ?) only, so merges may cross
spaces — one token can be `" of the"` or `" के लिए"` (SentencePiece `split_by_whitespace=false` precedent).
English's bill drops to 4,390 merges and the savings carry everyone under their gates:

| V=10,000 strict | en | hi | te | kn | score |
|---|---|---|---|---|---|
| Attempt 1 | 1.1899 ✓ | 2.0582 ✗ | 2.0589 ✗ | 2.0586 ✗ | 1,151 |
| **Final** | **1.1897 ✓** | **1.7305 ✓** | **1.7305 ✓** | **1.7306 ✓** | **1,849** (naive 1,657) |

Extended past the budget the trio converges and parks at 1.25 by V=13,323 (projection peak 16,455) —
shown in the dashboard as the faded "beyond 10k" curves. Prefix determinism is asserted: the extended
run's first 9,744 merges are byte-identical to the submitted tokenizer.

## The dashboard

Animated BPE flowchart with the attempt-1 vs final fork · auto-cycling merge demo on one sentence ·
dual score tiles + gates · live truncation slider (prefix property — cut list == tokenizer trained to V) ·
merge-allocation strip · score & fertility charts with beyond-budget projections · dual playground ·
**paste-any-Wikipedia-URL scorer** (the unseen-text honesty check: fresh Telugu page scores 1.813 final
vs 2.112 attempt-1) · reflections cards. Everything NFC-normalized, akshara-aware, ZWJ/ZWNJ-preserving,
zero-UNK byte-level; both word-count conventions displayed.

## Reproduce end-to-end

```bash
pip install regex                 # only non-stdlib dep (Unicode \p{L}\p{M})
python fetch.py                   # India page (en/hi/te/kn) -> data/*.txt
python feedback.py                # attempt 1: word-scope run -> train20k.json
python export2.py                 # verifies + exports attempt 1 -> tokenizer_data.json
python pricelist.py               # the infeasibility proof (11,019 > 9,744)
python feedback3.py               # (module) sentence-scope trainer
python run_v3b.py                 # frontier check (clause scope)
python export3.py                 # verifies + stages assignment/tokenizer_v3.json
#   extended v3 run: see the inline script in git history / tracker (freeze indic 1.25, vocab 16000)
python export4.py                 # fuses both runs, proves prefix determinism -> widget_data_v4.json
python build_widget.py            # -> assignment/s2-bpe-tokenizer.html
node verify_live4.js              # headless: both JS encoders == curves == Python, gates, downloads, wiki fetch
```

## Files

- **`bpe.py`** — from-scratch core (byte map, pretokenize, clean, heap trainer, encode, word counts).
- **`feedback.py` / `feedback3.py`** — score-aware trainers (word-scope / sentence-scope); both record
  per-merge per-language token deltas = the widget's instant, exact curves.
- **`pricelist.py`** — merges-per-target accounting; **`analyze_run.py`** — landmark analysis.
- **`export2/3/4.py`** — verification + exports (every export re-proves curve == real encoder).
- **`widget_template.html`** / **`build_widget.py`** / **`verify_live4.js`** — the dashboard and its checks.
